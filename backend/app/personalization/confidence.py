from app.models.context import UserContextBundle
from app.models.personalization import ContextItem
from app.models.responses import Confidence


def score_confidence(bundle: UserContextBundle, selected_context: list[ContextItem]) -> tuple[Confidence, dict]:
    primary_count = sum(1 for item in selected_context if item.priority == "primary")
    failed_count = len(bundle.failed_sources)
    factors = {
        "primaryContextCount": primary_count,
        "failedSources": bundle.failed_sources,
        "failedSourceCount": failed_count,
    }

    if primary_count >= 2 and failed_count == 0:
        return "HIGH", factors
    if primary_count >= 1 and failed_count <= 1:
        return "MEDIUM", factors
    return "LOW", factors
