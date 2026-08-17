# Learning Notes, Methodologies, Pros, Cons, and Tradeoffs

## Methodologies Used

### 1. Configuration-driven rules

The Personalization Engine uses JSON rules for intent mapping, context selection, exclusions, and response preferences.

Pros:

- Easy to extend without changing code.
- Reviewers can inspect business logic directly.
- New intents can be added quickly.

Cons:

- Requires careful validation.
- Complex rules may become hard to debug if the config grows too much.

Tradeoff:

- For this POC, JSON is a strong fit because it is simple, inspectable, fast to modify, and avoids extra native dependencies on the local Python 3.14 environment.

### 2. Concurrent upstream fetching

All upstream services should be fetched at the same time using async HTTP calls.

Pros:

- Lower latency than sequential calls.
- Demonstrates backend orchestration skills.
- Matches the assignment requirement directly.

Cons:

- Error handling is more complex.
- Logs need request ids and per-service metadata to stay understandable.

Tradeoff:

- Worth doing even in a POC because the assignment explicitly evaluates this.

### 3. Partial failure tolerance

The system should continue when non-critical astrology services fail.

Pros:

- More resilient demo.
- Realistic service behavior.
- Allows confidence to reflect missing context.

Cons:

- The answer may be less grounded.
- Requires explicit confidence scoring and source tracking.

Tradeoff:

- User profile should be treated as required. Kundli, horoscope, and panchang can degrade gracefully.

### 4. Prompt optimization

The prompt should include only context selected by the engine.

Pros:

- Lower token usage.
- Better grounding.
- Easier to audit.
- Directly demonstrates the assignment's main evaluation criteria.

Cons:

- A bad rule may exclude useful context.
- General questions require careful balancing.

Tradeoff:

- Prefer explicit source selection over sending full JSON. The debug endpoint helps prove what was selected and why.

### 5. Swappable LLM provider interface

The backend should call LLMs through a provider abstraction.

Pros:

- Works with OpenRouter, LM Studio, OpenAI-compatible APIs, or mock mode.
- Avoids vendor lock-in.
- Lets the project run without secrets.

Cons:

- Provider differences still leak through in model behavior and JSON reliability.
- Some providers support structured output better than others.

Tradeoff:

- Use a common OpenAI-compatible chat completion shape for the POC, then add provider-specific enhancements later.

### 6. In-memory cache first

Use a small TTL cache in the backend and browser `localStorage` in the frontend.

Pros:

- Minimal setup.
- Easy to understand.
- Satisfies the assignment's caching expectation.

Cons:

- Not shared across backend workers.
- Lost on restart.
- No central invalidation.

Tradeoff:

- Good for the POC. Redis can replace the cache interface later.

### 7. Mock services over HTTP

Expose mock upstream services as local FastAPI routes and call them with HTTP clients.

Pros:

- Demonstrates real concurrency, retries, timeouts, and partial failure handling.
- Easy for reviewers to run.
- Keeps external dependencies low.

Cons:

- Slightly more code than direct function calls.
- Same-process mocks are not identical to true distributed services.

Tradeoff:

- Better assignment signal than static local function calls.

## Important Design Decisions

### Intent detection starts simple

Start with keyword scoring from config.

Reason:

- Easy to explain in follow-up discussion.
- Deterministic and testable.
- Sufficient for sample questions.

Future:

- Add embedding similarity or LLM classification behind the same interface.

### Confidence is deterministic

Confidence should be calculated from available selected context and upstream failures, not guessed freely by the LLM.

Reason:

- More auditable.
- Prevents confident answers when key context is missing.

Future:

- Combine deterministic context confidence with model self-assessment or evaluator checks.

### The debug endpoint is a first-class feature

The debug endpoint should reuse the real engine path and stop before the LLM call.

Reason:

- Demonstrates explainability.
- Makes testing easier.
- Shows exactly what the assignment evaluates.

## Production Concerns Intentionally Left Out

The first POC should not spend time on:

- OAuth or user authentication
- Role-based access control
- Distributed tracing
- Kubernetes deployment
- Advanced secret rotation
- Redis cluster setup
- Rate limiting by user
- Full observability dashboard
- Prompt injection defense beyond basic context boundaries
- Human feedback loops
- Multi-language quality evaluation

These are valid production concerns, but they are not the main assignment objective.

## What To Improve With Another Day

- Add Redis cache implementation behind the same cache interface.
- Persist request metadata to MongoDB.
- Add provider-native JSON schema mode where supported.
- Add an embedding-based intent classifier.
- Add prompt snapshot tests.
- Add source-level token budgeting.
- Add a small admin endpoint to inspect personalization rules.
- Add richer UI controls for language, provider, model, and cache refresh.
- Add fault-injection tests for every upstream service.

## Implementation Lessons From This Environment

- Python 3.14 required loose backend dependency pins so pip could choose compatible wheels.
- JSON config avoided an unnecessary native dependency and still kept personalization rules externalized.
- Deterministic engine confidence is preferable to LLM-reported confidence because it reflects actual source availability.
- Calling same-app mock services over HTTP is useful for demonstrating orchestration, but API unit tests should monkeypatch the fetcher to avoid needing a live server.
- Keeping data source and LLM provider as request-level options is useful for demos: reviewers can compare mock data, MongoDB data, mock LLM output, and real LLM output without restarting the backend.
- The OpenRouter key file contained an assignment-style line, so the local `.env` writer now extracts the actual `sk-or-...` token instead of assuming the whole file is the key.
- Passwords are hashed with salted PBKDF2-SHA256 using the Python standard library. This avoids native bcrypt/argon2 build issues in the current Python 3.14 environment, but argon2id would be preferred in production.
- RBAC is deliberately simple: admin can select any user; normal users can only personalize for their own business `id`.
- Stripe Checkout is integrated as a boundary with a mock fallback because a full billing lifecycle needs webhook handling and production Stripe price configuration.
- The UI was reframed as a dark studio experience while keeping the personalization engine central. The constellation preview and dynamic style gallery are visual affordances; the actual evaluated features remain visible on the same page.
- Log viewing uses manual refresh rather than live polling to avoid unnecessary backend load during the POC demo.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Prompt includes too much context | Use config-selected context and prompt size logging. |
| LLM returns invalid JSON | Parse defensively and fallback to structured response. |
| Upstream service fails | Continue with partial context and lower confidence. |
| Intent detection misses phrasing | Keep intent keywords in config and add tests for sample questions. |
| API key unavailable | Use mock provider or LM Studio local provider. |
| LM Studio model is not ideal for natural guidance | Keep provider swappable and document recommended general instruct models. |
| MongoDB slows setup | Make Mongo optional and use mock data by default. |

## Core Evaluation Story

The final implementation should let the reviewer see this clearly:

1. The backend did not send every upstream payload to the LLM.
2. The engine chose context based on intent.
3. The chosen context and exclusions are explainable through `/debug/personalization`.
4. User preferences affected language, tone, and length.
5. The LLM call was grounded in selected structured data.
6. Failures were handled gracefully and reflected in confidence.
