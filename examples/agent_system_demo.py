#!/usr/bin/env python3
"""
Agent System Demonstration

This script demonstrates the autonomous agent system capabilities including:
- Autonomous memory storage decisions
- Intelligent context assembly
- Task decomposition and analysis
- Multi-dimensional relevance scoring

Run this script to see the agent system in action.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_memory_service.storage.sqlite_vec import SQLiteVecStorage
from src.mcp_memory_service.models.memory import Memory, MemoryMetadata
from src.agents.integration import initialize_agent_integration, autonomous_store_memory, autonomous_retrieve_context, get_agent_status
from src.agents import orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AgentSystemDemo:
    """Demonstration of the autonomous agent system"""
    
    def __init__(self):
        self.storage = None
        self.integration = None
    
    async def setup(self):
        """Set up the demo environment"""
        print("🚀 Setting up Agent System Demo")
        print("=" * 50)
        
        # Initialize storage (using SQLite-Vec for demo)
        self.storage = SQLiteVecStorage()
        await self.storage.initialize()
        
        # Initialize agent integration
        self.integration = initialize_agent_integration(self.storage)
        
        # Seed some test memories for context demonstration
        await self._seed_test_memories()
        
        print("✅ Setup complete!\n")
    
    async def _seed_test_memories(self):
        """Seed the memory system with test data"""
        print("📝 Seeding test memories...")
        
        test_memories = [
            {
                "content": "Implemented JWT authentication for the user service using Python Flask. Used Redis for session storage and token blacklisting. Key considerations: 15-minute access tokens, 7-day refresh tokens, proper logout handling.",
                "tags": ["python", "flask", "jwt", "authentication", "redis", "implementation"],
                "metadata": {"type": "implementation", "project": "user-service", "date": "2024-01-15"}
            },
            {
                "content": "Fixed memory leak in the data processing pipeline. Issue was caused by unclosed database connections in the async handlers. Solution: implemented proper context managers and connection pooling.",
                "tags": ["python", "bug-fix", "memory-leak", "database", "async", "performance"],
                "metadata": {"type": "bug-fix", "project": "data-pipeline", "severity": "high"}
            },
            {
                "content": "Best practice for testing async functions: Use pytest-asyncio and proper event loop management. Always test both success and failure cases. Mock external dependencies using unittest.mock.AsyncMock.",
                "tags": ["python", "testing", "async", "pytest", "best-practices"],
                "metadata": {"type": "best-practice", "category": "testing"}
            },
            {
                "content": "Database migration strategy: Use incremental migrations with rollback capability. Test migrations on staging environment first. Keep migrations small and focused on single concerns.",
                "tags": ["database", "migration", "deployment", "best-practices", "strategy"],
                "metadata": {"type": "strategy", "category": "database"}
            },
            {
                "content": "Common Docker pitfall: Not using .dockerignore leads to large build contexts. Always include node_modules, .git, and temporary files in .dockerignore to speed up builds.",
                "tags": ["docker", "pitfall", "build-optimization", "best-practices"],
                "metadata": {"type": "pitfall", "category": "docker"}
            },
            {
                "content": "API rate limiting implementation: Used Redis with sliding window algorithm. Configuration: 100 requests per minute per user, exponential backoff on rate limit exceeded.",
                "tags": ["api", "rate-limiting", "redis", "implementation", "performance"],
                "metadata": {"type": "implementation", "project": "api-gateway"}
            }
        ]
        
        for memory_data in test_memories:
            memory = Memory(
                content=memory_data["content"],
                tags=memory_data["tags"],
                metadata=MemoryMetadata(**memory_data["metadata"]),
                timestamp=datetime.now()
            )
            await self.storage.store_memory(memory)
        
        print(f"   Seeded {len(test_memories)} test memories")
    
    async def demo_autonomous_storage(self):
        """Demonstrate autonomous memory storage decisions"""
        print("🤖 Demo: Autonomous Memory Storage")
        print("-" * 40)
        
        # Test cases that should trigger autonomous storage
        test_decisions = [
            "We decided to use PostgreSQL instead of MongoDB for the new microservice because we need ACID transactions and complex queries.",
            "Successfully resolved the Redis connection timeout issue by implementing connection pooling with a max pool size of 20.",
            "Architecture decision: Moving from monolith to microservices using Docker containers and Kubernetes orchestration.",
            "This is just a random comment that probably shouldn't be stored as a memory."
        ]
        
        for i, decision in enumerate(test_decisions, 1):
            print(f"\n📝 Test {i}: Analyzing content...")
            print(f"Content: {decision[:80]}...")
            
            result = await autonomous_store_memory(
                decision,
                {"demo": True, "test_case": i}
            )
            
            if result["stored"]:
                print(f"✅ STORED - Reason: {result['reason']}")
                print(f"   Tags: {', '.join(result['tags'])}")
                print(f"   Analysis: {result['agent_analysis']}")
            else:
                print(f"❌ NOT STORED - Reason: {result['reason']}")
    
    async def demo_context_assembly(self):
        """Demonstrate intelligent context assembly"""
        print("\n\n🧠 Demo: Intelligent Context Assembly")
        print("-" * 40)
        
        # Test queries that should trigger context assembly
        test_queries = [
            "I need to implement user authentication for a Python web API",
            "Help me debug a memory leak in my Python application", 
            "What are the best practices for testing async Python functions?",
            "How should I handle database migrations in production?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Query {i}: {query}")
            print("=" * len(f"Query {i}: {query}"))
            
            result = await autonomous_retrieve_context(
                query,
                {"demo": True, "query_number": i}
            )
            
            if result["success"]:
                stats = result["statistics"]
                print(f"✅ Context Assembled Successfully")
                print(f"   Total Items: {result['total_items']}")
                print(f"   Relevance Score: {result['relevance_score']:.2f}")
                print(f"   Sections Created: {stats['overview']['total_sections']}")
                print(f"   Technologies: {', '.join(stats['technologies'])}")
                
                # Show a snippet of the context
                context_lines = result["context"].split("\n")
                print(f"\n📋 Context Preview:")
                for line in context_lines[:10]:
                    if line.strip():
                        print(f"   {line}")
                if len(context_lines) > 10:
                    print(f"   ... ({len(context_lines) - 10} more lines)")
            else:
                print(f"❌ Context Assembly Failed: {result['error']}")
    
    async def demo_orchestrator_analysis(self):
        """Demonstrate orchestrator decision-making analysis"""
        print("\n\n🎯 Demo: Agent Orchestrator Analysis")
        print("-" * 40)
        
        test_scenarios = [
            {
                "content": "Getting a ConnectionTimeout error when trying to connect to the Redis server",
                "expected": "Should trigger debug-context agent"
            },
            {
                "content": "Need to create unit tests for the user registration function",
                "expected": "Should trigger test-context agent"
            },
            {
                "content": "We've chosen to implement the payment system using Stripe API with webhook validation",
                "expected": "Should trigger memory-store agent"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🧪 Scenario {i}: {scenario['expected']}")
            print(f"Content: {scenario['content']}")
            
            # Analyze what agents would be triggered
            invocations = await orchestrator.analyze_context(
                scenario["content"],
                {"demo_scenario": i}
            )
            
            print(f"📊 Analysis Results:")
            print(f"   Agents Triggered: {len(invocations)}")
            
            for inv in invocations:
                print(f"   - {inv.agent_type.value} (Priority: {inv.priority}, Trigger: {inv.trigger.value})")
                if "reason" in inv.context:
                    print(f"     Reason: {inv.context['reason']}")
    
    async def demo_agent_status(self):
        """Demonstrate agent system status reporting"""
        print("\n\n📊 Demo: Agent System Status")
        print("-" * 40)
        
        status = await get_agent_status()
        
        print("🤖 Agent System Status:")
        print(json.dumps(status, indent=2, default=str))
    
    async def run_full_demo(self):
        """Run the complete demonstration"""
        try:
            await self.setup()
            await self.demo_autonomous_storage()
            await self.demo_context_assembly()
            await self.demo_orchestrator_analysis()
            await self.demo_agent_status()
            
            print("\n\n🎉 Agent System Demonstration Complete!")
            print("=" * 50)
            print("The autonomous agent system successfully demonstrated:")
            print("✅ Intelligent decision-making for memory storage")
            print("✅ Comprehensive context assembly from multiple sources")
            print("✅ Task decomposition and analysis")
            print("✅ Multi-agent coordination and orchestration")
            print("✅ Real-time status monitoring and reporting")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed with error: {e}")
        finally:
            # Cleanup
            if self.storage:
                await self.storage.close()


async def main():
    """Main demonstration function"""
    demo = AgentSystemDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    print("🤖 Autonomous Agent System Demonstration")
    print("🚀 Starting demo...")
    print()
    
    asyncio.run(main())