# MyNaksh Personalized AI Context Engine

Proof-of-concept implementation for the MyNaksh backend assignment.

The project focuses on the layer between structured backend services and an LLM: concurrent context gathering, intent detection, config-driven context selection, response personalization, optimized prompt construction, and grounded AI response generation.

## Stack

- Backend: Python, FastAPI, Pydantic, httpx
- Frontend: React + Vite
- Cache: in-memory backend TTL cache and browser `localStorage`
- Database: MongoDB-backed service data, with mock-data fallback
- LLM: mock, OpenRouter, LM Studio, or generic OpenAI-compatible API
- Personalization config: JSON files in `backend/configs`

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Default mode uses the mock LLM provider, so no API key is required.

## Seed MongoDB

MongoDB is optional at runtime because the UI can still use mock data, but the POC includes a seeded Mongo path.

```bash
cd backend
python scripts\seed_mongo.py
```

This creates `mynaksh_poc` with:

- `users`: 10 user profiles plus one master admin, primary key `_id=<guid>`
- `kundlis`: one document per astrology user, unique `userRefId` reference to `users._id`
- `horoscopes`: one document per astrology user, unique `userRefId` reference to `users._id`
- `panchangs`: date-keyed panchang documents with GUID `_id`

Seeded demo credentials:

- Admin: `admin` / `Admin@12345`
- Users: `user_101` through `user_110` / `Password@123`

Passwords are stored as salted PBKDF2-SHA256 hashes, not plaintext.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Required API Examples

First login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"usernameOrEmail\":\"admin\",\"password\":\"Admin@12345\"}"
```

Use the returned token as `Authorization: Bearer <token>` for `/personalize`, `/debug/personalization`, admin user listing, and billing.

```bash
curl -X POST http://127.0.0.1:8000/personalize ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer <token>" ^
  -d "{\"userId\":\"user_101\",\"question\":\"Should I consider changing my job in the next few months?\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/debug/personalization ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer <token>" ^
  -d "{\"userId\":\"user_101\",\"question\":\"Should I consider changing my job in the next few months?\"}"
```

## LLM Configuration

Mock mode:

```env
LLM_PROVIDER=mock
```

OpenRouter:

```env
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-oss-120b
OPENROUTER_API_KEY=your_key_here
```

LM Studio:

```env
LLM_PROVIDER=lmstudio
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=qwen2.5-coder-14b-instruct
```

## Tests

```bash
cd backend
pytest
```

## Notes

Detailed planning and tradeoff documentation lives in:

- `docs/DETAILED_PLAN.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/LEARNING_NOTES.md`

The UI includes per-request selectors for:

- Data source: mock data or MongoDB data
- LLM provider: mock, OpenRouter, LM Studio, or generic OpenAI-compatible
- Model name, for non-mock providers

## Auth and RBAC

- `POST /auth/login` returns a signed bearer token.
- `POST /auth/register` creates a MongoDB user with a hashed password.
- `GET /auth/users` is admin-only and powers the UI dropdown.
- Normal users can only ask questions for their own `userId`.
- The master admin can select any user from the dropdown.

## Logs

Backend logs are written to both console and rotating files:

```text
backend/logs/app.log
```

The log file captures request/session details such as actor user, role, selected target user, data source, LLM provider, intent, confidence, selected sources, and a short answer preview.

Admins can view recent logs from the UI using the `Live Logs` console and its `Refresh` button. The backend endpoint is:

```http
GET /admin/logs?lines=120
```

## Stripe

`POST /billing/checkout` creates a Stripe Checkout Session in `subscription` mode when `STRIPE_SECRET_KEY` and the relevant price ID are configured.

If Stripe config is missing, the endpoint returns a mock checkout result and updates the user to premium for POC testing.

## Assumptions

- This is a POC, not a production service.
- Auth is intentionally basic and uses signed local bearer tokens, not OAuth/OIDC.
- Mock upstream services are hosted in the same FastAPI app but called over HTTP during normal runtime.
- User profile is required. Kundli, horoscope, and panchang can fail partially.
- Astrology responses are framed as reflective guidance, not certainty.

## Tradeoffs

- Keyword intent detection is deterministic and explainable, but less flexible than embeddings or LLM classification.
- In-memory cache satisfies the POC requirement but is not shared across processes.
- MongoDB is optional to keep the demo simple.
- The UI is intentionally thin because backend context orchestration is the main evaluation target.
