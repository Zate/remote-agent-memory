"""
Relevance Scorer

Multi-dimensional relevance scoring for memory search results.
Provides sophisticated scoring algorithms that consider semantic similarity,
temporal relevance, tag overlap, metadata matching, and contextual factors.

This scorer enables agents to make intelligent decisions about which memories
are most relevant for different types of tasks and contexts.
"""

import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ScoreDimension(Enum):
    """Dimensions used in multi-dimensional relevance scoring"""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    TEMPORAL_RELEVANCE = "temporal_relevance"
    TAG_OVERLAP = "tag_overlap"
    METADATA_MATCH = "metadata_match"
    CONTENT_TYPE_MATCH = "content_type_match"
    TECHNOLOGY_ALIGNMENT = "technology_alignment"
    CONTEXTUAL_SIMILARITY = "contextual_similarity"
    USAGE_FREQUENCY = "usage_frequency"


class ContextualFactor(Enum):
    """Contextual factors that influence relevance"""
    TASK_CATEGORY = "task_category"
    URGENCY_LEVEL = "urgency_level"
    COMPLEXITY_LEVEL = "complexity_level"
    DOMAIN_SPECIFICITY = "domain_specificity"
    ERROR_CONTEXT = "error_context"
    IMPLEMENTATION_STAGE = "implementation_stage"


@dataclass
class ScoringWeights:
    """Weights for different scoring dimensions"""
    semantic_similarity: float = 0.30
    temporal_relevance: float = 0.15
    tag_overlap: float = 0.20
    metadata_match: float = 0.10
    content_type_match: float = 0.10
    technology_alignment: float = 0.10
    contextual_similarity: float = 0.03
    usage_frequency: float = 0.02


@dataclass
class ScoringContext:
    """Context information for relevance scoring"""
    query_text: str
    query_tags: List[str]
    target_technologies: Set[str]
    task_category: str
    content_type_preference: Optional[str] = None
    temporal_preference: Optional[str] = None  # "recent", "historical", "any"
    metadata_requirements: Dict[str, Any] = None
    contextual_factors: Dict[ContextualFactor, Any] = None


@dataclass
class MemoryCandidate:
    """A memory candidate for relevance scoring"""
    content: str
    tags: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    content_hash: str
    base_similarity_score: float = 0.0
    usage_count: int = 0


@dataclass
class RelevanceScore:
    """Detailed relevance score with dimension breakdown"""
    total_score: float
    dimension_scores: Dict[ScoreDimension, float]
    confidence: float
    reasoning: List[str]
    boosters: List[str] = None  # Factors that increased relevance
    penalties: List[str] = None  # Factors that decreased relevance


