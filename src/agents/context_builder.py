"""
Context Builder

Intelligent context assembly from multiple memory sources.
Used by the memory-context agent to build comprehensive context packages
that provide optimal information for task completion.

The context builder takes task decompositions and assembles contextual
information from various memory searches, organizing it into a coherent
and useful format for the user.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set, Optional, Tuple
from enum import Enum

from .task_decomposer import TaskDecomposition, ContextQuery, Priority, ContextType

logger = logging.getLogger(__name__)


class ContextSectionType(Enum):
    """Sections of assembled context"""
    OVERVIEW = "overview"
    SIMILAR_IMPLEMENTATIONS = "similar_implementations"  
    BEST_PRACTICES = "best_practices"
    COMMON_PITFALLS = "common_pitfalls"
    TECHNICAL_PATTERNS = "technical_patterns"
    ERROR_SOLUTIONS = "error_solutions"
    TESTING_STRATEGIES = "testing_strategies"
    CONFIGURATION_EXAMPLES = "configuration_examples"
    PERFORMANCE_CONSIDERATIONS = "performance_considerations"
    SECURITY_PRACTICES = "security_practices"
    ARCHITECTURAL_DECISIONS = "architectural_decisions"
    RECENT_RELATED_WORK = "recent_related_work"


@dataclass
class ContextItem:
    """A single piece of contextual information"""
    content: str
    source_hash: str
    relevance_score: float
    context_type: ContextType
    tags: List[str]
    timestamp: datetime
    memory_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextSection:
    """A section of assembled context with related items"""
    section_type: ContextSectionType
    title: str
    items: List[ContextItem]
    priority: Priority
    summary: Optional[str] = None


@dataclass
class AssembledContext:
    """Complete assembled context for a task"""
    task_description: str
    decomposition_summary: Dict[str, Any]
    sections: List[ContextSection]
    total_items: int
    assembly_metadata: Dict[str, Any]
    created_at: datetime
    estimated_relevance: float


class ContextBuilder:
    """
    Intelligent context assembly and organization.
    
    Takes task decompositions and memory search results, then assembles
    them into comprehensive, well-organized context packages.
    """
    
    def __init__(self):
        self.context_type_mappings = self._initialize_context_mappings()
        self.section_priorities = self._initialize_section_priorities()
        
    def _initialize_context_mappings(self) -> Dict[ContextType, ContextSectionType]:
        """Map context types to sections"""
        return {
            ContextType.SIMILAR_IMPLEMENTATIONS: ContextSectionType.SIMILAR_IMPLEMENTATIONS,
            ContextType.BEST_PRACTICES: ContextSectionType.BEST_PRACTICES,
            ContextType.COMMON_PITFALLS: ContextSectionType.COMMON_PITFALLS,
            ContextType.TECHNICAL_PATTERNS: ContextSectionType.TECHNICAL_PATTERNS,
            ContextType.ERROR_SOLUTIONS: ContextSectionType.ERROR_SOLUTIONS,
            ContextType.TESTING_STRATEGIES: ContextSectionType.TESTING_STRATEGIES,
            ContextType.CONFIGURATION_EXAMPLES: ContextSectionType.CONFIGURATION_EXAMPLES,
            ContextType.PERFORMANCE_CONSIDERATIONS: ContextSectionType.PERFORMANCE_CONSIDERATIONS,
            ContextType.SECURITY_PRACTICES: ContextSectionType.SECURITY_PRACTICES,
            ContextType.ARCHITECTURAL_DECISIONS: ContextSectionType.ARCHITECTURAL_DECISIONS
        }
    
    def _initialize_section_priorities(self) -> Dict[ContextSectionType, Priority]:
        """Define default priorities for each section type"""
        return {
            ContextSectionType.OVERVIEW: Priority.CRITICAL,
            ContextSectionType.SIMILAR_IMPLEMENTATIONS: Priority.CRITICAL,
            ContextSectionType.BEST_PRACTICES: Priority.HIGH,
            ContextSectionType.TECHNICAL_PATTERNS: Priority.HIGH,
            ContextSectionType.COMMON_PITFALLS: Priority.HIGH,
            ContextSectionType.ERROR_SOLUTIONS: Priority.HIGH,
            ContextSectionType.TESTING_STRATEGIES: Priority.MEDIUM,
            ContextSectionType.CONFIGURATION_EXAMPLES: Priority.MEDIUM,
            ContextSectionType.PERFORMANCE_CONSIDERATIONS: Priority.MEDIUM,
            ContextSectionType.SECURITY_PRACTICES: Priority.MEDIUM,
            ContextSectionType.ARCHITECTURAL_DECISIONS: Priority.MEDIUM,
            ContextSectionType.RECENT_RELATED_WORK: Priority.LOW
        }
    
    async def assemble_context(self, decomposition: TaskDecomposition, 
                              memory_results: Dict[str, List[Dict[str, Any]]]) -> AssembledContext:
        """
        Assemble comprehensive context from task decomposition and memory results.
        
        Args:
            decomposition: Task decomposition with context requirements
            memory_results: Results from memory searches, keyed by query identifier
            
        Returns:
            AssembledContext with organized, prioritized contextual information
        """
        logger.info(f"Assembling context for task: {decomposition.original_task[:100]}...")
        
        start_time = datetime.now()
        
        # Parse and organize memory results
        context_items = await self._parse_memory_results(memory_results, decomposition)
        
        # Group items by context type/section
        sections_data = self._group_items_by_section(context_items)
        
        # Create organized sections
        sections = await self._create_context_sections(sections_data, decomposition)
        
        # Add overview and recent work sections
        sections = await self._add_special_sections(sections, context_items, decomposition)
        
        # Sort sections by priority
        sections.sort(key=lambda s: s.priority.value)
        
        # Calculate overall relevance
        overall_relevance = self._calculate_overall_relevance(context_items)
        
        # Create assembly metadata
        assembly_metadata = {
            "assembly_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
            "total_memory_results": sum(len(results) for results in memory_results.values()),
            "sections_created": len(sections),
            "highest_relevance": max([item.relevance_score for item in context_items], default=0),
            "technologies_covered": list(decomposition.technologies_involved),
            "context_types_found": list(set(item.context_type.value for item in context_items))
        }
        
        assembled_context = AssembledContext(
            task_description=decomposition.original_task,
            decomposition_summary={
                "category": decomposition.primary_category.value,
                "technologies": list(decomposition.technologies_involved),
                "components_count": len(decomposition.components),
                "estimated_duration": decomposition.estimated_duration,
                "risk_factors": decomposition.risk_factors
            },
            sections=sections,
            total_items=len(context_items),
            assembly_metadata=assembly_metadata,
            created_at=datetime.now(),
            estimated_relevance=overall_relevance
        )
        
        logger.info(f"Context assembled: {len(sections)} sections, {len(context_items)} items, {overall_relevance:.2f} relevance")
        return assembled_context
    
    async def _parse_memory_results(self, memory_results: Dict[str, List[Dict[str, Any]]], 
                                   decomposition: TaskDecomposition) -> List[ContextItem]:
        """Parse raw memory results into structured context items"""
        context_items = []
        
        for query_id, results in memory_results.items():
            # Find the corresponding context query
            context_query = self._find_context_query(query_id, decomposition.context_queries)
            
            if not context_query:
                logger.warning(f"Could not find context query for {query_id}")
                continue
            
            for result in results:
                try:
                    # Extract memory data (assuming standard memory service format)
                    content = result.get("content", "")
                    metadata = result.get("metadata", {})
                    tags = result.get("tags", [])
                    timestamp_str = result.get("timestamp", result.get("created_at", ""))
                    
                    # Parse timestamp
                    timestamp = self._parse_timestamp(timestamp_str)
                    
                    # Calculate relevance score (would be enhanced with actual scoring)
                    relevance_score = result.get("score", result.get("similarity", 0.5))
                    
                    context_item = ContextItem(
                        content=content,
                        source_hash=result.get("hash", result.get("id", "")),
                        relevance_score=float(relevance_score),
                        context_type=context_query.context_type,
                        tags=tags,
                        timestamp=timestamp,
                        memory_metadata=metadata
                    )
                    
                    context_items.append(context_item)
                    
                except Exception as e:
                    logger.error(f"Error parsing memory result: {e}")
                    continue
        
        # Sort by relevance
        context_items.sort(key=lambda x: x.relevance_score, reverse=True)
        return context_items
    
    def _find_context_query(self, query_id: str, context_queries: List[ContextQuery]) -> Optional[ContextQuery]:
        """Find the context query that corresponds to a query ID"""
        # This is simplified - in practice, query_id would be tracked through the search process
        try:
            query_index = int(query_id.split("_")[-1]) if "_" in query_id else int(query_id)
            if 0 <= query_index < len(context_queries):
                return context_queries[query_index]
        except (ValueError, IndexError):
            pass
        
        # Fallback: find by content match or return first query
        return context_queries[0] if context_queries else None
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string into datetime object"""
        if not timestamp_str:
            return datetime.now()
        
        try:
            # Try common formats
            for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(timestamp_str[:19], fmt)
                except ValueError:
                    continue
            
            # Fallback
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def _group_items_by_section(self, context_items: List[ContextItem]) -> Dict[ContextSectionType, List[ContextItem]]:
        """Group context items by their section type"""
        sections_data = {}
        
        for item in context_items:
            section_type = self.context_type_mappings.get(item.context_type)
            
            if section_type:
                if section_type not in sections_data:
                    sections_data[section_type] = []
                sections_data[section_type].append(item)
        
        return sections_data
    
    async def _create_context_sections(self, sections_data: Dict[ContextSectionType, List[ContextItem]], 
                                      decomposition: TaskDecomposition) -> List[ContextSection]:
        """Create organized context sections from grouped items"""
        sections = []
        
        section_titles = {
            ContextSectionType.SIMILAR_IMPLEMENTATIONS: "🔍 Similar Implementations",
            ContextSectionType.BEST_PRACTICES: "✅ Best Practices",
            ContextSectionType.COMMON_PITFALLS: "⚠️ Common Pitfalls to Avoid",
            ContextSectionType.TECHNICAL_PATTERNS: "🏗️ Technical Patterns",
            ContextSectionType.ERROR_SOLUTIONS: "🔧 Error Solutions",
            ContextSectionType.TESTING_STRATEGIES: "🧪 Testing Strategies",
            ContextSectionType.CONFIGURATION_EXAMPLES: "⚙️ Configuration Examples",
            ContextSectionType.PERFORMANCE_CONSIDERATIONS: "⚡ Performance Considerations",
            ContextSectionType.SECURITY_PRACTICES: "🔒 Security Practices",
            ContextSectionType.ARCHITECTURAL_DECISIONS: "🏛️ Architectural Decisions"
        }
        
        for section_type, items in sections_data.items():
            if not items:
                continue
            
            # Limit items per section and sort by relevance
            items.sort(key=lambda x: x.relevance_score, reverse=True)
            max_items = self._get_max_items_for_section(section_type)
            limited_items = items[:max_items]
            
            # Create section
            section = ContextSection(
                section_type=section_type,
                title=section_titles.get(section_type, section_type.value.replace("_", " ").title()),
                items=limited_items,
                priority=self.section_priorities.get(section_type, Priority.MEDIUM),
                summary=await self._generate_section_summary(section_type, limited_items)
            )
            
            sections.append(section)
        
        return sections
    
    def _get_max_items_for_section(self, section_type: ContextSectionType) -> int:
        """Get maximum number of items to include in each section"""
        limits = {
            ContextSectionType.SIMILAR_IMPLEMENTATIONS: 8,
            ContextSectionType.BEST_PRACTICES: 6,
            ContextSectionType.COMMON_PITFALLS: 5,
            ContextSectionType.TECHNICAL_PATTERNS: 6,
            ContextSectionType.ERROR_SOLUTIONS: 8,
            ContextSectionType.TESTING_STRATEGIES: 5,
            ContextSectionType.CONFIGURATION_EXAMPLES: 4,
            ContextSectionType.PERFORMANCE_CONSIDERATIONS: 4,
            ContextSectionType.SECURITY_PRACTICES: 4,
            ContextSectionType.ARCHITECTURAL_DECISIONS: 5
        }
        return limits.get(section_type, 5)
    
    async def _generate_section_summary(self, section_type: ContextSectionType, 
                                       items: List[ContextItem]) -> Optional[str]:
        """Generate a summary for a context section"""
        if not items:
            return None
        
        # Get common themes from the items
        all_tags = []
        high_relevance_items = [item for item in items if item.relevance_score > 0.6]
        
        for item in items:
            all_tags.extend(item.tags)
        
        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create summary based on section type
        summaries = {
            ContextSectionType.SIMILAR_IMPLEMENTATIONS: f"Found {len(items)} similar implementations, focusing on {', '.join([tag for tag, _ in common_tags])}",
            ContextSectionType.BEST_PRACTICES: f"{len(items)} best practices identified, with {len(high_relevance_items)} highly relevant recommendations",
            ContextSectionType.COMMON_PITFALLS: f"{len(items)} potential pitfalls to avoid, particularly around {', '.join([tag for tag, _ in common_tags[:2]])}",
            ContextSectionType.ERROR_SOLUTIONS: f"{len(items)} error solutions found with {len(high_relevance_items)} highly relevant fixes",
            ContextSectionType.TESTING_STRATEGIES: f"{len(items)} testing approaches covering {', '.join([tag for tag, _ in common_tags[:2]])}"
        }
        
        return summaries.get(section_type, f"{len(items)} relevant items found")
    
    async def _add_special_sections(self, sections: List[ContextSection], 
                                   context_items: List[ContextItem],
                                   decomposition: TaskDecomposition) -> List[ContextSection]:
        """Add special sections like overview and recent work"""
        
        # Add overview section
        overview_section = await self._create_overview_section(context_items, decomposition)
        sections.insert(0, overview_section)
        
        # Add recent related work section
        recent_items = [item for item in context_items 
                       if item.timestamp > datetime.now() - timedelta(days=30)]
        
        if recent_items:
            recent_section = ContextSection(
                section_type=ContextSectionType.RECENT_RELATED_WORK,
                title="📅 Recent Related Work",
                items=recent_items[:5],  # Limit to 5 most recent
                priority=Priority.LOW,
                summary=f"Recent work from the last 30 days ({len(recent_items)} items found)"
            )
            sections.append(recent_section)
        
        return sections
    
    async def _create_overview_section(self, context_items: List[ContextItem], 
                                      decomposition: TaskDecomposition) -> ContextSection:
        """Create an overview section summarizing the context"""
        
        # Create synthetic overview item
        total_items = len(context_items)
        avg_relevance = sum(item.relevance_score for item in context_items) / max(len(context_items), 1)
        technologies = decomposition.technologies_involved
        
        overview_content = f"""
# Context Overview

**Task**: {decomposition.original_task}

**Summary**: Found {total_items} relevant memories with average relevance of {avg_relevance:.2f}

**Technologies Involved**: {', '.join(technologies) if technologies else 'General development'}

**Task Complexity**: {decomposition.estimated_duration}

**Key Areas Covered**:
{self._generate_coverage_summary(context_items)}

**Risk Factors**: {', '.join(decomposition.risk_factors)}
        """.strip()
        
        overview_item = ContextItem(
            content=overview_content,
            source_hash="overview_generated",
            relevance_score=1.0,
            context_type=ContextType.TECHNICAL_PATTERNS,  # Arbitrary assignment
            tags=list(technologies) + [decomposition.primary_category.value],
            timestamp=datetime.now(),
            memory_metadata={"generated": True, "type": "overview"}
        )
        
        return ContextSection(
            section_type=ContextSectionType.OVERVIEW,
            title="📋 Task Context Overview",
            items=[overview_item],
            priority=Priority.CRITICAL,
            summary="Generated overview of available context"
        )
    
    def _generate_coverage_summary(self, context_items: List[ContextItem]) -> str:
        """Generate a summary of what areas are covered by the context"""
        context_type_counts = {}
        for item in context_items:
            context_type = item.context_type.value.replace("_", " ").title()
            context_type_counts[context_type] = context_type_counts.get(context_type, 0) + 1
        
        coverage_lines = []
        for context_type, count in sorted(context_type_counts.items(), key=lambda x: x[1], reverse=True):
            coverage_lines.append(f"- {context_type}: {count} items")
        
        return "\n".join(coverage_lines[:6])  # Top 6 areas
    
    def _calculate_overall_relevance(self, context_items: List[ContextItem]) -> float:
        """Calculate overall relevance score for the assembled context"""
        if not context_items:
            return 0.0
        
        # Weight by position (higher relevance items are sorted first)
        weighted_scores = []
        for i, item in enumerate(context_items[:20]):  # Consider top 20 items
            position_weight = 1.0 - (i * 0.05)  # Decrease weight by position
            weighted_scores.append(item.relevance_score * max(0.1, position_weight))
        
        return sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
    
    def format_context_for_display(self, assembled_context: AssembledContext) -> str:
        """Format assembled context for display to the user"""
        
        output_lines = [
            f"# Context for: {assembled_context.task_description}",
            "",
            f"**Assembled**: {assembled_context.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Relevance Score**: {assembled_context.estimated_relevance:.2f}/1.0",
            f"**Total Context Items**: {assembled_context.total_items}",
            ""
        ]
        
        # Add each section
        for section in assembled_context.sections:
            output_lines.extend([
                f"## {section.title}",
                ""
            ])
            
            if section.summary:
                output_lines.extend([
                    f"*{section.summary}*",
                    ""
                ])
            
            for i, item in enumerate(section.items[:5]):  # Limit display items
                output_lines.extend([
                    f"### {i+1}. Relevance: {item.relevance_score:.2f}",
                    "",
                    item.content,
                    "",
                    f"**Tags**: {', '.join(item.tags)}",
                    f"**Source**: {item.source_hash[:8]}...",
                    ""
                ])
            
            if len(section.items) > 5:
                output_lines.append(f"*({len(section.items) - 5} more items available)*")
                output_lines.append("")
        
        # Add metadata
        metadata = assembled_context.assembly_metadata
        output_lines.extend([
            "---",
            "## Assembly Metadata",
            "",
            f"- **Assembly Time**: {metadata.get('assembly_time_ms', 0):.0f}ms",
            f"- **Memory Results Processed**: {metadata.get('total_memory_results', 0)}",
            f"- **Technologies**: {', '.join(metadata.get('technologies_covered', []))}",
            f"- **Context Types**: {', '.join(metadata.get('context_types_found', []))}",
            ""
        ])
        
        return "\n".join(output_lines)
    
    def get_context_statistics(self, assembled_context: AssembledContext) -> Dict[str, Any]:
        """Get statistics about the assembled context"""
        
        section_stats = {}
        for section in assembled_context.sections:
            section_stats[section.section_type.value] = {
                "items_count": len(section.items),
                "avg_relevance": sum(item.relevance_score for item in section.items) / len(section.items),
                "priority": section.priority.value
            }
        
        return {
            "overview": {
                "total_items": assembled_context.total_items,
                "total_sections": len(assembled_context.sections),
                "overall_relevance": assembled_context.estimated_relevance,
                "assembly_time_ms": assembled_context.assembly_metadata.get("assembly_time_ms", 0)
            },
            "sections": section_stats,
            "technologies": assembled_context.decomposition_summary.get("technologies", []),
            "estimated_duration": assembled_context.decomposition_summary.get("estimated_duration", "Unknown")
        }