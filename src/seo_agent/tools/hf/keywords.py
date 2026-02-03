"""Keyword extraction tool."""

from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import re

from seo_agent.models import KeywordCandidate, ParsedDocument


class KeywordExtractor:
    """Extract keywords from parsed documents."""
    
    def __init__(self, max_keywords: int = 50, ngram_range: tuple = (1, 3)):
        self.max_keywords = max_keywords
        self.ngram_range = ngram_range
    
    def extract(self, documents: List[ParsedDocument]) -> List[KeywordCandidate]:
        """Extract keywords from multiple documents."""
        if not documents:
            return []
        
        texts = [doc.main_text for doc in documents if doc.main_text]
        if not texts:
            return []
        
        try:
            # Adjust max_df based on number of documents to avoid min_df/max_df conflict
            # For small document sets, set max_df to 1.0 (100%)
            num_docs = len(texts)
            max_df = 1.0 if num_docs < 5 else 0.8
            
            # Create vectorizer with appropriate parameters
            vectorizer = TfidfVectorizer(
                ngram_range=self.ngram_range,
                max_features=self.max_keywords * 2,
                stop_words="english",
                lowercase=True,
                min_df=1,
                max_df=max_df,
            )
            
            # Compute TF-IDF
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top keywords across all documents
            scores = tfidf_matrix.sum(axis=0).A1
            top_indices = scores.argsort()[-self.max_keywords:][::-1]
            
            keywords = []
            for idx in top_indices:
                keyword = feature_names[idx]
                score = float(scores[idx])
                
                # Count frequency
                freq = sum(1 for doc in documents if keyword.lower() in doc.main_text.lower())
                
                # Determine intent (simple heuristic)
                intent = self._detect_intent(keyword)
                
                keywords.append(KeywordCandidate(
                    keyword=keyword,
                    frequency=freq,
                    tf_idf_score=score,
                    intent=intent,
                    source_urls=[doc.url for doc in documents if keyword.lower() in doc.main_text.lower()]
                ))
            
            return keywords
        except Exception as e:
            print(f"Keyword extraction error: {e}")
            return []
    
    @staticmethod
    def _detect_intent(keyword: str) -> str:
        """Simple intent detection heuristic."""
        keyword_lower = keyword.lower()
        
        commercial_words = ["buy", "price", "cost", "cheap", "discount", "deal", "sale"]
        if any(word in keyword_lower for word in commercial_words):
            return "commercial"
        
        transactional_words = ["how to", "tutorial", "guide", "best", "top"]
        if any(word in keyword_lower for word in transactional_words):
            return "informational"
        
        return "informational"
