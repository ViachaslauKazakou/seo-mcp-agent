"""Tests for keyword intent detection heuristics."""

import pytest

from seo_agent.models import IntentType
from seo_agent.tools.hf.keywords import KeywordExtractor


@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("доставка по москве", IntentType.TRANSACTIONAL),
        ("buy laptop online", IntentType.TRANSACTIONAL),
        ("лучший ноутбук 2026", IntentType.COMMERCIAL),
        ("официальный сайт dellin", IntentType.NAVIGATIONAL),
        ("как выбрать перевозчика", IntentType.INFORMATIONAL),
        ("какой-то неизвестный запрос", IntentType.INFORMATIONAL),
    ],
)
def test_detect_intent_from_default_config(keyword: str, expected: IntentType) -> None:
    """Extractor should map keywords to intents using default phrase config."""
    extractor = KeywordExtractor()

    assert extractor._detect_intent(keyword) == expected


def test_detect_intent_with_custom_extra_phrases() -> None:
    """Custom phrases should extend built-in rules and affect classification."""
    extractor = KeywordExtractor(
        extra_phrases={
            "transactional": ["расчет маршрута"],
        }
    )

    assert extractor._detect_intent("расчет маршрута для перевозки") == IntentType.TRANSACTIONAL
