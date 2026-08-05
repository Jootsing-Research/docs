# TapKit Docs

Source for the TapKit documentation site at [docs.tapkit.ai](https://docs.tapkit.ai).

## Local development

```
npm i -g mint
mint dev
```

Preview at `http://localhost:3000`.

## Structure

| Tab | Path | What's there |
|-----|------|--------------|
| Documentation | `setup/`, `use-cases/` | Getting started, setup guides, use cases |
| Integrations | `integrations/` | Claude, Codex, MCP, skills |
| API Reference | `api-reference/` | REST endpoints for devices, gestures, actions |
| SDK | `sdk/` | Python SDK reference |

## Deploying

Pushes to `main` deploy automatically via Mintlify.
