#!/usr/bin/env python3
"""Fetch OpenAPI spec from api.tapkit.ai and save it locally."""

import json
import urllib.request

def fetch_openapi():
    url = "https://api.tapkit.ai/openapi.json"
    print(f"Fetching OpenAPI spec from {url}...")
    
    with urllib.request.urlopen(url) as response:
        spec = json.loads(response.read())
    
    output_path = "openapi.json"
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)
    
    print(f"✓ Saved OpenAPI spec to {output_path}")
    print(f"  Endpoints: {len(spec.get('paths', {}))}")

if __name__ == "__main__":
    fetch_openapi()
