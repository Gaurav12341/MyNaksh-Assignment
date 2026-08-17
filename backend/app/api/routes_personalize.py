from fastapi import APIRouter, Depends, Request

from app.core.auth import ensure_can_access_user, get_current_user
from app.core.config import get_settings
from app.core.logging import get_logger
from app.llm.provider_factory import create_llm_provider
from app.models.requests import PersonalizeRequest
from app.models.responses import PersonalizeResponse
from app.personalization.engine import PersonalizationEngine
from app.personalization.prompt_builder import PromptBuilder
from app.services.context_fetcher import ContextFetcher

router = APIRouter(tags=["personalize"])
logger = get_logger(__name__)


@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize(payload: PersonalizeRequest, request: Request, current_user=Depends(get_current_user)):
    settings = get_settings().with_overrides(llm_provider=payload.llmProvider, llm_model=payload.llmModel)
    request_id = getattr(request.state, "request_id", None)
    ensure_can_access_user(current_user, payload.userId)
    bundle = await ContextFetcher(settings).fetch_all(
        payload.userId,
        request_id=request_id,
        data_source=payload.dataSource,
    )
    plan = PersonalizationEngine().build_plan(payload.question, bundle)
    prompt = PromptBuilder().build(payload.question, plan)

    logger.info(
        "prompt_built",
        extra={
            "request_id": request_id or "-",
            "user_id": payload.userId,
            "intent": plan.intent,
            "prompt_chars": len(prompt),
            "sources_used": plan.sources_used,
            "failed_sources": plan.failed_sources,
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
        },
    )

    try:
        provider = create_llm_provider(settings)
        llm_result = await provider.generate(prompt, model=settings.llm_model, max_tokens=max(plan.max_words * 2, 300))
        answer = llm_result.answer
        confidence = plan.confidence
    except Exception as exc:
        logger.warning(
            "llm_generation_failed_using_fallback",
            extra={
                "request_id": request_id or "-",
                "user_id": payload.userId,
                "intent": plan.intent,
                "error": str(exc),
            },
        )
        answer = fallback_answer(payload.question, plan)
        confidence = "LOW" if plan.confidence == "LOW" else "MEDIUM"

    logger.info(
        "personalize_response user_id=%s actor_id=%s actor_role=%s data_source=%s llm_provider=%s intent=%s confidence=%s sources=%s answer_preview=%s",
        payload.userId,
        current_user.get("id"),
        current_user.get("role"),
        payload.dataSource,
        settings.llm_provider,
        plan.intent,
        confidence,
        "|".join(plan.sources_used),
        answer[:160].replace("\n", " "),
    )
    return PersonalizeResponse(answer=answer, confidence=confidence, sourcesUsed=plan.sources_used)


def fallback_answer(question: str, plan) -> str:
    source_list = ", ".join(plan.sources_used) if plan.sources_used else "limited available context"
    return (
        f"I could not reach the configured LLM provider, so this fallback answer is based on {source_list}. "
        f"For your question, '{question}', the selected context points to a {plan.tone.lower()} and cautious reading. "
        "Use this as reflective guidance, compare it with real-world facts, and avoid making a major decision from "
        "astrology alone."
    )
