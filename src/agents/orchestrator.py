"""
Agent Orchestrator

Coordinates between specialized sub-agents to provide autonomous memory operations
and intelligent context assembly for Claude Code sessions.

This orchestrator enables Claude to autonomously decide when to store, retrieve,
or search memories by delegating to specialized sub-agents rather than requiring
explicit user commands.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Set
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of available sub-agents"""
    MEMORY_STORE = "memory-store"
    MEMORY_CONTEXT = "memory-context"
    MEMORY_RECALL = "memory-recall" 
    MEMORY_CONSOLIDATE = "memory-consolidate"
    MEMORY_HEALTH = "memory-health"
    TEST_CONTEXT = "test-context"
    DEBUG_CONTEXT = "debug-context"


class TriggerCondition(Enum):
    """Conditions that trigger agent invocation"""
    DECISION_MADE = "decision_made"
    ERROR_ENCOUNTERED = "error_encountered"
    TASK_STARTED = "task_started"
    TESTING_NEEDED = "testing_needed"
    DEBUG_NEEDED = "debug_needed"
    CONTEXT_NEEDED = "context_needed"
    HEALTH_CHECK = "health_check"
    MAINTENANCE_DUE = "maintenance_due"


@dataclass
class AgentInvocation:
    """Represents a request to invoke a sub-agent"""
    agent_type: AgentType
    trigger: TriggerCondition
    context: Dict[str, Any]
    priority: int = 1  # 1=high, 2=medium, 3=low
    dependencies: List[AgentType] = None


@dataclass
class AgentResult:
    """Result from a sub-agent execution"""
    agent_type: AgentType
    success: bool
    data: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


