"""
Agent Integration

Integration layer between the agent system and the MCP Memory Service.
Provides the actual implementation that connects agent orchestration
with memory operations and Claude Code sub-agent invocation.

This module bridges the gap between the agent system's decision-making
and the actual execution of memory operations.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..mcp_memory_service.models.memory import Memory, MemoryMetadata
from ..mcp_memory_service.storage.base import BaseStorageBackend
from .orchestrator import AgentOrchestrator, orchestrator
from .task_decomposer import TaskDecomposer
from .context_builder import ContextBuilder
from .relevance_scorer import RelevanceScorer

logger = logging.getLogger(__name__)


class AgentMemoryIntegration:
    """
    Integration layer between agents and memory service.
    
    Provides the concrete implementation that enables agents to actually
    store and retrieve memories through the MCP Memory Service.
    """
    
    def __init__(self, storage_backend: BaseStorageBackend):
        self.storage = storage_backend
        self.orchestrator = orchestrator
        self.task_decomposer = TaskDecomposer()
        self.context_builder = ContextBuilder()
        self.relevance_scorer = RelevanceScorer()
        
    async def autonomous_store_memory(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Autonomously store memory with agent decision-making.
        
        The agent system analyzes the content and decides whether it should be stored,
        what tags to apply, and how to categorize it.
        """
        try:
            # Let the orchestrator analyze if this should be stored
            analysis = await self.orchestrator.analyze_context(content, metadata)
            
            # Check if the orchestrator recommends storage
            storage_invocations = [inv for inv in analysis if inv.agent_type.value == "memory-store"]
            
            if not storage_invocations:
                return {
                    "stored": False,
                    "reason": "Agent analysis determined storage not necessary",
                    "analysis": f"Analyzed {len(analysis)} potential actions"
                }
            
            # Extract storage context from the invocation
            storage_context = storage_invocations[0].context
            
            # Enhance metadata with agent insights
            enhanced_metadata = metadata or {}
            enhanced_metadata.update({
                "agent_analyzed": True,
                "agent_trigger": storage_invocations[0].trigger.value,
                "storage_reason": storage_context.get("reason", "Agent decision"),
                "autonomous_storage": True,
                "analysis_timestamp": datetime.now().isoformat()
            })
            
            # Automatically generate tags if not provided
            if "tags" not in storage_context:
                auto_tags = await self._generate_smart_tags(content, enhanced_metadata)
                storage_context["tags"] = auto_tags
            
            # Store the memory
            memory = Memory(
                content=content,
                tags=storage_context.get("tags", []),
                metadata=MemoryMetadata(**enhanced_metadata),
                timestamp=datetime.now()
            )
            
            stored_hash = await self.storage.store_memory(memory)
            
            logger.info(f"Agent-driven memory storage: {stored_hash}")
            
            return {
                "stored": True,
                "hash": stored_hash,
                "reason": enhanced_metadata["storage_reason"],
                "tags": storage_context.get("tags", []),
                "agent_analysis": f"Triggered by {storage_invocations[0].trigger.value}"
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous memory storage: {e}")
            return {
                "stored": False,
                "error": str(e),
                "reason": "Storage error encountered"
            }
    
    async def autonomous_retrieve_context(self, query: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Autonomously retrieve and assemble context for a query.
        
        Uses the full agent system pipeline: task decomposition, memory search,
        relevance scoring, and context assembly.
        """
        try:
            # Decompose the query/task
            decomposition = self.task_decomposer.decompose_task(query, metadata)
            
            logger.info(f"Task decomposed into {len(decomposition.components)} components")
            
            # Execute context queries
            memory_results = {}
            for i, context_query in enumerate(decomposition.context_queries):
                query_id = f"query_{i}"
                
                # Search memories using the context query
                search_results = await self._execute_memory_search(context_query)
                memory_results[query_id] = search_results
            
            # Assemble comprehensive context
            assembled_context = await self.context_builder.assemble_context(
                decomposition, memory_results
            )
            
            # Format for return
            formatted_context = self.context_builder.format_context_for_display(assembled_context)
            
            logger.info(f"Context assembled: {assembled_context.total_items} items, {assembled_context.estimated_relevance:.2f} relevance")
            
            return {
                "success": True,
                "context": formatted_context,
                "statistics": self.context_builder.get_context_statistics(assembled_context),
                "decomposition_summary": assembled_context.decomposition_summary,
                "total_items": assembled_context.total_items,
                "relevance_score": assembled_context.estimated_relevance
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous context retrieval: {e}")
            return {
                "success": False,
                "error": str(e),
                "context": f"Error retrieving context for: {query}"
            }
    
    async def _execute_memory_search(self, context_query) -> List[Dict[str, Any]]:
        """Execute a memory search based on a context query"""
        try:
            # Use semantic search
            memories = await self.storage.search_memories(
                query=context_query.query_text,
                limit=context_query.max_results,
                similarity_threshold=context_query.similarity_threshold
            )
            
            # Convert Memory objects to dicts for processing
            results = []
            for memory in memories:
                memory_dict = {
                    "content": memory.content,
                    "tags": memory.tags,
                    "metadata": memory.metadata.__dict__ if memory.metadata else {},
                    "timestamp": memory.timestamp.isoformat() if memory.timestamp else "",
                    "hash": getattr(memory, 'hash', ''),
                    "score": getattr(memory, 'similarity_score', 0.5)  # Default similarity
                }
                results.append(memory_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing memory search: {e}")
            return []
    
    async def _generate_smart_tags(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Generate smart tags based on content analysis"""
        tags = []
        content_lower = content.lower()
        
        # Technology detection
        tech_keywords = {
            "python": ["python", "py", "pip", "pytest", "django", "flask"],
            "javascript": ["javascript", "js", "node", "npm", "react", "vue"],
            "docker": ["docker", "container", "dockerfile"],
            "database": ["database", "db", "sql", "postgres", "mysql"],
            "api": ["api", "rest", "endpoint", "microservice"],
            "testing": ["test", "testing", "unit", "integration"],
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tech)
        
        # Content type detection
        if any(word in content_lower for word in ["decided", "chosen", "solution"]):
            tags.append("decision")
        if any(word in content_lower for word in ["error", "bug", "fix", "debug"]):
            tags.append("bug-fix")
        if any(word in content_lower for word in ["implement", "create", "build"]):
            tags.append("implementation")
        if any(word in content_lower for word in ["config", "setup", "install"]):
            tags.append("configuration")
        
        # Add metadata-based tags
        if metadata:
            if "project" in metadata:
                tags.append(f"project-{metadata['project']}")
            if "category" in metadata:
                tags.append(metadata["category"])
        
        # Agent-specific tags
        tags.extend(["agent-stored", "autonomous"])
        
        # Remove duplicates and return
        return list(set(tags))
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the agent system"""
        orchestrator_status = self.orchestrator.get_agent_status()
        
        return {
            "orchestrator": orchestrator_status,
            "components": {
                "task_decomposer": "active",
                "context_builder": "active", 
                "relevance_scorer": "active"
            },
            "integration": {
                "storage_backend": type(self.storage).__name__,
                "storage_connected": hasattr(self.storage, 'client'),
                "autonomous_mode": "enabled"
            },
            "capabilities": [
                "autonomous_memory_storage",
                "intelligent_context_assembly",
                "task_decomposition",
                "multi_dimensional_relevance_scoring",
                "sub_agent_coordination"
            ]
        }


# Global integration instance (will be initialized with storage backend)
_agent_integration: Optional[AgentMemoryIntegration] = None


def initialize_agent_integration(storage_backend: BaseStorageBackend) -> AgentMemoryIntegration:
    """Initialize the global agent integration instance"""
    global _agent_integration
    _agent_integration = AgentMemoryIntegration(storage_backend)
    logger.info("Agent integration initialized")
    return _agent_integration


def get_agent_integration() -> Optional[AgentMemoryIntegration]:
    """Get the global agent integration instance"""
    return _agent_integration


# Convenience functions for external use
async def autonomous_store_memory(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Convenience function for autonomous memory storage"""
    integration = get_agent_integration()
    if not integration:
        raise RuntimeError("Agent integration not initialized. Call initialize_agent_integration() first.")
    
    return await integration.autonomous_store_memory(content, metadata)


async def autonomous_retrieve_context(query: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Convenience function for autonomous context retrieval"""
    integration = get_agent_integration()
    if not integration:
        raise RuntimeError("Agent integration not initialized. Call initialize_agent_integration() first.")
    
    return await integration.autonomous_retrieve_context(query, metadata)


async def get_agent_status() -> Dict[str, Any]:
    """Convenience function for getting agent status"""
    integration = get_agent_integration()
    if not integration:
        return {"status": "not_initialized", "error": "Agent integration not initialized"}
    
    return await integration.get_agent_status()