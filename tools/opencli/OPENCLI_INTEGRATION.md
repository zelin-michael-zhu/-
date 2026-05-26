# OpenCLI Integration

## Role In ApplyPilot

OpenCLI is an optional browser executor for ApplyPilot. ApplyPilot remains the main product and backend. OpenCLI is called through `backend/app/services/browser_agent/opencli_executor.py` via `subprocess.run(..., shell=False)`.

## Why Not Copy OpenCLI Into Backend

OpenCLI is a separate tool with its own release cycle. Keeping it outside `backend/app` preserves clear boundaries and lets ApplyPilot switch between Mock, Playwright, OpenCLI, Browser-use, Stagehand, or other executors later.

## Install

```bash
npm install -g @jackwener/opencli
```

Then install the Browser Bridge extension required by OpenCLI, following OpenCLI's own documentation.

## Health Check

```bash
opencli doctor
```

ApplyPilot also exposes:

```text
GET /api/browser-agent/opencli/status
```

## Manual Smoke Test

```bash
opencli browser applypilot open https://example.com
opencli browser applypilot state
```

## How ApplyPilot Calls OpenCLI

The command builder creates list-form commands such as:

```python
["opencli", "browser", "applypilot", "open", "https://example.com"]
```

The executor runs those commands with `shell=False`, after `RiskGuard` classifies the action.

## Safety Boundaries

- No automatic final submit.
- No automatic payment.
- No CAPTCHA bypass.
- No password storage.
- No school portal login automation in MVP.
- High-risk actions require explicit user approval or are blocked.
