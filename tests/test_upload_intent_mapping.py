"""Tests for intent mapping used by keyword upload flow."""

from seo_agent.models import IntentType
from seo_agent.tools.hf.keywords import KeywordExtractor


def test_upload_keyword_delivery_maps_to_transactional() -> None:
    """Upload flow should classify 'доставка' as transactional intent."""
    extractor = KeywordExtractor()

    assert extractor._detect_intent("доставка груза") == IntentType.TRANSACTIONAL


def test_upload_keyword_uses_custom_db_phrase_extension() -> None:
    """Upload flow should support custom phrases from DB via extra_phrases."""
    extractor = KeywordExtractor(extra_phrases={"commercial": ["что выбрать"]})

    assert extractor._detect_intent("что выбрать для логистики") == IntentType.COMMERCIAL
