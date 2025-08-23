"""
Server Integration

Integration of the agent system with the MCP Memory Service server.
This module provides the hooks and extensions needed to enable autonomous
agent operations within the existing MCP server infrastructure.

This enables the MCP server to use the agent system for intelligent
memory operations and autonomous decision-making.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from ..mcp_memory_service.server import MemoryServer
from ..mcp_memory_service.storage.base import BaseStorageBackend
from .integration import initialize_agent_integration, get_agent_integration

logger = logging.getLogger(__name__)


class AgentEnabledMemoryServer(MemoryServer):
    """
    Extended MCP Memory Server with autonomous agent capabilities.
    
    This server extends the base MemoryServer to include agent-driven
    autonomous operations while maintaining full backward compatibility.
    """
    
    def __init__(self, storage_backend: BaseStorageBackend):
        super().__init__(storage_backend)
        self.agent_integration = None
        self.agent_enabled = False
        
    async def initialize(self):
        """Initialize the server with agent system integration"""
        await super().initialize()
        
        try:
            # Initialize the agent integration
            self.agent_integration = initialize_agent_integration(self.storage)
            self.agent_enabled = True
            logger.info("Agent system integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent system: {e}")
            logger.info("Server will continue without agent capabilities")
            self.agent_enabled = False
    
    async def store_memory_with_agent_analysis(self, content: str, tags: list = None, 
                                             metadata: dict = None) -> dict:
        """
        Store memory with optional agent analysis.
        
        This method first lets the agent system analyze whether the content
        should be stored, and can enhance tags and metadata based on the analysis.
        """
        if not self.agent_enabled:
            # Fallback to standard storage
            return await self.store_memory_handler(content, tags or [], metadata or {})
        
        try:
            # Let agents analyze and potentially store
            agent_result = await self.agent_integration.autonomous_store_memory(
                content, 
                metadata or {}
            )
            
            if agent_result["stored"]:
                return {
                    "success": True,
                    "hash": agent_result["hash"],
                    "message": f"Stored with agent analysis: {agent_result['reason']}",
                    "agent_enhanced": True,
                    "agent_tags": agent_result["tags"],
                    "original_tags": tags or [],
                    "storage_trigger": agent_result.get("agent_analysis", "autonomous")
                }
            else:
                # Agent decided not to store, but allow manual override
                if tags or (metadata and metadata.get("force_store")):
                    # User explicitly provided tags or forced storage
                    result = await self.store_memory_handler(content, tags or [], metadata or {})
                    result["agent_analysis"] = agent_result["reason"]
                    result["agent_override"] = True
                    return result
                else:
                    return {
                        "success": False,
                        "message": f"Agent analysis: {agent_result['reason']}",
                        "suggestion": "Add explicit tags or set 'force_store': true to override",
                        "agent_analysis": agent_result
                    }
        
        except Exception as e:
            logger.error(f"Agent analysis failed, falling back to standard storage: {e}")
            return await self.store_memory_handler(content, tags or [], metadata or {})
    
    async def retrieve_memory_with_context_assembly(self, query: str, 
                                                   limit: int = 10) -> dict:
        """
        Retrieve memories with intelligent context assembly.
        
        Uses the agent system to decompose the query, search for relevant context,
        and assemble a comprehensive response.
        """
        if not self.agent_enabled:
            # Fallback to standard retrieval
            memories = await self.storage.search_memories(query, limit)
            return {
                "success": True,
                "memories": [memory.to_dict() for memory in memories],
                "count": len(memories),
                "agent_enhanced": False
            }
        
        try:
            # Use agent system for intelligent context assembly
            context_result = await self.agent_integration.autonomous_retrieve_context(
                query,
                {"retrieval_limit": limit}
            )
            
            if context_result["success"]:
                return {
                    "success": True,
                    "context": context_result["context"],
                    "statistics": context_result["statistics"],
                    "total_items": context_result["total_items"],
                    "relevance_score": context_result["relevance_score"],
                    "agent_enhanced": True,
                    "decomposition": context_result["decomposition_summary"]
                }
            else:
                # Fallback to standard search
                logger.warning(f"Context assembly failed: {context_result['error']}")
                memories = await self.storage.search_memories(query, limit)
                return {
                    "success": True,
                    "memories": [memory.to_dict() for memory in memories],
                    "count": len(memories),
                    "agent_enhanced": False,
                    "agent_error": context_result["error"]
                }
        
        except Exception as e:
            logger.error(f"Agent context assembly failed: {e}")
            # Fallback to standard retrieval
            memories = await self.storage.search_memories(query, limit)
            return {
                "success": True,
                "memories": [memory.to_dict() for memory in memories],
                "count": len(memories),
                "agent_enhanced": False,
                "fallback_reason": str(e)
            }
    
    async def get_agent_status(self) -> dict:
        """Get status of the agent system"""
        if not self.agent_enabled:
            return {
                "agent_system": "disabled",
                "reason": "Agent system not initialized or failed to initialize"
            }
        
        try:
            integration = get_agent_integration()
            if integration:
                return await integration.get_agent_status()
            else:
                return {
                    "agent_system": "error",
                    "reason": "Agent integration not found"
                }
        except Exception as e:
            return {
                "agent_system": "error",
                "error": str(e)
            }
    
    # Enhanced MCP protocol handlers
    async def handle_store_memory(self, content: str, tags: list = None, metadata: dict = None) -> dict:
        """Enhanced store_memory handler with agent analysis"""
        return await self.store_memory_with_agent_analysis(content, tags, metadata)
    
    async def handle_retrieve_memory(self, query: str, limit: int = 10) -> dict:
        """Enhanced retrieve_memory handler with context assembly"""
        return await self.retrieve_memory_with_context_assembly(query, limit)
    
    async def handle_get_agent_status(self) -> dict:
        """New MCP handler for agent status"""
        return await self.get_agent_status()


class AgentMiddleware:
    """
    Middleware for adding agent capabilities to existing MCP servers.
    
    This can be used to wrap an existing MemoryServer instance to add
    agent capabilities without modifying the original server.
    """
    
    def __init__(self, server: MemoryServer):
        self.server = server
        self.agent_integration = None
        self.agent_enabled = False
    
    async def initialize(self):
        """Initialize agent capabilities"""
        try:
            self.agent_integration = initialize_agent_integration(self.server.storage)
            self.agent_enabled = True
            logger.info("Agent middleware initialized")
        except Exception as e:
            logger.error(f"Failed to initialize agent middleware: {e}")
            self.agent_enabled = False
    
    async def store_memory(self, content: str, tags: list = None, metadata: dict = None) -> dict:
        """Store memory with agent analysis"""
        if self.agent_enabled:
            try:
                agent_result = await self.agent_integration.autonomous_store_memory(
                    content, metadata or {}
                )
                
                if agent_result["stored"]:
                    return {
                        "success": True,
                        "hash": agent_result["hash"],
                        "agent_enhanced": True,
                        "agent_reason": agent_result["reason"],
                        "enhanced_tags": agent_result["tags"]
                    }
            except Exception as e:
                logger.error(f"Agent storage failed: {e}")
        
        # Fallback to original server
        return await self.server.store_memory_handler(content, tags or [], metadata or {})
    
    async def retrieve_memory(self, query: str, limit: int = 10) -> dict:
        """Retrieve memory with context assembly"""
        if self.agent_enabled:
            try:
                context_result = await self.agent_integration.autonomous_retrieve_context(query)
                if context_result["success"]:
                    return {
                        "success": True,
                        "context": context_result["context"],
                        "agent_enhanced": True,
                        "statistics": context_result["statistics"]
                    }
            except Exception as e:
                logger.error(f"Agent retrieval failed: {e}")
        
        # Fallback to original server
        memories = await self.server.storage.search_memories(query, limit)
        return {
            "success": True,
            "memories": [memory.to_dict() for memory in memories],
            "agent_enhanced": False
        }


# Factory function for creating agent-enabled servers
def create_agent_enabled_server(storage_backend: BaseStorageBackend) -> AgentEnabledMemoryServer:
    """
    Factory function to create an agent-enabled memory server.
    
    Args:
        storage_backend: The storage backend to use
        
    Returns:
        AgentEnabledMemoryServer instance with agent capabilities
    """
    return AgentEnabledMemoryServer(storage_backend)


# Utility function for adding agent middleware to existing servers
async def add_agent_middleware(server: MemoryServer) -> AgentMiddleware:
    """
    Add agent capabilities to an existing memory server via middleware.
    
    Args:
        server: Existing MemoryServer instance
        
    Returns:
        AgentMiddleware wrapper with agent capabilities
    """
    middleware = AgentMiddleware(server)
    await middleware.initialize()
    return middleware


# Example usage for server initialization
async def initialize_agent_server(storage_backend: BaseStorageBackend) -> AgentEnabledMemoryServer:
    """
    Initialize a complete agent-enabled memory server.
    
    This is the recommended way to create a server with full agent capabilities.
    """
    server = create_agent_enabled_server(storage_backend)
    await server.initialize()
    
    logger.info("Agent-enabled memory server initialized successfully")
    return server