"""SEO agent orchestrator."""

import logging
from datetime import datetime
from typing import List

from seo_agent.models import (
    InputSpec, ParsedDocument, KeywordCandidate, Cluster, Recommendation, RunReport
)
from seo_agent.tools.hf.fetcher import Fetcher, Parser
from seo_agent.tools.hf.keywords import KeywordExtractor
from seo_agent.tools.hf.clustering import Embedder, SemanticClusterer
from seo_agent.tools.openai.embedder import OpenAIEmbedder
from seo_agent.tools.openai.recommender import OpenAIRecommender

logger = logging.getLogger(__name__)


class SEOAgent:
    """Orchestrates SEO analysis pipeline."""
    
    def __init__(self):
        self.fetcher = Fetcher()
        self.parser = Parser()
        self.keyword_extractor = KeywordExtractor()
        self.embedder = None  # Will be initialized per-request
        self.clusterer = SemanticClusterer(n_clusters=5)
        self.openai_recommender = OpenAIRecommender()
    
    async def analyze(self, input_spec: InputSpec) -> RunReport:
        """Run full SEO analysis."""
        logger.info(f"Starting analysis for URLs: {input_spec.urls}")
        logger.info(f"Settings: embedding_provider={input_spec.embedding_provider}, use_openai={input_spec.use_openai}")
        
        started_at = datetime.now()
        errors: List[str] = []
        documents: List[ParsedDocument] = []
        
        # Step 1: Fetch and parse URLs
        for url in input_spec.urls[:input_spec.max_pages]:
            try:
                fetch_result = await self.fetcher.fetch(str(url))
                if fetch_result.error:
                    errors.append(f"Fetch error for {url}: {fetch_result.error}")
                    continue
                
                parsed = self.parser.parse(fetch_result)
                if parsed.error:
                    errors.append(f"Parse error for {url}: {parsed.error}")
                    continue
                
                documents.append(parsed)
            except Exception as e:
                errors.append(f"Error processing {url}: {str(e)}")
        
        documents_parsed = len(documents)
        logger.info(f"Fetched and parsed {documents_parsed} documents")
        if documents:
            logger.debug(f"Document details: {[{'url': d.url, 'word_count': d.word_count, 'error': d.error} for d in documents]}")
        
        # Step 2: Extract keywords
        keywords: List[KeywordCandidate] = []
        if documents:
            try:
                keywords = self.keyword_extractor.extract(documents)
                logger.info(f"Extracted {len(keywords)} keywords")
            except Exception as e:
                error_msg = f"Keyword extraction error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
        
        # Step 3: Generate embeddings
        clusters: List[Cluster] = []
        if keywords:
            try:
                logger.info(f"Using {input_spec.embedding_provider} embeddings provider")
                # Choose embedder based on input spec
                if input_spec.embedding_provider == "openai":
                    if not OpenAIEmbedder().is_enabled:
                        error_msg = "OpenAI API key not set for embeddings"
                        logger.warning(error_msg)
                        errors.append(error_msg)
                        embeddings = None
                    else:
                        logger.info(f"Initializing OpenAI embedder with model: {input_spec.openai_embedding_model}")
                        openai_embedder = OpenAIEmbedder(model=input_spec.openai_embedding_model)
                        embeddings = await openai_embedder.embed_keywords(keywords)
                        logger.info(f"Generated {len(embeddings)} OpenAI embeddings")
                else:
                    # HuggingFace embedder
                    logger.info(f"Initializing HF embedder with model: {input_spec.hf_embedding_model}")
                    self.embedder = Embedder(model_name=input_spec.hf_embedding_model)
                    embeddings = self.embedder.embed_keywords(keywords)
                    logger.info(f"Generated {len(embeddings)} HF embeddings")
                
                if embeddings:
                    logger.info(f"Clustering {len(embeddings)} embeddings")
                    clusters = self.clusterer.cluster(keywords, embeddings)
                    logger.info(f"Created {len(clusters)} clusters")
            except Exception as e:
                error_msg = f"Clustering error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
        
        # Step 4: Generate recommendations
        logger.info("Generating recommendations")
        try:
            recommendations = await self._generate_recommendations(
                documents, keywords, clusters, input_spec, errors
            )
            logger.info(f"Generated {len(recommendations)} recommendations")
        except Exception as e:
            error_msg = f"Recommendation generation error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            recommendations = []
        
        logger.info(f"Analysis complete. Errors: {len(errors)}")
        logger.debug(f"Creating RunReport with input_spec type: {type(input_spec)}")
        
        try:
            # Convert input_spec to dict for Pydantic v2 compatibility
            input_spec_dict = input_spec.model_dump() if hasattr(input_spec, 'model_dump') else input_spec.dict()
            
            report = RunReport(
                input_spec=input_spec_dict,
                status="completed" if not errors else "partial",
                documents_parsed=documents_parsed,
                keywords_extracted=keywords[:20],  # Top 20
                clusters=clusters,
                recommendations=recommendations,
                started_at=started_at,
                errors=errors,
            )
        except Exception as e:
            logger.error(f"Failed to create RunReport: {str(e)}", exc_info=True)
            logger.debug(f"input_spec: {input_spec}")
            raise
        
        logger.info(f"Report created with run_id: {report.run_id}")
        return report
    
    async def _generate_recommendations(
        self,
        documents: List[ParsedDocument],
        keywords: List[KeywordCandidate],
        clusters: List[Cluster],
        input_spec: InputSpec,
        errors: List[str],
    ) -> List[Recommendation]:
        """Generate SEO recommendations based on analysis."""
        recommendations: List[Recommendation] = []
        
        if not documents:
            return recommendations
        
        # Rec 1: Keyword coverage
        if keywords:
            recommendations.append(Recommendation(
                title="Focus on semantic clusters",
                description=f"Found {len(clusters)} semantic clusters. Target each with dedicated content.",
                priority=4,
                category="keywords",
                evidence={"clusters": len(clusters), "keywords": len(keywords)},
                action_items=["Map content to clusters", "Identify content gaps"]
            ))
        
        # Rec 2: Content length
        avg_words = sum(d.word_count for d in documents) / len(documents)
        if avg_words < 500:
            recommendations.append(Recommendation(
                title="Improve content depth",
                description=f"Average content length is {int(avg_words)} words. Aim for 1000+ words.",
                priority=3,
                category="on-page",
                evidence={"avg_words": avg_words},
                action_items=["Expand thin content", "Add more sections"]
            ))
        
        # Rec 3: Heading structure
        total_headings = sum(len(d.headings) for d in documents)
        if total_headings < len(documents) * 3:
            recommendations.append(Recommendation(
                title="Add structured headings",
                description="Use H2/H3 headings to improve structure and SEO.",
                priority=3,
                category="on-page",
                evidence={"total_headings": total_headings},
                action_items=["Add H2 for main topics", "Add H3 for subtopics"]
            ))
        
        # Rec 4: Meta descriptions
        docs_without_meta = sum(1 for d in documents if not d.description)
        if docs_without_meta > 0:
            recommendations.append(Recommendation(
                title="Add meta descriptions",
                description=f"{docs_without_meta} pages missing meta descriptions.",
                priority=2,
                category="on-page",
                evidence={"missing": docs_without_meta},
                action_items=["Write meta descriptions", "Keep 150-160 chars"]
            ))
        
        # Optional: OpenAI recommendations
        if input_spec.use_openai:
            if self.openai_recommender.is_enabled:
                try:
                    self.openai_recommender.model = input_spec.openai_model
                    openai_recs = await self.openai_recommender.generate_recommendations(
                        documents,
                        keywords,
                        clusters,
                        max_items=5,
                    )
                    recommendations.extend(openai_recs)
                except Exception as e:
                    errors.append(f"OpenAI error: {str(e)}")
            else:
                errors.append("OpenAI API key not set. Add OPENAI_API_KEY to .env")
        
        return recommendations[:5]  # Top 5