class AgentOrchestrator:
    """
    Orchestrates autonomous agent invocation and coordination.
    
    Enables Claude to make intelligent decisions about when to store memories,
    retrieve context, or perform maintenance without explicit user commands.
    """
    
    def __init__(self):
        self.active_agents: Set[AgentType] = set()
        self.agent_history: List[AgentResult] = []
        self.decision_patterns = self._initialize_decision_patterns()
        
    def _initialize_decision_patterns(self) -> Dict[str, List[AgentType]]:
        """Initialize patterns that determine which agents to invoke"""
        return {
            # Context patterns for autonomous decision-making
            "error_keywords": [
                "error", "exception", "fail", "crash", "bug", "issue",
                "problem", "broken", "not working", "timeout"
            ],
            "decision_keywords": [
                "decided", "chosen", "selected", "approach", "strategy",
                "solution", "resolved", "implemented", "architecture"
            ],
            "test_keywords": [
                "test", "testing", "spec", "verify", "validate",
                "check", "assert", "expect", "should", "coverage"
            ],
            "task_keywords": [
                "implement", "create", "build", "develop", "add",
                "feature", "function", "component", "module"
            ],
            "context_keywords": [
                "similar", "before", "previous", "history", "experience",
                "pattern", "best practice", "lesson learned"
            ]
        }
    
    async def analyze_context(self, content: str, metadata: Dict[str, Any] = None) -> List[AgentInvocation]:
        """
        Analyze content and determine which agents should be invoked.
        
        This is the core autonomous decision-making function that enables
        Claude to decide when memory operations are needed.
        """
        invocations = []
        content_lower = content.lower()
        metadata = metadata or {}
        
        # Check for decision-making content that should be stored
        if self._contains_decision_content(content_lower):
            invocations.append(AgentInvocation(
                agent_type=AgentType.MEMORY_STORE,
                trigger=TriggerCondition.DECISION_MADE,
                context={
                    "content": content,
                    "metadata": metadata,
                    "auto_store": True,
                    "reason": "Decision or solution detected"
                },
                priority=1
            ))
        
        # Check for error or debugging scenarios
        if self._contains_error_content(content_lower):
            invocations.append(AgentInvocation(
                agent_type=AgentType.DEBUG_CONTEXT,
                trigger=TriggerCondition.ERROR_ENCOUNTERED,
                context={
                    "error_content": content,
                    "metadata": metadata
                },
                priority=1
            ))
        
        # Check for task initiation requiring context
        if self._contains_task_content(content_lower):
            invocations.append(AgentInvocation(
                agent_type=AgentType.MEMORY_CONTEXT,
                trigger=TriggerCondition.TASK_STARTED,
                context={
                    "task_description": content,
                    "metadata": metadata
                },
                priority=1
            ))
        
        # Check for testing scenarios
        if self._contains_test_content(content_lower):
            invocations.append(AgentInvocation(
                agent_type=AgentType.TEST_CONTEXT,
                trigger=TriggerCondition.TESTING_NEEDED,
                context={
                    "test_request": content,
                    "metadata": metadata
                },
                priority=2
            ))
        
        # Check for requests needing historical context
        if self._contains_context_request(content_lower):
            invocations.append(AgentInvocation(
                agent_type=AgentType.MEMORY_RECALL,
                trigger=TriggerCondition.CONTEXT_NEEDED,
                context={
                    "query": content,
                    "metadata": metadata
                },
                priority=2
            ))
        
        return sorted(invocations, key=lambda x: x.priority)
    
    def _contains_decision_content(self, content: str) -> bool:
        """Detect content that represents decisions or solutions to store"""
        decision_indicators = [
            # Decision patterns
            r"(?:decided|chosen|selected|going with|will use|approach is)",
            r"(?:solution|fix|resolved|implemented|working)",
            r"(?:architecture|design|pattern|strategy)",
            r"(?:learned|discovered|found that|realized)",
            
            # Implementation patterns
            r"(?:successfully|completed|finished|deployed)",
            r"(?:best practice|recommendation|should)",
            r"(?:key insight|important|critical|essential)"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in decision_indicators)
    
    def _contains_error_content(self, content: str) -> bool:
        """Detect error or debugging scenarios"""
        error_indicators = [
            r"(?:error|exception|failed?|crash|bug)",
            r"(?:not working|broken|issue|problem)",
            r"(?:debug|troubleshoot|investigate)",
            r"(?:timeout|connection|memory leak)",
            r"(?:stacktrace|traceback|log shows)"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in error_indicators)
    
    def _contains_task_content(self, content: str) -> bool:
        """Detect task initiation that might need context"""
        task_indicators = [
            r"(?:implement|create|build|develop|add)",
            r"(?:feature|function|component|module|system)",
            r"(?:need to|want to|going to|planning to)",
            r"(?:how do I|how can I|what's the best way)",
            r"(?:working on|starting|beginning)"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in task_indicators)
    
    def _contains_test_content(self, content: str) -> bool:
        """Detect testing scenarios"""
        test_indicators = [
            r"(?:test|testing|spec|verify|validate)",
            r"(?:unit test|integration test|e2e test)",
            r"(?:check|assert|expect|should)",
            r"(?:coverage|test case|test suite)",
            r"(?:mock|stub|fixture)"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in test_indicators)
    
    def _contains_context_request(self, content: str) -> bool:
        """Detect requests for historical context"""
        context_indicators = [
            r"(?:similar|before|previous|history)",
            r"(?:have we|did we|how did we)",
            r"(?:last time|previously|earlier)",
            r"(?:experience|pattern|lesson learned)",
            r"(?:best practice|what worked|what didn't work)"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in context_indicators)
    
    async def execute_invocations(self, invocations: List[AgentInvocation]) -> List[AgentResult]:
        """
        Execute a list of agent invocations, handling dependencies and coordination.
        """
        results = []
        
        for invocation in invocations:
            try:
                start_time = datetime.now()
                
                # Check if agent is already active to avoid conflicts
                if invocation.agent_type in self.active_agents:
                    logger.warning(f"Agent {invocation.agent_type} already active, skipping")
                    continue
                
                self.active_agents.add(invocation.agent_type)
                
                # Execute the agent
                result = await self._execute_single_agent(invocation)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                result.execution_time = execution_time
                
                results.append(result)
                self.agent_history.append(result)
                
            except Exception as e:
                logger.error(f"Error executing agent {invocation.agent_type}: {e}")
                results.append(AgentResult(
                    agent_type=invocation.agent_type,
                    success=False,
                    data={},
                    execution_time=0,
                    error_message=str(e)
                ))
            finally:
                self.active_agents.discard(invocation.agent_type)
        
        return results
    
    async def _execute_single_agent(self, invocation: AgentInvocation) -> AgentResult:
        """Execute a single agent invocation"""
        
        # Prepare agent-specific prompt based on the invocation
        agent_prompt = self._build_agent_prompt(invocation)
        
        # Note: In a real implementation, this would use the Claude Code Task tool
        # to invoke the sub-agent. For now, we simulate the structure:
        
        # TODO: Implement actual Claude Code Task invocation
        # task_result = await self._invoke_claude_code_agent(
        #     agent_type=invocation.agent_type.value,
        #     prompt=agent_prompt
        # )
        
        # Simulated result for now
        task_result = {
            "success": True,
            "data": {
                "agent": invocation.agent_type.value,
                "trigger": invocation.trigger.value,
                "context": invocation.context,
                "prompt_sent": agent_prompt
            }
        }
        
        return AgentResult(
            agent_type=invocation.agent_type,
            success=task_result["success"],
            data=task_result["data"],
            execution_time=0  # Will be set by caller
        )
    
    def _build_agent_prompt(self, invocation: AgentInvocation) -> str:
        """Build the appropriate prompt for the agent invocation"""
        
        base_prompt = f"Agent triggered by: {invocation.trigger.value}\n"
        
        if invocation.agent_type == AgentType.MEMORY_STORE:
            return f"""{base_prompt}
Store this important information in memory:

Content: {invocation.context.get('content', '')}

This was automatically detected as containing decisions, solutions, or important insights that should be preserved for future reference.

Please store this with appropriate tags and metadata.
"""
        
        elif invocation.agent_type == AgentType.MEMORY_CONTEXT:
            return f"""{base_prompt}
Gather comprehensive context for this task:

Task: {invocation.context.get('task_description', '')}

Please decompose this task, search for related memories, and provide relevant context that would help with successful completion.
"""
        
        elif invocation.agent_type == AgentType.DEBUG_CONTEXT:
            return f"""{base_prompt}
Provide debugging context for this issue:

Error/Issue: {invocation.context.get('error_content', '')}

Please search for similar problems, solutions, and debugging approaches from past experiences.
"""
        
        elif invocation.agent_type == AgentType.TEST_CONTEXT:
            return f"""{base_prompt}
Provide testing context for this request:

Testing Request: {invocation.context.get('test_request', '')}

Please analyze the target, find testing patterns, and provide comprehensive context for test creation.
"""
        
        elif invocation.agent_type == AgentType.MEMORY_RECALL:
            return f"""{base_prompt}
Retrieve relevant memories for this query:

Query: {invocation.context.get('query', '')}

Please search for similar situations, solutions, and relevant historical context.
"""
        
        else:
            return f"""{base_prompt}
Context: {invocation.context}

Please execute your specialized function based on this context.
"""
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "active_agents": [agent.value for agent in self.active_agents],
            "total_executions": len(self.agent_history),
            "recent_results": [
                {
                    "agent": result.agent_type.value,
                    "success": result.success,
                    "execution_time": result.execution_time
                }
                for result in self.agent_history[-5:]  # Last 5 executions
            ]
        }
    
    async def autonomous_memory_operation(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for autonomous memory operations.
        
        This function analyzes content and autonomously decides what memory
        operations should be performed, then executes them.
        """
        logger.info("Starting autonomous memory operation")
        
        # Analyze what agents should be invoked
        invocations = await self.analyze_context(content, context)
        
        if not invocations:
            logger.info("No agents triggered for this content")
            return {"message": "No memory operations needed", "agents_triggered": 0}
        
        logger.info(f"Triggering {len(invocations)} agents: {[inv.agent_type.value for inv in invocations]}")
        
        # Execute the agents
        results = await self.execute_invocations(invocations)
        
        # Aggregate results
        successful_agents = [r for r in results if r.success]
        failed_agents = [r for r in results if not r.success]
        
        return {
            "message": f"Executed {len(successful_agents)}/{len(results)} agents successfully",
            "agents_triggered": len(invocations),
            "successful_agents": [r.agent_type.value for r in successful_agents],
            "failed_agents": [r.agent_type.value for r in failed_agents],
            "results": [
                {
                    "agent": r.agent_type.value,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "data": r.data
                }
                for r in results
            ]
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()


# Convenience functions for integration
async def autonomous_store_decision(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Autonomously store a decision or important insight"""
    return await orchestrator.autonomous_memory_operation(content, metadata)


async def autonomous_get_context(query: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Autonomously gather context for a task or question"""
    return await orchestrator.autonomous_memory_operation(query, metadata)


async def autonomous_debug_support(error_content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Autonomously get debugging support for an error"""
    return await orchestrator.autonomous_memory_operation(error_content, metadata)