#!/usr/bin/env python3
"""Integration test for stopwords, clustering and logging."""

import logging
from seo_agent.tools.hf.keywords import KeywordExtractor
from seo_agent.tools.hf.clustering import Embedder, SemanticClusterer
from seo_agent.models import ParsedDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Test data
test_doc = ParsedDocument(
    url="https://example.com",
    title="Test Page",
    main_text="""
    Купить автомобиль в Минске по выгодной цене. Продажа авто с пробегом и новых машин.
    Как выбрать автомобиль? Что нужно знать перед покупкой? Это важная информация.
    Цена на автомобили в Беларуси. Объявления о продаже авто. У нас большой выбор.
    На сайте есть все модели автомобилей. Купить машину можно онлайн.
    Автомобили с пробегом по низкой цене. Продажа новых и подержанных авто.
    """,
    word_count=150
)

print("\n" + "="*70)
print("STEP 1: KEYWORD EXTRACTION WITH STOPWORDS FILTERING")
print("="*70)

extractor = KeywordExtractor(max_keywords=15)
keywords = extractor.extract([test_doc])

print(f"\n✅ Extracted {len(keywords)} keywords:")
for kw in keywords[:10]:
    print(f"  • {kw.keyword:25} | TF-IDF: {kw.tf_idf_score:.3f} | Intent: {kw.intent}")

print("\n" + "="*70)
print("STEP 2: CLUSTERING WITH EXTENDED INFO")
print("="*70)

embedder = Embedder()
embeddings = embedder.embed_keywords(keywords)

clusterer = SemanticClusterer(n_clusters=3)
clusters = clusterer.cluster(keywords, embeddings)

print(f"\n✅ Created {len(clusters)} clusters:")
for cluster in clusters:
    print(f"\n  🏷️ Cluster {cluster.cluster_id}: {cluster.topic_summary}")
    print(f"     Size: {cluster.size} keywords")
    print(f"     Cohesion: {cluster.cohesion_score:.3f}")
    print(f"     Avg TF-IDF: {cluster.avg_tfidf:.3f}")
    print(f"     Top Keywords: {', '.join(cluster.top_keywords[:3])}")
    if cluster.intent_distribution:
        print(f"     Intent Distribution: {cluster.intent_distribution}")

print("\n" + "="*70)
print("TEST COMPLETED SUCCESSFULLY")
print("="*70 + "\n")
