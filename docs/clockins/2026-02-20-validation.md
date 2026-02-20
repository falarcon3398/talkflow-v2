# Clock-In — 2026-02-20 — 1001-VIDEO AVATAR (Project Setup & Validation)

## 1) Context
- **Why now:** We need a clear, repeatable way to run and validate the project end-to-end (frontend + API + supporting services) so anyone on the team can reproduce the environment and confirm it works.
- **Current state:**
  - Mono-repo with `api_server/` (Python), `frontend/` (Vite + React + Tailwind), `nginx/`, `docker-compose.yml`, `models/`, and runtime folders under `data/`.
  - Frontend uses npm (lockfile present) and includes standard scripts for dev/build/lint/preview.
- **Related docs:** Existing report(s) under `docs/clockouts/`.

## 2) Objective
- **Primary goal:** Validate that the project runs successfully and document exact steps for local development and docker-based execution.
- **Success criteria (definition of done):**
  - [ ] Clear run instructions exist in `README.md` (local + docker).
  - [ ] Frontend builds successfully: `cd frontend && npm run build`.
  - [ ] Frontend runs locally: `cd frontend && npm run dev` (smoke check).
  - [ ] Docker compose builds and starts (if applicable): `docker compose build` + `docker compose up`.
  - [ ] Basic smoke validation is documented (what URL to open, what endpoint to hit, expected result).
  - [ ] A clock-out report summarizes commands run and outcomes.

## 3) Scope
### In scope
- Determine and document:
  - How to run frontend locally (npm commands, ports, env vars).
  - How to run backend/API locally or via docker-compose.
  - How nginx is used (if it’s part of the local stack).
- Execute baseline validation steps and record results.
- Minimal fixes **only if required** to make the project run (e.g., missing env example, missing command in docs).

### Out of scope
- Refactoring or code cleanup.
- Reformatting files, lint/Prettier changes, or restructuring folders unless strictly necessary to run.
- Feature development or behavior changes.

## 4) Assumptions
- Frontend uses **npm** because `frontend/package-lock.json` exists.
- Backend is orchestrated through `docker-compose.yml` (verify by inspection).
- Environment variables may be required (verify by searching code/config references).

## 5) Risks & Mitigations
- **Risk:** Missing or unclear env variables prevent the app from running.
  - **Mitigation:** Identify required env vars from config/code and document them in `.env.example` + README.
- **Risk:** Services rely on local files/paths that differ between machines.
  - **Mitigation:** Document required directories/volumes and expected structure; confirm docker volume mounts.
- **Risk:** Port conflicts or unclear entry points.
  - **Mitigation:** Document ports and entry commands; standardize the “source of truth” in README.

## 6) Plan (Phased)

### Phase 0 — Discovery (no changes)
1. Inspect `docker-compose.yml`, `api_server/Dockerfile`, `requirements.txt`, and `frontend/package.json`.
2. Identify:
   - Main services and how they connect (API ↔ frontend ↔ nginx).
   - Ports exposed and URLs to test.

### Phase 1 — Local frontend validation (npm)
1. Run:
   - `cd frontend && npm ci`
   - `cd frontend && npm run build`
   - `cd frontend && npm run dev` (smoke check)
2. Record outputs and any required env vars.

### Phase 2 — Docker validation (if applicable)
1. Run:
   - `docker compose build`
   - `docker compose up`
2. Smoke test:
   - Which URL to open in browser
   - Which API endpoint to hit (if any) and expected response
3. Record results.

### Phase 3 — Documentation
1. Update `README.md` with:
   - Local run steps (frontend + backend)
   - Docker run steps
   - Ports/URLs and smoke-test checklist
   - Env var setup (reference `.env.example`)

### Phase 4 — Clock-out
1. Write `docs/clockouts/2026-02-20-validation.md` summarizing:
   - Commands run
   - What worked / what didn’t
   - Required env vars
   - Next actions (if any)

## 7) Validation Plan
- **Frontend:**
  - `cd frontend && npm ci`
  - `cd frontend && npm run build`
  - `cd frontend && npm run dev`
- **Docker (if used):**
  - `docker compose build`
  - `docker compose up`
- **Manual checks:**
  - Frontend page loads
  - Any critical API path responds (document the exact endpoint)

## 8) Rollback Strategy
- Work on a dedicated branch (e.g., `chore/validation-notes`).
- If documentation-only, rollback is simply reverting commits.

## 9) Deliverables
- Updated `README.md` with reproducible run instructions
- `.env.example` updated (only if needed)
- Clock-out report: `docs/clockouts/2026-02-20-validation.md`

## 10) Notes / Questions
- Confirm whether backend is intended to be run primarily via docker-compose or also directly (python/uvicorn/etc.).
- Confirm which service is the “public” entry point (nginx vs Vite dev server).