class RelevanceScorer:
    """
    Advanced multi-dimensional relevance scoring system.
    
    Provides sophisticated relevance scoring that goes beyond simple semantic
    similarity to consider temporal factors, contextual alignment, and task-specific
    requirements.
    """
    
    def __init__(self):
        self.default_weights = ScoringWeights()
        self.technology_keywords = self._initialize_technology_keywords()
        self.content_type_patterns = self._initialize_content_type_patterns()
        self.temporal_decay_factors = self._initialize_temporal_factors()
    
    def _initialize_technology_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for technology detection and alignment"""
        return {
            "python": ["python", "py", "pip", "conda", "pytest", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "npm", "yarn", "react", "vue", "angular"],
            "typescript": ["typescript", "ts", "tsc", "tsx"],
            "docker": ["docker", "container", "dockerfile", "compose", "k8s", "kubernetes"],
            "database": ["database", "db", "sql", "postgres", "mysql", "mongo", "redis"],
            "api": ["api", "rest", "graphql", "endpoint", "microservice", "service"],
            "web": ["web", "http", "https", "html", "css", "frontend", "backend"],
            "cloud": ["aws", "azure", "gcp", "cloud", "serverless", "lambda"],
            "testing": ["test", "testing", "unit", "integration", "e2e", "spec", "mock"],
            "security": ["security", "auth", "oauth", "jwt", "ssl", "tls", "encryption"]
        }
    
    def _initialize_content_type_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for content type detection"""
        return {
            "decision": [
                r"decided|chosen|selected|going with|will use",
                r"solution|approach|strategy|plan",
                r"resolved|fixed|implemented|deployed"
            ],
            "error": [
                r"error|exception|failed?|crash|bug",
                r"not working|broken|issue|problem",
                r"debug|troubleshoot|fix"
            ],
            "implementation": [
                r"implement|create|build|develop|code",
                r"function|method|class|component|module",
                r"feature|functionality|requirement"
            ],
            "configuration": [
                r"config|configuration|setup|install",
                r"environment|settings|parameters",
                r"deploy|deployment|infrastructure"
            ],
            "best_practice": [
                r"best practice|recommendation|should|ought",
                r"pattern|convention|standard|guideline",
                r"lesson learned|experience|advice"
            ],
            "performance": [
                r"performance|optimize|speed|fast|slow",
                r"memory|cpu|resource|scalability",
                r"benchmark|profiling|bottleneck"
            ]
        }
    
    def _initialize_temporal_factors(self) -> Dict[str, Tuple[float, timedelta]]:
        """Initialize temporal decay factors for different time periods"""
        return {
            "immediate": (1.0, timedelta(days=1)),
            "recent": (0.95, timedelta(days=7)),
            "current": (0.85, timedelta(days=30)),
            "relevant": (0.70, timedelta(days=90)),
            "historical": (0.50, timedelta(days=365)),
            "archived": (0.30, timedelta(days=365*2))
        }
    
    def score_relevance(self, candidate: MemoryCandidate, context: ScoringContext,
                       weights: Optional[ScoringWeights] = None) -> RelevanceScore:
        """
        Score the relevance of a memory candidate for the given context.
        
        Args:
            candidate: Memory candidate to score
            context: Scoring context with query and requirements
            weights: Custom weights for scoring dimensions
            
        Returns:
            RelevanceScore with detailed breakdown
        """
        weights = weights or self.default_weights
        dimension_scores = {}
        reasoning = []
        boosters = []
        penalties = []
        
        # 1. Semantic Similarity (base score from search)
        semantic_score = candidate.base_similarity_score
        dimension_scores[ScoreDimension.SEMANTIC_SIMILARITY] = semantic_score
        if semantic_score > 0.8:
            boosters.append("High semantic similarity")
        elif semantic_score < 0.3:
            penalties.append("Low semantic similarity")
        
        # 2. Temporal Relevance
        temporal_score = self._calculate_temporal_relevance(candidate, context)
        dimension_scores[ScoreDimension.TEMPORAL_RELEVANCE] = temporal_score
        
        # 3. Tag Overlap
        tag_score = self._calculate_tag_overlap(candidate, context)
        dimension_scores[ScoreDimension.TAG_OVERLAP] = tag_score
        if tag_score > 0.7:
            boosters.append("Strong tag alignment")
        
        # 4. Metadata Match
        metadata_score = self._calculate_metadata_match(candidate, context)
        dimension_scores[ScoreDimension.METADATA_MATCH] = metadata_score
        
        # 5. Content Type Match
        content_type_score = self._calculate_content_type_match(candidate, context)
        dimension_scores[ScoreDimension.CONTENT_TYPE_MATCH] = content_type_score
        
        # 6. Technology Alignment
        tech_score = self._calculate_technology_alignment(candidate, context)
        dimension_scores[ScoreDimension.TECHNOLOGY_ALIGNMENT] = tech_score
        if tech_score > 0.8:
            boosters.append("Perfect technology match")
        
        # 7. Contextual Similarity
        contextual_score = self._calculate_contextual_similarity(candidate, context)
        dimension_scores[ScoreDimension.CONTEXTUAL_SIMILARITY] = contextual_score
        
        # 8. Usage Frequency
        usage_score = self._calculate_usage_frequency(candidate, context)
        dimension_scores[ScoreDimension.USAGE_FREQUENCY] = usage_score
        
        # Calculate weighted total score
        total_score = (
            semantic_score * weights.semantic_similarity +
            temporal_score * weights.temporal_relevance +
            tag_score * weights.tag_overlap +
            metadata_score * weights.metadata_match +
            content_type_score * weights.content_type_match +
            tech_score * weights.technology_alignment +
            contextual_score * weights.contextual_similarity +
            usage_score * weights.usage_frequency
        )
        
        # Apply contextual boosters and penalties
        total_score, boost_penalty_info = self._apply_contextual_adjustments(
            total_score, candidate, context, boosters, penalties
        )
        boosters.extend(boost_penalty_info["boosters"])
        penalties.extend(boost_penalty_info["penalties"])
        
        # Calculate confidence based on score distribution
        confidence = self._calculate_confidence(dimension_scores, total_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(dimension_scores, boosters, penalties)
        
        return RelevanceScore(
            total_score=min(1.0, max(0.0, total_score)),
            dimension_scores=dimension_scores,
            confidence=confidence,
            reasoning=reasoning,
            boosters=boosters,
            penalties=penalties
        )
    
    def _calculate_temporal_relevance(self, candidate: MemoryCandidate, 
                                    context: ScoringContext) -> float:
        """Calculate temporal relevance score"""
        if not candidate.timestamp:
            return 0.5  # Neutral score for missing timestamp
        
        time_diff = datetime.now() - candidate.timestamp
        
        # Apply preference-based scoring
        if context.temporal_preference == "recent":
            # Exponential decay favoring recent memories
            decay_rate = 0.1  # Aggressive decay
            score = math.exp(-decay_rate * time_diff.days / 30)
        elif context.temporal_preference == "historical":
            # Slight preference for older, more established memories
            if time_diff.days > 90:
                score = 0.8 + 0.2 * min(1.0, (time_diff.days - 90) / 365)
            else:
                score = 0.6
        else:  # "any" or None
            # Gentle decay with stabilization
            if time_diff.days <= 7:
                score = 1.0
            elif time_diff.days <= 30:
                score = 0.9
            elif time_diff.days <= 90:
                score = 0.8
            elif time_diff.days <= 365:
                score = 0.6
            else:
                score = 0.4
        
        return score
    
    def _calculate_tag_overlap(self, candidate: MemoryCandidate, 
                             context: ScoringContext) -> float:
        """Calculate tag overlap score"""
        if not context.query_tags or not candidate.tags:
            return 0.0
        
        query_tags_set = set(tag.lower() for tag in context.query_tags)
        candidate_tags_set = set(tag.lower() for tag in candidate.tags)
        
        intersection = query_tags_set.intersection(candidate_tags_set)
        union = query_tags_set.union(candidate_tags_set)
        
        if not union:
            return 0.0
        
        # Jaccard similarity with bias toward precision
        jaccard = len(intersection) / len(union)
        precision = len(intersection) / len(candidate_tags_set) if candidate_tags_set else 0
        
        # Weighted combination favoring precision
        score = 0.7 * jaccard + 0.3 * precision
        
        return score
    
    def _calculate_metadata_match(self, candidate: MemoryCandidate, 
                                context: ScoringContext) -> float:
        """Calculate metadata matching score"""
        if not context.metadata_requirements:
            return 0.5  # Neutral when no requirements
        
        matches = 0
        total_requirements = len(context.metadata_requirements)
        
        for key, expected_value in context.metadata_requirements.items():
            if key in candidate.metadata:
                candidate_value = candidate.metadata[key]
                if isinstance(expected_value, list):
                    if candidate_value in expected_value:
                        matches += 1
                elif candidate_value == expected_value:
                    matches += 1
                elif isinstance(candidate_value, str) and isinstance(expected_value, str):
                    # Fuzzy string matching
                    if expected_value.lower() in candidate_value.lower():
                        matches += 0.7
        
        return matches / total_requirements if total_requirements > 0 else 0.5
    
    def _calculate_content_type_match(self, candidate: MemoryCandidate, 
                                    context: ScoringContext) -> float:
        """Calculate content type matching score"""
        if not context.content_type_preference:
            return 0.5  # Neutral when no preference
        
        content_lower = candidate.content.lower()
        patterns = self.content_type_patterns.get(context.content_type_preference, [])
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                matches += 1
        
        # Normalize by pattern count
        score = min(1.0, matches / len(patterns)) if patterns else 0.0
        
        return score
    
    def _calculate_technology_alignment(self, candidate: MemoryCandidate, 
                                      context: ScoringContext) -> float:
        """Calculate technology alignment score"""
        if not context.target_technologies:
            return 0.5  # Neutral when no specific technologies
        
        content_lower = candidate.content.lower()
        tags_lower = [tag.lower() for tag in candidate.tags]
        
        aligned_techs = 0
        total_target_techs = len(context.target_technologies)
        
        for target_tech in context.target_technologies:
            tech_keywords = self.technology_keywords.get(target_tech.lower(), [target_tech.lower()])
            
            # Check content and tags for technology keywords
            found_in_content = any(keyword in content_lower for keyword in tech_keywords)
            found_in_tags = any(keyword in " ".join(tags_lower) for keyword in tech_keywords)
            
            if found_in_content or found_in_tags:
                aligned_techs += 1
        
        return aligned_techs / total_target_techs if total_target_techs > 0 else 0.5
    
    def _calculate_contextual_similarity(self, candidate: MemoryCandidate, 
                                       context: ScoringContext) -> float:
        """Calculate contextual similarity based on task category and factors"""
        score = 0.5  # Base score
        
        if context.contextual_factors:
            # Task category alignment
            if ContextualFactor.TASK_CATEGORY in context.contextual_factors:
                target_category = context.contextual_factors[ContextualFactor.TASK_CATEGORY]
                if target_category.lower() in candidate.content.lower():
                    score += 0.2
                if target_category.lower() in [tag.lower() for tag in candidate.tags]:
                    score += 0.3
            
            # Error context alignment
            if ContextualFactor.ERROR_CONTEXT in context.contextual_factors:
                error_indicators = ["error", "exception", "fix", "debug", "solution"]
                content_lower = candidate.content.lower()
                if any(indicator in content_lower for indicator in error_indicators):
                    score += 0.3
        
        return min(1.0, score)
    
    def _calculate_usage_frequency(self, candidate: MemoryCandidate, 
                                 context: ScoringContext) -> float:
        """Calculate usage frequency score"""
        if candidate.usage_count <= 0:
            return 0.0
        
        # Logarithmic scaling to prevent over-weighting highly used memories
        normalized_usage = min(1.0, math.log(candidate.usage_count + 1) / math.log(10))
        
        return normalized_usage
    
    def _apply_contextual_adjustments(self, base_score: float, candidate: MemoryCandidate,
                                    context: ScoringContext, boosters: List[str], 
                                    penalties: List[str]) -> Tuple[float, Dict[str, List[str]]]:
        """Apply contextual adjustments to the base score"""
        adjusted_score = base_score
        new_boosters = []
        new_penalties = []
        
        # Recency booster for time-sensitive tasks
        if context.contextual_factors and ContextualFactor.URGENCY_LEVEL in context.contextual_factors:
            urgency = context.contextual_factors[ContextualFactor.URGENCY_LEVEL]
            if urgency == "high":
                time_diff = datetime.now() - candidate.timestamp
                if time_diff.days <= 7:
                    adjusted_score += 0.1
                    new_boosters.append("Recent memory for urgent task")
        
        # Complexity alignment
        if context.contextual_factors and ContextualFactor.COMPLEXITY_LEVEL in context.contextual_factors:
            complexity = context.contextual_factors[ContextualFactor.COMPLEXITY_LEVEL]
            content_indicators = {
                "simple": ["simple", "basic", "easy", "straightforward"],
                "complex": ["complex", "advanced", "sophisticated", "intricate"]
            }
            
            content_lower = candidate.content.lower()
            if complexity in content_indicators:
                if any(indicator in content_lower for indicator in content_indicators[complexity]):
                    adjusted_score += 0.05
                    new_boosters.append(f"Complexity alignment ({complexity})")
        
        # Domain specificity penalty/booster
        if context.contextual_factors and ContextualFactor.DOMAIN_SPECIFICITY in context.contextual_factors:
            domain = context.contextual_factors[ContextualFactor.DOMAIN_SPECIFICITY]
            if domain and domain.lower() not in candidate.content.lower():
                adjusted_score -= 0.05
                new_penalties.append("Domain mismatch")
        
        # Implementation stage alignment
        if context.contextual_factors and ContextualFactor.IMPLEMENTATION_STAGE in context.contextual_factors:
            stage = context.contextual_factors[ContextualFactor.IMPLEMENTATION_STAGE]
            stage_keywords = {
                "planning": ["plan", "design", "architecture", "strategy"],
                "development": ["implement", "code", "build", "develop"],
                "testing": ["test", "verify", "validate", "check"],
                "deployment": ["deploy", "release", "production", "launch"],
                "maintenance": ["maintain", "update", "patch", "fix"]
            }
            
            if stage in stage_keywords:
                content_lower = candidate.content.lower()
                if any(keyword in content_lower for keyword in stage_keywords[stage]):
                    adjusted_score += 0.08
                    new_boosters.append(f"Implementation stage match ({stage})")
        
        return adjusted_score, {"boosters": new_boosters, "penalties": new_penalties}
    
    def _calculate_confidence(self, dimension_scores: Dict[ScoreDimension, float], 
                            total_score: float) -> float:
        """Calculate confidence in the relevance score"""
        
        # High confidence when multiple dimensions agree
        high_scores = sum(1 for score in dimension_scores.values() if score > 0.7)
        low_scores = sum(1 for score in dimension_scores.values() if score < 0.3)
        
        # Base confidence from score distribution
        if high_scores >= 3:
            base_confidence = 0.9
        elif high_scores >= 2:
            base_confidence = 0.8
        elif low_scores >= 4:
            base_confidence = 0.4
        else:
            base_confidence = 0.6
        
        # Adjust for extreme scores
        if total_score > 0.9 or total_score < 0.1:
            base_confidence *= 0.9  # Slightly less confident in extreme scores
        
        return base_confidence
    
    def _generate_reasoning(self, dimension_scores: Dict[ScoreDimension, float],
                          boosters: List[str], penalties: List[str]) -> List[str]:
        """Generate human-readable reasoning for the score"""
        reasoning = []
        
        # Top contributing dimensions
        sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
        top_dimensions = sorted_dimensions[:3]
        
        for dimension, score in top_dimensions:
            if score > 0.6:
                dim_name = dimension.value.replace("_", " ").title()
                reasoning.append(f"{dim_name}: {score:.2f} (strong contribution)")
        
        # Add booster information
        if boosters:
            reasoning.append(f"Positive factors: {', '.join(boosters[:3])}")
        
        # Add penalty information
        if penalties:
            reasoning.append(f"Limiting factors: {', '.join(penalties[:2])}")
        
        return reasoning
    
    def batch_score_candidates(self, candidates: List[MemoryCandidate], 
                             context: ScoringContext,
                             weights: Optional[ScoringWeights] = None) -> List[Tuple[MemoryCandidate, RelevanceScore]]:
        """
        Score multiple candidates and return them sorted by relevance.
        
        Args:
            candidates: List of memory candidates to score
            context: Scoring context
            weights: Optional custom weights
            
        Returns:
            List of (candidate, score) tuples sorted by relevance
        """
        scored_candidates = []
        
        for candidate in candidates:
            score = self.score_relevance(candidate, context, weights)
            scored_candidates.append((candidate, score))
        
        # Sort by total score (descending)
        scored_candidates.sort(key=lambda x: x[1].total_score, reverse=True)
        
        return scored_candidates
    
    def get_optimal_weights_for_context(self, context: ScoringContext) -> ScoringWeights:
        """Get optimal weights based on the scoring context"""
        
        weights = ScoringWeights()
        
        # Adjust weights based on context
        if context.temporal_preference == "recent":
            weights.temporal_relevance = 0.25  # Increased temporal weight
            weights.semantic_similarity = 0.25  # Decreased semantic weight
        
        if context.content_type_preference:
            weights.content_type_match = 0.20  # Increased content type weight
            weights.semantic_similarity = 0.25  # Adjust semantic weight
        
        if context.target_technologies:
            weights.technology_alignment = 0.20  # Increased tech alignment
            weights.tag_overlap = 0.25  # Increased tag weight
        
        if context.contextual_factors and ContextualFactor.ERROR_CONTEXT in context.contextual_factors:
            # For error contexts, prioritize exact solutions
            weights.semantic_similarity = 0.40
            weights.content_type_match = 0.25
            weights.temporal_relevance = 0.10
        
        return weights
    
    def explain_score(self, score: RelevanceScore) -> str:
        """Generate a human-readable explanation of the relevance score"""
        
        explanation_lines = [
            f"**Overall Relevance**: {score.total_score:.2f}/1.0 (Confidence: {score.confidence:.2f})",
            ""
        ]
        
        # Dimension breakdown
        explanation_lines.append("**Score Breakdown**:")
        for dimension, dim_score in sorted(score.dimension_scores.items(), 
                                         key=lambda x: x[1], reverse=True):
            dim_name = dimension.value.replace("_", " ").title()
            explanation_lines.append(f"- {dim_name}: {dim_score:.2f}")
        
        explanation_lines.append("")
        
        # Reasoning
        if score.reasoning:
            explanation_lines.append("**Key Factors**:")
            for reason in score.reasoning:
                explanation_lines.append(f"- {reason}")
            explanation_lines.append("")
        
        # Boosters and penalties
        if score.boosters:
            explanation_lines.append("**Positive Factors**:")
            for booster in score.boosters:
                explanation_lines.append(f"+ {booster}")
            explanation_lines.append("")
        
        if score.penalties:
            explanation_lines.append("**Limiting Factors**:")
            for penalty in score.penalties:
                explanation_lines.append(f"- {penalty}")
        
        return "\n".join(explanation_lines)