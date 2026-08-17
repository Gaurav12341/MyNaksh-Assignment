# MyNaksh Personalized AI Context Engine

POC backend and React UI for the MyNaksh assignment. The main focus is the layer between structured services and an LLM: fetch context concurrently, detect intent, select only relevant data, personalize response settings, build a compact prompt, and return a grounded structured answer.

## Stack

- Backend: Python, FastAPI, Pydantic, httpx
- Frontend: React + Vite
- Database: MongoDB, with mock-data fallback
- Cache: backend in-memory TTL cache plus browser `localStorage`
- LLM providers: Mock LLM and OpenRouter implemented; LM Studio/OpenAI-compatible are UI placeholders for future extension
- Config: `backend/configs/personalization_rules.json` and `backend/configs/prompt_templates.json`

## Run

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Mongo Seed

MongoDB is optional because the UI can use mock data. To seed Mongo-backed services:

```bash
cd backend
python scripts\seed_mongo.py
```

Creates `mynaksh_poc` with 10 astrology users, one master admin, kundli, horoscope, and panchang documents. User-facing IDs remain `user_101` to `user_110`; database `_id` fields use GUIDs and related service documents reference users by `userRefId`.

Demo passwords are hashed with salted PBKDF2-SHA256 in MongoDB. See `backend/scripts/seed_mongo.py` for local seed credentials.

## Main APIs

Login first:

```bash
curl -X POST http://127.0.0.1:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"usernameOrEmail\":\"admin\",\"password\":\"<password>\"}"
```

Use the returned token as `Authorization: Bearer <token>`.

```bash
curl -X POST http://127.0.0.1:8000/personalize ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer <token>" ^
  -d "{\"userId\":\"user_101\",\"question\":\"Should I consider changing my job in the next few months?\"}"
```

Useful endpoints:

- `POST /personalize`
- `POST /debug/personalization`
- `POST /auth/login`
- `POST /auth/register`
- `GET /auth/users` admin only
- `GET /admin/logs?lines=120` admin only

## LLM Config

Mock mode requires no API key:

```env
LLM_PROVIDER=mock
```

OpenRouter:

```env
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-oss-120b
OPENROUTER_API_KEY=your_key_here
```

Real keys belong only in `backend/.env`, which is ignored by Git.

## Auth, RBAC, Logs

- Login returns a signed bearer token.
- Registered users are stored in MongoDB with hashed passwords.
- Normal users can only query their own profile.
- Master admin can select any seeded user.
- Backend logs go to console and `backend/logs/app.log`.
- Admins can view recent logs from the UI with the `Logs` panel refresh button.

## Stripe

Stripe subscription flow is **coming soon**. The current billing endpoint is POC-only: if Stripe settings are missing, it returns a mock checkout result for local testing. Do not treat subscription/payment behavior as production functional.

## Tests

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run build
```

## Assumptions

- This is a POC, not a production service.
- The assignment evaluates context selection and prompt orchestration more than UI polish or payment depth.
- User profile is required; kundli, horoscope, and panchang can partially fail.
- Astrology output is framed as reflective guidance, not deterministic prediction.
- Mock and Mongo data intentionally share the same public `userId` values for easy comparison.

## Trade-Offs

Intentionally simplified:

- Keyword-based intent detection instead of embeddings or LLM classification.
- In-memory backend cache instead of Redis.
- Local signed bearer tokens instead of OAuth/OIDC.
- Mock Stripe fallback instead of a full checkout, webhook, and entitlement lifecycle.
- Upstream services are simulated inside the same FastAPI app.

With another day:

- Add Redis and cache invalidation rules.
- Add real LM Studio/OpenAI-compatible provider wiring in the UI and backend.
- Add stronger prompt evaluation tests and source-selection regression fixtures.
- Add streaming responses and richer debug provenance.
- Add real Stripe Checkout, webhook handling, subscription status sync, and admin billing views.

Production concerns left out:

- Secrets manager, key rotation, and per-environment config management.
- Rate limiting, abuse protection, and audit-grade logging.
- Distributed tracing, metrics, alerting, and request correlation dashboards.
- Robust authorization policies, refresh tokens, password reset, email verification, and MFA.
- Containerization, deployment manifests, CI/CD, and load testing.

## Docs

More detailed planning notes are in:

- `docs/DETAILED_PLAN.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/LEARNING_NOTES.md`
