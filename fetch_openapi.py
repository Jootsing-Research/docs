#!/usr/bin/env python3
"""Fetch and sanitize the public TapKit OpenAPI documentation."""

import json
import urllib.request
from pathlib import Path


PUBLIC_INFO = {
    "title": "TapKit API",
    "description": (
        "REST API for controlling connected iPhones programmatically with TapKit."
    ),
    "version": "1.0.0",
}

PUBLIC_SERVERS = [
    {
        "url": "https://api.tapkit.ai/v1",
        "description": "Production",
    }
]

PUBLIC_SECURITY_SCHEMES = {
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API key starting with joot_ prefix",
    }
}


# The upstream schema includes internal and legacy routes. Only routes explicitly
# approved for the public documentation are allowed through this list.
PUBLIC_PATHS = {
    "/health",
    "/jobs/{job_id}",
    "/phones",
    "/phones/{phone_id}/action-button",
    "/phones/{phone_id}/agent",
    "/phones/{phone_id}/agent/execute",
    "/phones/{phone_id}/agent/{task_id}",
    "/phones/{phone_id}/agent/{task_id}/resume",
    "/phones/{phone_id}/agent/{task_id}/stop",
    "/phones/{phone_id}/app-switcher",
    "/phones/{phone_id}/apps",
    "/phones/{phone_id}/control-center",
    "/phones/{phone_id}/double-tap",
    "/phones/{phone_id}/double-tap/select",
    "/phones/{phone_id}/drag",
    "/phones/{phone_id}/drag/select",
    "/phones/{phone_id}/escape",
    "/phones/{phone_id}/flick",
    "/phones/{phone_id}/flick/select",
    "/phones/{phone_id}/hold-and-drag",
    "/phones/{phone_id}/home",
    "/phones/{phone_id}/info",
    "/phones/{phone_id}/lock",
    "/phones/{phone_id}/open-app",
    "/phones/{phone_id}/pinch",
    "/phones/{phone_id}/pinch/select",
    "/phones/{phone_id}/screenshot",
    "/phones/{phone_id}/settings",
    "/phones/{phone_id}/siri",
    "/phones/{phone_id}/spotlight",
    "/phones/{phone_id}/status",
    "/phones/{phone_id}/stream/leave",
    "/phones/{phone_id}/stream/start",
    "/phones/{phone_id}/stream/status",
    "/phones/{phone_id}/stream/stop",
    "/phones/{phone_id}/tap",
    "/phones/{phone_id}/tap-and-hold",
    "/phones/{phone_id}/tap-and-hold/select",
    "/phones/{phone_id}/tap/select",
    "/phones/{phone_id}/unlock",
    "/sessions",
    "/sessions/{session_id}",
    "/sessions/{session_id}/events",
    "/sessions/{session_id}/interrupt",
    "/sessions/{session_id}/message",
    "/sessions/{session_id}/pause",
    "/sessions/{session_id}/resume",
    "/sessions/{session_id}/stop",
    "/status",
}

REMOVED_SCHEMA_TOKENS = (
    "shortcut",
    "switchcontrol",
    "copytext",
    "readclipboard",
    "openurl",
)

REMOVED_SCHEMAS = {
    "PhoneSettingsResponse",
    "SpeedSetting",
    "TypeMethod",
}

REMOVED_PROPERTIES = {
    "HomeRequest": {"method", "stop_after", "invoke_shortcut"},
    "OpenAppRequest": {"stop_after", "invoke_shortcut"},
    "PhoneInfo": {
        "unique_id",
        "lockdown_id",
        "core_media_id",
        "bluetooth_address",
        "product_type",
    },
    "PhoneResponse": {
        "shortcut_token",
        "typing_method",
        "speed",
        "unique_id",
        "lockdown_id",
        "core_media_id",
        "bluetooth_address",
        "product_type",
    },
    "PhoneSettingsUpdate": {"typing_method", "speed"},
    "PhoneStatusResponse": {"switch_control_enabled"},
    "StatusResponse": {"switch_control_enabled"},
    "TypeRequest": {"method"},
    "TypeTextRequest": {"method"},
}


def remove_schema_properties(schema, property_names):
    properties = schema.get("properties", {})
    for property_name in property_names:
        properties.pop(property_name, None)

    if "required" in schema:
        schema["required"] = [
            name for name in schema["required"] if name not in property_names
        ]


