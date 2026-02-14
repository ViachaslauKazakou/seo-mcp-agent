"""Clustering and semantic analysis tool."""

import os
from pathlib import Path
from typing import List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from seo_agent.models import KeywordCandidate, EmbeddingRecord, Cluster


# Load environment variables
root_dir = Path(__file__).resolve().parents[4]
load_dotenv(root_dir / ".env")


class Embedder:
    """Generate embeddings for keywords."""
    
    def __init__(self, model_name: str | None = None):
        # Use provided model, env variable, or default
        if model_name is None:
            model_name = os.getenv("HF_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        self.model_name = model_name
        hf_token = os.getenv("HF_TOKEN")
        
        # Load model with optional token
        self.model = SentenceTransformer(
            model_name,
            token=hf_token if hf_token else None
        )
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    def embed_keywords(self, keywords: List[KeywordCandidate]) -> List[EmbeddingRecord]:
        """Generate embeddings for keyword candidates."""
        if not keywords:
            return []
        
        keyword_texts = [kw.keyword for kw in keywords]
        embeddings = self.embed(keyword_texts)
        
        records = []
        for kw, emb in zip(keywords, embeddings):
            # Use first source URL or placeholder
            source_url = kw.source_urls[0] if kw.source_urls else "unknown"
            records.append(EmbeddingRecord(
                text=kw.keyword,
                embedding=emb,
                source_url=source_url
            ))
        
        return records


class SemanticClusterer:
    """Cluster keywords semantically."""
    
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
    
    def cluster(
        self,
        keywords: List[KeywordCandidate],
        embeddings: List[EmbeddingRecord]
    ) -> List[Cluster]:
        """Cluster keywords using embeddings."""
        if len(keywords) < self.n_clusters:
            # If few keywords, create one cluster
            if keywords:
                centroid = np.mean([np.array(e.embedding) for e in embeddings], axis=0).tolist()
                
                # Calculate statistics for single cluster
                sorted_keywords = sorted(keywords, key=lambda k: k.tf_idf_score, reverse=True)
                top_5_keywords = [kw.keyword for kw in sorted_keywords[:5]]
                avg_tfidf = sum(kw.tf_idf_score for kw in keywords) / len(keywords)
                
                # Calculate intent distribution
                intent_dist = {}
                for kw in keywords:
                    if kw.intent:
                        intent_name = kw.intent.value if hasattr(kw.intent, 'value') else str(kw.intent)
                        intent_dist[intent_name] = intent_dist.get(intent_name, 0) + 1
                
                return [Cluster(
                    cluster_id=0,
                    keywords=keywords,
                    centroid=centroid,
                    cohesion_score=1.0,
                    topic_summary="Primary Topic",
                    size=len(keywords),
                    avg_tfidf=avg_tfidf,
                    top_keywords=top_5_keywords,
                    intent_distribution=intent_dist
                )]
            return []
        
        try:
            # K-means clustering
            embedding_matrix = np.array([e.embedding for e in embeddings])
            kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
            labels = kmeans.fit_predict(embedding_matrix)
            
            # Calculate silhouette score
            silhouette = silhouette_score(embedding_matrix, labels)
            
            # Build clusters
            clusters = []
            for cluster_id in range(self.n_clusters):
                mask = labels == cluster_id
                cluster_keywords = [kw for i, kw in enumerate(keywords) if mask[i]]
                
                if cluster_keywords:
                    centroid = kmeans.cluster_centers_[cluster_id].tolist()
                    
                    # Generate topic summary from top keywords
                    topic = ", ".join([kw.keyword for kw in cluster_keywords[:3]])
                    
                    # Calculate cluster statistics
                    sorted_keywords = sorted(cluster_keywords, key=lambda k: k.tf_idf_score, reverse=True)
                    top_5_keywords = [kw.keyword for kw in sorted_keywords[:5]]
                    avg_tfidf = sum(kw.tf_idf_score for kw in cluster_keywords) / len(cluster_keywords)
                    
                    # Calculate intent distribution
                    intent_dist = {}
                    for kw in cluster_keywords:
                        if kw.intent:
                            intent_name = kw.intent.value if hasattr(kw.intent, 'value') else str(kw.intent)
                            intent_dist[intent_name] = intent_dist.get(intent_name, 0) + 1
                    
                    clusters.append(Cluster(
                        cluster_id=cluster_id,
                        keywords=cluster_keywords,
                        centroid=centroid,
                        cohesion_score=float(silhouette),
                        topic_summary=topic,
                        suggested_content_topics=[topic],
                        size=len(cluster_keywords),
                        avg_tfidf=avg_tfidf,
                        top_keywords=top_5_keywords,
                        intent_distribution=intent_dist
                    ))
            
            return clusters
        except Exception as e:
            print(f"Clustering error: {e}")
            return []
