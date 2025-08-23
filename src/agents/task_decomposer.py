"""
Task Decomposer

Intelligent task analysis and decomposition for memory context assembly.
Used by the memory-context agent to break down complex tasks and identify
the most relevant types of context needed for successful completion.

The decomposer analyzes task descriptions and provides structured guidance
on what memories to search for and how to prioritize different types of context.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Set, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TaskCategory(Enum):
    """Categories of tasks with different context needs"""
    IMPLEMENTATION = "implementation"
    DEBUGGING = "debugging"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    RESEARCH = "research"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    DEPLOYMENT = "deployment"
    SECURITY = "security"


class ContextType(Enum):
    """Types of context that can be retrieved"""
    TECHNICAL_PATTERNS = "technical_patterns"
    SIMILAR_IMPLEMENTATIONS = "similar_implementations"
    BEST_PRACTICES = "best_practices"
    COMMON_PITFALLS = "common_pitfalls"
    CONFIGURATION_EXAMPLES = "configuration_examples"
    ERROR_SOLUTIONS = "error_solutions"
    TESTING_STRATEGIES = "testing_strategies"
    PERFORMANCE_CONSIDERATIONS = "performance_considerations"
    SECURITY_PRACTICES = "security_practices"
    ARCHITECTURAL_DECISIONS = "architectural_decisions"


class Priority(Enum):
    """Priority levels for context retrieval"""
    CRITICAL = 1  # Essential for task completion
    HIGH = 2      # Very helpful, should be included
    MEDIUM = 3    # Useful background information
    LOW = 4       # Nice to have, optional


@dataclass
class TaskComponent:
    """A decomposed component of a larger task"""
    component: str
    category: TaskCategory
    technologies: Set[str]
    context_needs: List[Tuple[ContextType, Priority]]
    search_terms: List[str]
    estimated_complexity: int  # 1-5 scale


@dataclass
class ContextQuery:
    """A structured query for retrieving specific context"""
    query_text: str
    context_type: ContextType
    priority: Priority
    tags: List[str]
    similarity_threshold: float
    max_results: int


@dataclass
class TaskDecomposition:
    """Complete decomposition of a task with context requirements"""
    original_task: str
    primary_category: TaskCategory
    components: List[TaskComponent]
    context_queries: List[ContextQuery]
    technologies_involved: Set[str]
    estimated_duration: str
    risk_factors: List[str]
    success_criteria: List[str]


class TaskDecomposer:
    """
    Intelligent task decomposition and context requirement analysis.
    
    This class analyzes task descriptions to understand what needs to be done
    and determines what types of context would be most helpful for completion.
    """
    
    def __init__(self):
        self.technology_patterns = self._initialize_technology_patterns()
        self.task_patterns = self._initialize_task_patterns()
        self.context_mappings = self._initialize_context_mappings()
    
    def _initialize_technology_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting technologies mentioned in tasks"""
        return {
            "python": [r"\bpython\b", r"\bpy\b", r"\.py\b", r"\bpip\b", r"\bpytest\b", r"\bdjango\b", r"\bflask\b"],
            "javascript": [r"\bjavascript\b", r"\bjs\b", r"\.js\b", r"\bnode\b", r"\bnpm\b", r"\breact\b", r"\bvue\b"],
            "typescript": [r"\btypescript\b", r"\bts\b", r"\.ts\b", r"\.tsx\b"],
            "docker": [r"\bdocker\b", r"\bcontainer\b", r"\bdockerfile\b", r"\bdocker-compose\b"],
            "kubernetes": [r"\bk8s\b", r"\bkubernetes\b", r"\bkubectl\b", r"\bhelm\b"],
            "database": [r"\bdatabase\b", r"\bdb\b", r"\bsql\b", r"\bpostgres\b", r"\bmysql\b", r"\bmongo\b"],
            "api": [r"\bapi\b", r"\brest\b", r"\bgraphql\b", r"\bendpoint\b", r"\bmicroservice\b"],
            "web": [r"\bweb\b", r"\bhttp\b", r"\bhttps\b", r"\bhtml\b", r"\bcss\b", r"\bfrontend\b"],
            "testing": [r"\btest\b", r"\btesting\b", r"\bunit test\b", r"\bintegration\b", r"\be2e\b"],
            "ci/cd": [r"\bci\b", r"\bcd\b", r"\bjenkins\b", r"\bgithub actions\b", r"\bpipeline\b"],
            "cloud": [r"\baws\b", r"\bazure\b", r"\bgcp\b", r"\bcloud\b", r"\bterraform\b"],
            "security": [r"\bsecurity\b", r"\bauth\b", r"\bssl\b", r"\btls\b", r"\boauth\b", r"\bjwt\b"]
        }
    
    def _initialize_task_patterns(self) -> Dict[TaskCategory, List[str]]:
        """Initialize patterns for categorizing tasks"""
        return {
            TaskCategory.IMPLEMENTATION: [
                r"\bimplement\b", r"\bcreate\b", r"\bbuild\b", r"\bdevelop\b", r"\badd\b",
                r"\bwrite\b", r"\bcode\b", r"\bfeature\b", r"\bfunction\b", r"\bcomponent\b"
            ],
            TaskCategory.DEBUGGING: [
                r"\bdebug\b", r"\bfix\b", r"\berror\b", r"\bbug\b", r"\bissue\b", r"\bproblem\b",
                r"\bbroken\b", r"\bfailing\b", r"\bnot working\b", r"\btroubleshoot\b"
            ],
            TaskCategory.TESTING: [
                r"\btest\b", r"\btesting\b", r"\bunit test\b", r"\bintegration test\b",
                r"\be2e test\b", r"\bspec\b", r"\bverify\b", r"\bvalidate\b"
            ],
            TaskCategory.ARCHITECTURE: [
                r"\barchitecture\b", r"\bdesign\b", r"\bstructure\b", r"\bpattern\b",
                r"\bsystem\b", r"\bmodule\b", r"\bservice\b", r"\bmicroservice\b"
            ],
            TaskCategory.RESEARCH: [
                r"\bresearch\b", r"\binvestigate\b", r"\bexplore\b", r"\banalyze\b",
                r"\bcompare\b", r"\bevaluate\b", r"\bstudy\b", r"\blearn\b"
            ],
            TaskCategory.CONFIGURATION: [
                r"\bconfigure\b", r"\bconfig\b", r"\bsetup\b", r"\binstall\b",
                r"\bdeployment\b", r"\benvironment\b", r"\bsettings\b"
            ],
            TaskCategory.REFACTORING: [
                r"\brefactor\b", r"\bclean up\b", r"\brestructure\b", r"\boptimize\b",
                r"\bimprove\b", r"\bmodernize\b", r"\bupgrade\b"
            ],
            TaskCategory.SECURITY: [
                r"\bsecurity\b", r"\bsecure\b", r"\bauth\b", r"\bpermission\b",
                r"\bvulnerability\b", r"\bencryption\b", r"\bssl\b", r"\btls\b"
            ]
        }
    
    def _initialize_context_mappings(self) -> Dict[TaskCategory, List[Tuple[ContextType, Priority]]]:
        """Initialize mappings between task categories and useful context types"""
        return {
            TaskCategory.IMPLEMENTATION: [
                (ContextType.SIMILAR_IMPLEMENTATIONS, Priority.CRITICAL),
                (ContextType.TECHNICAL_PATTERNS, Priority.HIGH),
                (ContextType.BEST_PRACTICES, Priority.HIGH),
                (ContextType.COMMON_PITFALLS, Priority.MEDIUM),
                (ContextType.PERFORMANCE_CONSIDERATIONS, Priority.MEDIUM)
            ],
            TaskCategory.DEBUGGING: [
                (ContextType.ERROR_SOLUTIONS, Priority.CRITICAL),
                (ContextType.COMMON_PITFALLS, Priority.CRITICAL),
                (ContextType.SIMILAR_IMPLEMENTATIONS, Priority.HIGH),
                (ContextType.TECHNICAL_PATTERNS, Priority.MEDIUM)
            ],
            TaskCategory.TESTING: [
                (ContextType.TESTING_STRATEGIES, Priority.CRITICAL),
                (ContextType.BEST_PRACTICES, Priority.HIGH),
                (ContextType.SIMILAR_IMPLEMENTATIONS, Priority.HIGH),
                (ContextType.COMMON_PITFALLS, Priority.MEDIUM)
            ],
            TaskCategory.ARCHITECTURE: [
                (ContextType.ARCHITECTURAL_DECISIONS, Priority.CRITICAL),
                (ContextType.TECHNICAL_PATTERNS, Priority.CRITICAL),
                (ContextType.BEST_PRACTICES, Priority.HIGH),
                (ContextType.PERFORMANCE_CONSIDERATIONS, Priority.HIGH),
                (ContextType.SECURITY_PRACTICES, Priority.MEDIUM)
            ],
            TaskCategory.CONFIGURATION: [
                (ContextType.CONFIGURATION_EXAMPLES, Priority.CRITICAL),
                (ContextType.BEST_PRACTICES, Priority.HIGH),
                (ContextType.COMMON_PITFALLS, Priority.HIGH),
                (ContextType.SIMILAR_IMPLEMENTATIONS, Priority.MEDIUM)
            ],
            TaskCategory.SECURITY: [
                (ContextType.SECURITY_PRACTICES, Priority.CRITICAL),
                (ContextType.BEST_PRACTICES, Priority.CRITICAL),
                (ContextType.COMMON_PITFALLS, Priority.HIGH),
                (ContextType.SIMILAR_IMPLEMENTATIONS, Priority.MEDIUM)
            ]
        }
    
    def decompose_task(self, task_description: str, metadata: Dict[str, Any] = None) -> TaskDecomposition:
        """
        Decompose a task description into components and context requirements.
        
        This is the main entry point that analyzes a task and determines
        what context would be most helpful for completion.
        """
        logger.info(f"Decomposing task: {task_description[:100]}...")
        
        # Analyze the task
        primary_category = self._categorize_task(task_description)
        technologies = self._extract_technologies(task_description)
        components = self._identify_components(task_description, primary_category, technologies)
        
        # Generate context queries
        context_queries = self._generate_context_queries(
            task_description, primary_category, technologies, components
        )
        
        # Estimate complexity and duration
        estimated_duration = self._estimate_duration(components)
        risk_factors = self._identify_risk_factors(task_description, components)
        success_criteria = self._generate_success_criteria(task_description, components)
        
        decomposition = TaskDecomposition(
            original_task=task_description,
            primary_category=primary_category,
            components=components,
            context_queries=context_queries,
            technologies_involved=technologies,
            estimated_duration=estimated_duration,
            risk_factors=risk_factors,
            success_criteria=success_criteria
        )
        
        logger.info(f"Task decomposed into {len(components)} components with {len(context_queries)} context queries")
        return decomposition
    
    def _categorize_task(self, task_description: str) -> TaskCategory:
        """Categorize the primary type of task"""
        text = task_description.lower()
        category_scores = {}
        
        for category, patterns in self.task_patterns.items():
            score = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in patterns)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return TaskCategory.IMPLEMENTATION  # Default fallback
    
    def _extract_technologies(self, task_description: str) -> Set[str]:
        """Extract technologies mentioned in the task description"""
        text = task_description.lower()
        technologies = set()
        
        for tech, patterns in self.technology_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    technologies.add(tech)
                    break
        
        return technologies
    
    def _identify_components(self, task_description: str, category: TaskCategory, technologies: Set[str]) -> List[TaskComponent]:
        """Identify the key components of the task"""
        # This is a simplified implementation - in practice, this would use
        # more sophisticated NLP techniques to parse the task structure
        
        components = []
        
        # Create a primary component based on the main task
        main_component = TaskComponent(
            component=task_description,
            category=category,
            technologies=technologies,
            context_needs=self.context_mappings.get(category, []),
            search_terms=self._generate_search_terms(task_description, technologies),
            estimated_complexity=self._estimate_complexity(task_description)
        )
        
        components.append(main_component)
        
        # Identify sub-components based on common patterns
        if "and" in task_description.lower():
            # Split on conjunctions to find multiple components
            parts = re.split(r'\band\b', task_description, flags=re.IGNORECASE)
            for part in parts[1:]:  # Skip first part as it's already in main_component
                if len(part.strip()) > 10:  # Only meaningful sub-tasks
                    sub_category = self._categorize_task(part)
                    sub_technologies = self._extract_technologies(part)
                    
                    sub_component = TaskComponent(
                        component=part.strip(),
                        category=sub_category,
                        technologies=sub_technologies,
                        context_needs=self.context_mappings.get(sub_category, []),
                        search_terms=self._generate_search_terms(part, sub_technologies),
                        estimated_complexity=self._estimate_complexity(part)
                    )
                    components.append(sub_component)
        
        return components
    
    def _generate_context_queries(self, task_description: str, category: TaskCategory, 
                                 technologies: Set[str], components: List[TaskComponent]) -> List[ContextQuery]:
        """Generate structured queries for retrieving context"""
        queries = []
        
        # Generate queries based on task category
        category_context = self.context_mappings.get(category, [])
        
        for context_type, priority in category_context:
            query_text = self._build_query_text(task_description, context_type, technologies)
            tags = self._generate_tags(technologies, category, context_type)
            
            query = ContextQuery(
                query_text=query_text,
                context_type=context_type,
                priority=priority,
                tags=tags,
                similarity_threshold=self._get_threshold_for_priority(priority),
                max_results=self._get_max_results_for_priority(priority)
            )
            queries.append(query)
        
        # Sort by priority
        queries.sort(key=lambda q: q.priority.value)
        
        return queries
    
    def _build_query_text(self, task_description: str, context_type: ContextType, technologies: Set[str]) -> str:
        """Build query text optimized for the specific context type"""
        base_terms = self._extract_key_terms(task_description)
        tech_terms = " ".join(technologies) if technologies else ""
        
        context_modifiers = {
            ContextType.SIMILAR_IMPLEMENTATIONS: "implementation example pattern",
            ContextType.BEST_PRACTICES: "best practice recommendation guideline",
            ContextType.COMMON_PITFALLS: "problem pitfall mistake avoid",
            ContextType.ERROR_SOLUTIONS: "error fix solution resolved",
            ContextType.TESTING_STRATEGIES: "test testing strategy approach",
            ContextType.CONFIGURATION_EXAMPLES: "configuration config setup example",
            ContextType.TECHNICAL_PATTERNS: "pattern architecture design approach",
            ContextType.PERFORMANCE_CONSIDERATIONS: "performance optimization scalability",
            ContextType.SECURITY_PRACTICES: "security secure authentication authorization",
            ContextType.ARCHITECTURAL_DECISIONS: "architecture decision design choice"
        }
        
        modifier = context_modifiers.get(context_type, "")
        
        return f"{base_terms} {tech_terms} {modifier}".strip()
    
    def _extract_key_terms(self, text: str) -> str:
        """Extract key terms from text for search queries"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [word for word in words if word not in common_words and len(word) > 2]
        
        return " ".join(key_terms[:10])  # Limit to top 10 terms
    
    def _generate_tags(self, technologies: Set[str], category: TaskCategory, context_type: ContextType) -> List[str]:
        """Generate tags for context queries"""
        tags = list(technologies)
        tags.append(category.value)
        tags.append(context_type.value.replace("_", "-"))
        
        return tags
    
    def _get_threshold_for_priority(self, priority: Priority) -> float:
        """Get similarity threshold based on priority"""
        thresholds = {
            Priority.CRITICAL: 0.3,  # More inclusive for critical context
            Priority.HIGH: 0.4,
            Priority.MEDIUM: 0.5,
            Priority.LOW: 0.6
        }
        return thresholds[priority]
    
    def _get_max_results_for_priority(self, priority: Priority) -> int:
        """Get max results based on priority"""
        max_results = {
            Priority.CRITICAL: 15,
            Priority.HIGH: 10,
            Priority.MEDIUM: 8,
            Priority.LOW: 5
        }
        return max_results[priority]
    
    def _estimate_complexity(self, text: str) -> int:
        """Estimate complexity on a 1-5 scale based on text analysis"""
        complexity_indicators = [
            (r"\bcomplex\b|\badvanced\b|\bsophisticated\b", 2),
            (r"\bmultiple\b|\bseveral\b|\bmany\b", 1),
            (r"\bintegration\b|\bapi\b|\bmicroservice\b", 1),
            (r"\bsecurity\b|\bauth\b|\bencryption\b", 1),
            (r"\bperformance\b|\boptimiz\b|\bscal\b", 1),
            (r"\bdatabase\b|\bdata\b|\bstorage\b", 1),
            (r"\btest\b|\btesting\b", 1)
        ]
        
        base_complexity = 1
        for pattern, weight in complexity_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                base_complexity += weight
        
        return min(5, base_complexity)
    
    def _estimate_duration(self, components: List[TaskComponent]) -> str:
        """Estimate task duration based on components"""
        total_complexity = sum(comp.estimated_complexity for comp in components)
        
        if total_complexity <= 3:
            return "1-2 hours"
        elif total_complexity <= 6:
            return "2-4 hours"
        elif total_complexity <= 10:
            return "4-8 hours"
        elif total_complexity <= 15:
            return "1-2 days"
        else:
            return "2+ days"
    
    def _identify_risk_factors(self, task_description: str, components: List[TaskComponent]) -> List[str]:
        """Identify potential risk factors for the task"""
        risks = []
        text = task_description.lower()
        
        risk_patterns = [
            (r"\bnew\b|\bunfamiliar\b|\bfirst time\b", "Working with unfamiliar technology"),
            (r"\blegacy\b|\bold\b|\bdeprecated\b", "Working with legacy systems"),
            (r"\bmigration\b|\bupgrade\b", "Migration/upgrade complexity"),
            (r"\bintegration\b|\bthird.?party\b", "Third-party integration challenges"),
            (r"\bperformance\b|\bscale\b", "Performance and scalability requirements"),
            (r"\bsecurity\b|\bauth\b", "Security implementation complexity"),
            (r"\bdeadline\b|\burgent\b|\basap\b", "Time pressure"),
            (r"\bmultiple\b.*\bteam\b", "Multi-team coordination required")
        ]
        
        for pattern, risk in risk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                risks.append(risk)
        
        # Add complexity-based risks
        high_complexity_components = [c for c in components if c.estimated_complexity >= 4]
        if high_complexity_components:
            risks.append("High complexity components present")
        
        if len(components) > 3:
            risks.append("Multiple interdependent components")
        
        return risks if risks else ["Low risk task"]
    
    def _generate_success_criteria(self, task_description: str, components: List[TaskComponent]) -> List[str]:
        """Generate success criteria for the task"""
        criteria = []
        
        # Basic completion criteria
        criteria.append("Task implementation completed successfully")
        
        # Component-specific criteria
        for component in components:
            if component.category == TaskCategory.TESTING:
                criteria.append("All tests pass with good coverage")
            elif component.category == TaskCategory.DEBUGGING:
                criteria.append("Original issue resolved and verified")
            elif component.category == TaskCategory.SECURITY:
                criteria.append("Security requirements met and verified")
            elif component.category == TaskCategory.PERFORMANCE:
                criteria.append("Performance requirements met")
        
        # Technology-specific criteria
        for tech in set().union(*[c.technologies for c in components]):
            if tech == "testing":
                criteria.append("Test suite runs successfully")
            elif tech == "database":
                criteria.append("Database operations work correctly")
            elif tech == "api":
                criteria.append("API endpoints respond correctly")
        
        # General quality criteria
        criteria.extend([
            "Code follows project conventions and standards",
            "Documentation updated as needed",
            "No regressions in existing functionality"
        ])
        
        return list(set(criteria))  # Remove duplicates
    
    def get_decomposition_summary(self, decomposition: TaskDecomposition) -> Dict[str, Any]:
        """Get a summary of the task decomposition for reporting"""
        return {
            "task": decomposition.original_task,
            "category": decomposition.primary_category.value,
            "technologies": list(decomposition.technologies_involved),
            "components_count": len(decomposition.components),
            "context_queries_count": len(decomposition.context_queries),
            "estimated_duration": decomposition.estimated_duration,
            "complexity_score": sum(c.estimated_complexity for c in decomposition.components),
            "risk_factors_count": len(decomposition.risk_factors),
            "high_priority_queries": len([q for q in decomposition.context_queries if q.priority in [Priority.CRITICAL, Priority.HIGH]])
        }