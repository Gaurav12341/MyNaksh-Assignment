from app.models.context import SourceResult, UserContextBundle
from app.personalization.engine import PersonalizationEngine
from app.personalization.prompt_builder import PromptBuilder
from app.services.mocks.mock_data import HOROSCOPE, KUNDLI, PANCHANG, USER_PROFILES


def sample_bundle() -> UserContextBundle:
    return UserContextBundle(
        user=SourceResult(name="User Profile", data=USER_PROFILES["user_101"]),
        kundli=SourceResult(name="Kundli", data=KUNDLI["user_101"]),
        horoscope=SourceResult(name="Horoscope", data=HOROSCOPE["user_101"]),
        panchang=SourceResult(name="Panchang", data=PANCHANG),
    )


def test_career_question_selects_relevant_context():
    plan = PersonalizationEngine().build_plan(
        "Should I consider changing my job in the next few months?",
        sample_bundle(),
    )

    assert plan.intent == "career"
    assert "Career Horoscope" in plan.sources_used
    assert "10th House" in plan.sources_used
    assert "Current Dasha" in plan.sources_used
    assert "Relationship Horoscope" in plan.excluded_context
    assert plan.language == "English"
    assert plan.tone == "Motivational"
    assert plan.max_words == 250


def test_relationship_question_omits_career_horoscope_from_prompt():
    plan = PersonalizationEngine().build_plan(
        "How does this month look for my relationship?",
        sample_bundle(),
    )
    prompt = PromptBuilder().build("How does this month look for my relationship?", plan)

    assert plan.intent == "relationship"
    assert "Relationship Horoscope" in prompt
    assert "7th House" in prompt
    assert "Career Horoscope:" not in prompt


def test_partial_kundli_failure_reduces_confidence_but_keeps_horoscope():
    bundle = sample_bundle()
    bundle.kundli = SourceResult(name="Kundli", failed=True, error="timeout")

    plan = PersonalizationEngine().build_plan("What should I focus on for my health?", bundle)

    assert plan.intent == "health"
    assert "Health Horoscope" in plan.sources_used
    assert "Kundli" in plan.failed_sources
    assert plan.confidence in {"LOW", "MEDIUM"}
