#!/usr/bin/env python3
"""Test stopwords filtering and logging."""

import logging
from seo_agent.tools.hf.keywords import KeywordExtractor
from seo_agent.models import ParsedDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test data with stop words
test_doc = ParsedDocument(
    url="https://example.com",
    title="Test Page",
    main_text="""
    Купить автомобиль в Минске. Продажа авто с пробегом и новых машин.
    Как выбрать автомобиль? Что нужно знать перед покупкой?
    Цена на автомобили. Это важная информация для покупателей.
    У нас большой выбор автомобилей. На сайте есть все модели.
    """,
    word_count=100
)

extractor = KeywordExtractor(max_keywords=20)
keywords = extractor.extract([test_doc])

print("\n" + "="*60)
print("EXTRACTED KEYWORDS AFTER FILTERING:")
print("="*60)
for kw in keywords[:15]:
    print(f"  {kw.keyword:30} | TF-IDF: {kw.tf_idf_score:.3f} | Intent: {kw.intent}")
