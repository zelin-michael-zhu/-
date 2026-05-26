# ApplyPilot MVP Implementation Plan

This file is the working roadmap for turning the current runnable MVP skeleton into a usable local product. The goal is to move step by step, keep every phase shippable, and avoid pretending mock features are complete.

## Current State

The project can run locally with:

- Next.js frontend at `/en` and `/zh`
- FastAPI backend
- MySQL through Docker Compose on host port `3307`
- Alembic initial schema
- Demo seed data for universities, applicant, programs, documents, applications, emails, and matches

Known limitations:

- Chinese UI still contains many English strings.
- Some English text comes from seed data and mock data, not just UI labels.
- Many buttons are visual only and do not yet call APIs.
- Most pages do not show loading, success, error, or JSON/API response feedback.
- Browser Agent, crawler, email tracker, AI writing, and interview prep are mostly mock flows.
- Program matching exists as a backend rule engine, but the frontend matches page is not yet fully connected to the API.
- The product needs clearer separation between real data, translated display labels, mock data, and future AI-generated content.

## Phase 0: Stabilize Local Runtime

Status: completed in current local environment

Tasks:

- Add missing root `frontend/app/layout.tsx` with `<html>` and `<body>` tags.
- Keep locale layout focused on locale-scoped rendering only.
- Confirm `/en`, `/zh`, `/en/dashboard`, `/zh/dashboard`, `/en/programs`, `/zh/programs` load without runtime overlays.
- Confirm FastAPI stays available at `http://127.0.0.1:8000/docs`.
- Confirm MySQL container health and `DATABASE_URL` using `localhost:3307`.
- Add a short troubleshooting section for port `3306` conflicts.

Acceptance criteria:

- No Next.js missing root layout error.
- Frontend and backend can be restarted from README commands.
- API health and programs API return expected data.

## Phase 1: Complete Chinese Localization

Status: started

Problem:

The Chinese UI is currently mixed with English. Some of that is acceptable for official program names, but action labels, status labels, helper text, section titles, filters, warnings, and mock content should switch language.

Tasks:

- Move all visible UI strings into dictionaries.
- Add dictionaries for:
  - navigation
  - dashboard
  - program database
  - program detail
  - profile
  - matches
  - documents
  - applications
  - browser agent
  - crawler
  - email tracker
  - interview prep
  - settings
  - common statuses and actions
- Translate status values for display:
  - `auto_extracted` -> `自动抽取`
  - `needs_review` -> `待审核`
  - `reviewed` -> `已审核`
  - `rejected` -> `已拒绝`
  - `Not Started` -> `未开始`
  - `In Progress` -> `进行中`
  - `Submitted` -> `已提交`
  - `Interview` -> `面试`
  - `Offer` -> `录取`
  - `Rejected` -> `拒信`
- Translate field and country display values where useful:
  - `Hong Kong` -> `中国香港`
  - `Singapore` -> `新加坡`
  - `United Kingdom` -> `英国`
  - `Business Analytics` -> `商业分析`
  - `Finance` -> `金融`
  - `Management` -> `管理学`
  - `Marketing` -> `市场营销`
- Keep official university and program names in English, but add optional Chinese display aliases later.
- Add `display.ts` helpers so raw backend values stay stable while UI display is localized.
- Update seed/mock email subjects with bilingual display variants or translate on render.

Acceptance criteria:

- `/zh` pages no longer show English UI labels except official names, degree abbreviations, URLs, and intentional product terms.
- `/en` pages remain natural English.
- No duplicated translation logic inside components.

Progress:

- Added `frontend/lib/display.ts` for localized display of backend enum-like values.
- Localized core labels in program cards, program details, dashboard pipeline, documents, email tracker, settings, crawler, matches, and browser agent.
- Official school and program names still remain English by design.
- Remaining work: move every remaining visible string into dictionaries and add optional Chinese aliases for demo data.

## Phase 2: Make Frontend Actions Real

Status: started

Problem:

Several controls look clickable but do not call APIs or show results.

Tasks:

- Create a reusable API action pattern:
  - loading state
  - success toast or inline result
  - error state
  - optional raw JSON preview
- Add a small `ActionResult` component for API responses.
- Add client-side action wrappers for:
  - crawler seed
  - crawler discover
  - crawler fetch
  - crawler extract
  - crawler full pipeline
  - match generation
  - document status update
  - application status update
  - browser task start
  - browser task approve
  - browser task stop
  - email analyze
  - AI background analysis
  - SOP outline generation
  - interview prep generation
- Use disabled states during requests.
- Show last API response in a collapsible JSON panel for MVP debugging.

Acceptance criteria:

- Every visible button either performs an action or is visibly disabled with a reason.
- Crawler buttons show API response JSON.
- Browser Agent buttons update logs/status.
- Matches page can generate and refresh real backend matches.

Progress:

- Added reusable `ActionResult` JSON feedback panel.
- Crawler control buttons now call local FastAPI endpoints and show JSON or error output.
- Matches page can call match generation and display the returned JSON payload.
- Browser Agent start, approve, and stop buttons call local FastAPI endpoints and show JSON output.
- Remaining work: wire Documents, Applications, Profile save, Email analyze, AI actions, and field-level validation.

## Phase 3: Connect Pages To Backend Data

Tasks:

- Dashboard:
  - fetch applicant
  - fetch programs
  - fetch applications
  - fetch documents
  - fetch emails
  - show computed stats
- Programs:
  - wire filters to query params
  - support search, country, field, review status, min confidence
  - add empty and error states
- Program detail:
  - add review status update buttons
  - show requirements, deadlines, and documents from backend tables
  - show source URL and confidence clearly
