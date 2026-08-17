from fastapi import APIRouter, Depends, Request

from app.core.auth import ensure_can_access_user, get_current_user
from app.models.requests import PersonalizeRequest
from app.models.responses import DebugPersonalizationResponse
from app.core.logging import get_logger
from app.personalization.engine import PersonalizationEngine
from app.services.context_fetcher import ContextFetcher

router = APIRouter(tags=["debug"])
logger = get_logger(__name__)


@router.post("/debug/personalization", response_model=DebugPersonalizationResponse)
async def debug_personalization(payload: PersonalizeRequest, request: Request, current_user=Depends(get_current_user)):
    request_id = getattr(request.state, "request_id", None)
    ensure_can_access_user(current_user, payload.userId)
    bundle = await ContextFetcher().fetch_all(payload.userId, request_id=request_id, data_source=payload.dataSource)
    plan = PersonalizationEngine().build_plan(payload.question, bundle)
    logger.info(
        "debug_personalization_response user_id=%s actor_id=%s actor_role=%s data_source=%s intent=%s confidence=%s selected=%s excluded=%s",
        payload.userId,
        current_user.get("id"),
        current_user.get("role"),
        payload.dataSource,
        plan.intent,
        plan.confidence,
        "|".join(plan.sources_used),
        "|".join(plan.excluded_context),
    )
    return DebugPersonalizationResponse(
        intent=plan.intent,
        selectedContext=plan.sources_used,
        excludedContext=plan.excluded_context,
        language=plan.language,
        tone=plan.tone,
        maxWords=plan.max_words,
        availableSources=plan.available_sources,
        failedSources=plan.failed_sources,
        modifiers=plan.modifiers,
        confidence=plan.confidence,
        confidenceFactors=plan.confidence_factors,
    )
