"""
Agent System

Autonomous agent orchestration for intelligent memory operations.

This module provides the infrastructure for Claude to autonomously decide
when to store, retrieve, or search memories using specialized sub-agents.

Key Components:
- AgentOrchestrator: Coordinates between sub-agents
- TaskDecomposer: Breaks down complex tasks for context assembly
- ContextBuilder: Assembles comprehensive context from multiple sources
- RelevanceScorer: Multi-dimensional relevance scoring for search results

Usage:
    from src.agents import autonomous_store_decision, autonomous_get_context
    
    # Autonomous decision storage
    result = await autonomous_store_decision("We decided to use PostgreSQL for the database")
    
    # Autonomous context gathering
    context = await autonomous_get_context("Create unit tests for user authentication")
"""

from .orchestrator import (
    AgentOrchestrator,
    AgentType,
    TriggerCondition,
    autonomous_store_decision,
    autonomous_get_context,
    autonomous_debug_support,
    orchestrator
)

from .task_decomposer import (
    TaskDecomposer,
    TaskCategory,
    ContextType,
    Priority,
    TaskDecomposition,
    ContextQuery
)

from .context_builder import (
    ContextBuilder,
    ContextSection,
    ContextSectionType,
    ContextItem,
    AssembledContext
)

from .relevance_scorer import (
    RelevanceScorer,
    ScoreDimension,
    ScoringWeights,
    ScoringContext,
    MemoryCandidate,
    RelevanceScore
)

from .integration import (
    AgentMemoryIntegration,
    initialize_agent_integration,
    get_agent_integration,
    autonomous_store_memory,
    autonomous_retrieve_context,
    get_agent_status
)

from .server_integration import (
    AgentEnabledMemoryServer,
    AgentMiddleware,
    create_agent_enabled_server,
    add_agent_middleware,
    initialize_agent_server
)

__all__ = [
    # Orchestrator
    "AgentOrchestrator",
    "AgentType", 
    "TriggerCondition",
    "autonomous_store_decision",
    "autonomous_get_context",
    "autonomous_debug_support",
    "orchestrator",
    
    # Task Decomposer
    "TaskDecomposer",
    "TaskCategory",
    "ContextType", 
    "Priority",
    "TaskDecomposition",
    "ContextQuery",
    
    # Context Builder
    "ContextBuilder",
    "ContextSection",
    "ContextSectionType",
    "ContextItem",
    "AssembledContext",
    
    # Relevance Scorer
    "RelevanceScorer",
    "ScoreDimension",
    "ScoringWeights",
    "ScoringContext",
    "MemoryCandidate",
    "RelevanceScore",
    
    # Integration
    "AgentMemoryIntegration",
    "initialize_agent_integration",
    "get_agent_integration",
    "autonomous_store_memory",
    "autonomous_retrieve_context",
    "get_agent_status",
    
    # Server Integration
    "AgentEnabledMemoryServer",
    "AgentMiddleware",
    "create_agent_enabled_server",
    "add_agent_middleware",
    "initialize_agent_server"
]