- Profile:
  - load default applicant
  - save profile edits
  - call applicant analysis endpoint
  - show GPA conversion result
- Matches:
  - call generate endpoint
  - show real match categories, reasons, and risks
  - add to applications
- Documents:
  - load real documents
  - update status
  - generate checklist by program
- Applications:
  - load applications
  - update status
  - create application from match/program
- Email tracker:
  - load mock backend emails
  - run mock analyze
- Settings:
  - persist local settings in database or local storage for MVP.

Acceptance criteria:

- Refreshing the page preserves data saved through API calls.
- Main workflows are usable without editing the database manually.

## Phase 4: Improve Backend Data Model And API Quality

Tasks:

- Replace loose `dict` request bodies with Pydantic schemas.
- Add response models for all endpoints.
- Add pagination metadata.
- Add consistent error format.
- Add `updated_at` handling where missing.
- Add MySQL-safe indexes and constraints.
- Add `display_name_zh` or translation tables for user-facing reference data if needed.
- Add tests for:
  - GPA conversion
  - matching score
  - program filters
  - seed idempotency
  - crawler robots decision
  - Browser Agent mock logs

Acceptance criteria:

- API docs are clear in Swagger.
- Seed scripts are idempotent.
- Core backend logic has tests.

## Phase 5: Browser Agent MVP Upgrade

Tasks:

- Make browser task lifecycle stateful:
  - `created`
  - `waiting_approval`
  - `running`
  - `saved_draft`
  - `stopped`
  - `failed`
- Persist logs as JSON.
- Add screenshot path to task output.
- Add endpoint to run the local Playwright sample form demo.
- Display screenshot in frontend.
- Add field-level approval:
  - approve all
  - edit value
  - skip field
- Keep final submit and payment disabled.
- Add visible audit log.

Acceptance criteria:

- User can start task, approve filling, run local demo, see logs, and see screenshot.
- Final submit remains disabled and clearly explained.

## Phase 5A: OpenCLI Optional Tool Layer

Status: started

Purpose:

OpenCLI can be useful as an optional bridge that turns websites or tools into CLI-like commands. In ApplyPilot, it should not become an uncontrolled real-school automation engine. It should be treated as a read-only, allowlisted, auditable tool layer.

Safety rules:

- OpenCLI is optional; ApplyPilot must work when it is not installed.
- Only read-only allowlisted commands are enabled in the MVP.
- Browser operation commands are blocked by default.
- Login, auth, submit, payment, CAPTCHA bypass, Cloudflare/risk-control bypass, and application submission commands are blocked.
- Any future browser operation must go through ApplyPilot human approval and audit logs.

Implemented:

- Backend status endpoint: `GET /api/browser-agent/opencli/status`
- Browser Agent executor endpoint: `GET /api/browser-agent/executors`
- Browser Agent task endpoints for start, next step, approve, stop, and logs.
- `RiskGuard` blocks or gates high-risk browser actions.
- Browser Agent page includes an executor selector for Mock, Playwright, and OpenCLI with JSON feedback.
- OpenCLI is treated as an external CLI. Its source is not vendored into ApplyPilot.

Next:

- Install OpenCLI globally and verify `opencli doctor` through ApplyPilot.
- Add persistent OpenCLI run logs to MySQL.
- Add user-configurable allowlist in Settings.
- Add read-only website research command templates for public program pages.
- Add crawler pipeline option to ingest OpenCLI JSON output into `raw_pages` and `extraction_runs`.
- Add tests for command allow/block decisions.

## Phase 6: Crawler Pipeline MVP Upgrade

Tasks:

- Add real dry-run discovery output.
- Save crawler runs and per-source statuses.
- Implement robots check per URL.
- Add rate limiting and domain page cap enforcement.
- Add raw page storage from allowed public pages.
- Add extraction run records.
- Add review queue UI for auto-extracted programs.
- Add manual review action for `reviewed` and `rejected`.
- Add crawler safety copy in both languages.

Acceptance criteria:

- Crawler dry run shows what would be fetched.
- Real fetch respects robots.txt and rate limits.
- Extracted data always includes source URL, confidence, and review status.

## Phase 7: Product Polish

Tasks:

- Add toast notifications.
- Add skeleton loading states.
- Add consistent empty states.
- Add responsive mobile layout checks.
- Reduce overly generic SaaS text.
- Improve visual hierarchy on dense pages.
- Add chart for application pipeline and portfolio balance.
- Add accessibility labels for icon buttons.
- Add keyboard-friendly form controls.

Acceptance criteria:

- Product feels like a coherent SaaS dashboard rather than a static demo.
- UI text does not overflow or overlap.
- Common workflows feel clear and repeatable.

## Phase 8: AI Feature Layer

Tasks:

- Keep mock AI as default.
- Add provider switch:
  - mock
  - OpenAI
  - Claude
  - DeepSeek
- Add prompt templates for:
  - background analysis
  - SOP outline
  - program-specific SOP tailoring
  - interview prep
  - email summary
  - match explanation
- Add user approval for any AI-generated application content.
- Store generated drafts and revisions.

Acceptance criteria:

- MVP works without API keys.
- With API keys, AI features can be enabled explicitly.
- Generated content is never submitted automatically.

## Suggested Next Step

Start with Phase 1 and Phase 2 together:

1. Fix all visible Chinese localization gaps.
2. Add real click handlers and JSON feedback for Crawler, Matches, Browser Agent, Documents, and Applications.
3. Then connect Profile and Dashboard more deeply to backend data.

This gives the fastest jump from “looks like a product” to “behaves like a product”.