def schema_references(value):
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
            yield reference.removeprefix("#/components/schemas/")

        for nested_value in value.values():
            yield from schema_references(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from schema_references(nested_value)


def sanitize_public_spec(spec):
    spec["info"] = dict(PUBLIC_INFO)
    spec["servers"] = [dict(server) for server in PUBLIC_SERVERS]
    spec["security"] = [{"ApiKeyAuth": []}]

    components = spec.setdefault("components", {})
    components["securitySchemes"] = {
        name: dict(security_scheme)
        for name, security_scheme in PUBLIC_SECURITY_SCHEMES.items()
    }

    paths = spec.get("paths", {})
    for path in list(paths):
        if path not in PUBLIC_PATHS:
            del paths[path]
            continue

        normalized_path = path.rstrip("/")
        if normalized_path.endswith("/settings"):
            paths[path].pop("get", None)
            if "patch" in paths[path]:
                paths[path]["patch"]["description"] = (
                    "Update the display name for a phone."
                )

        if normalized_path.endswith("/open-app") and "post" in paths[path]:
            paths[path]["post"]["description"] = "Open an installed app by name."

        if normalized_path.endswith("/home") and "post" in paths[path]:
            paths[path]["post"]["description"] = "Press the Home button."
            paths[path]["post"].pop("requestBody", None)

        if not paths[path]:
            del paths[path]

    schemas = components.get("schemas", {})
    for schema_name in list(schemas):
        normalized_name = "".join(
            character for character in schema_name if character.isalnum()
        ).lower()
        if any(token in normalized_name for token in REMOVED_SCHEMA_TOKENS):
            del schemas[schema_name]

    for schema_name in REMOVED_SCHEMAS:
        schemas.pop(schema_name, None)

    for schema_name, property_names in REMOVED_PROPERTIES.items():
        schema = schemas.get(schema_name)
        if schema:
            remove_schema_properties(schema, property_names)

    settings_update = schemas.get("PhoneSettingsUpdate")
    if settings_update:
        settings_update["description"] = "Request model for updating a phone display name."

    reachable_schemas = set(schema_references(paths))
    schemas_to_visit = list(reachable_schemas)
    while schemas_to_visit:
        schema_name = schemas_to_visit.pop()
        schema = schemas.get(schema_name)
        if not schema:
            continue

        for referenced_schema in schema_references(schema):
            if referenced_schema not in reachable_schemas:
                reachable_schemas.add(referenced_schema)
                schemas_to_visit.append(referenced_schema)

    for schema_name in list(schemas):
        if schema_name not in reachable_schemas:
            del schemas[schema_name]

    serialized = json.dumps(spec).lower()
    banned_terms = (
        "switch control",
        "switch-control",
        "switch_control",
        "shortcut",
        "copy-text",
        "copy_text",
        "read-clipboard",
        "read_clipboard",
        "open-url",
        "open_url",
        "typing method",
        "typing_method",
        "shortcut_token",
        "assistive touch",
        "assistive_touch",
        "invoke_shortcut",
        "stop_after",
        "unique_id",
        "lockdown_id",
        "core_media_id",
        "bluetooth_address",
        "product_type",
    )
    leaked_terms = [term for term in banned_terms if term in serialized]
    if leaked_terms:
        raise ValueError(
            "Public OpenAPI spec still contains removed terms: "
            + ", ".join(leaked_terms)
        )

    missing_schemas = sorted(set(schema_references(spec)) - set(schemas))
    if missing_schemas:
        raise ValueError(
            "Public OpenAPI spec contains references to removed or missing schemas: "
            + ", ".join(missing_schemas)
        )

    return spec


def fetch_openapi():
    url = "https://api.tapkit.ai/openapi.json"
    print(f"Fetching OpenAPI spec from {url}...")

    with urllib.request.urlopen(url) as response:
        spec = json.loads(response.read())

    spec = sanitize_public_spec(spec)
    output_path = Path(__file__).with_name("openapi-public.json")
    with output_path.open("w") as f:
        json.dump(spec, f, indent=2)
        f.write("\n")

    print(f"✓ Saved OpenAPI spec to {output_path}")
    print(f"  Endpoints: {len(spec.get('paths', {}))}")


if __name__ == "__main__":
    fetch_openapi()
