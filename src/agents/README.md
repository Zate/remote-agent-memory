# Autonomous Agent System

## Overview

The Autonomous Agent System transforms the MCP Memory Service from a reactive, command-driven service into an intelligent, proactive memory assistant. Instead of waiting for explicit user commands, the system enables Claude to autonomously decide when to store decisions, retrieve context, or perform memory operations based on conversation content and context.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent System Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ Claude Code     │    │         Sub-Agents               │   │
│  │ Session         │───▶│  (.claude/agents/*.md)           │   │
│  │                 │    │                                  │   │
│  │ - Conversation  │    │  • memory-store.md               │   │
│  │ - Task Context  │    │  • memory-context.md             │   │
│  │ - Decisions     │    │  • memory-recall.md              │   │
│  └─────────────────┘    │  • debug-context.md              │   │
│           │              │  • test-context.md               │   │
│           │              │  • memory-health.md              │   │
│           v              │  • memory-consolidate.md         │   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Agent Orchestrator                           │   │
│  │                                                         │   │
│  │  • Analyzes context and content                        │   │
│  │  • Decides which agents to invoke                      │   │
│  │  • Coordinates multi-agent workflows                   │   │
│  │  • Manages agent execution and results                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           v                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Core Intelligence Layer                    │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │  │ Task Decomposer │  │     Context Builder             │ │
│  │  │                 │  │                                 │ │
│  │  │ • Analyzes      │  │ • Assembles comprehensive      │ │
│  │  │   tasks         │  │   context from multiple        │ │
│  │  │ • Identifies    │  │   sources                       │ │
│  │  │   context needs │  │ • Organizes by relevance       │ │
│  │  │ • Plans search  │  │ • Formats for presentation     │ │
│  │  │   strategies    │  │                                 │ │
│  │  └─────────────────┘  └─────────────────────────────────┘ │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────────┐ │
│  │  │              Relevance Scorer                       │ │
│  │  │                                                     │ │
│  │  │ • Multi-dimensional scoring                         │ │
│  │  │ • Semantic + temporal + contextual                  │ │
│  │  │ • Technology alignment                              │ │
│  │  │ • Task-specific weighting                           │ │
│  │  └─────────────────────────────────────────────────────┘ │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           v                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Memory Operations                          │   │
│  │                                                         │   │
│  │  • Store decisions and solutions                        │   │
│  │  • Retrieve relevant context                            │   │
│  │  • Search with intelligent filtering                    │   │
│  │  • Maintain system health                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Types

#### Claude Code Sub-Agents (`.claude/agents/`)
These are Claude Code sub-agents that can be autonomously invoked by the main Claude instance:

- **memory-store.md**: Autonomously stores important decisions, solutions, and insights
- **memory-context.md**: Gathers comprehensive context for complex tasks using Opus model
- **memory-recall.md**: Retrieves relevant memories for similar problems and patterns
- **debug-context.md**: Provides debugging context from past solutions and error patterns
- **test-context.md**: Specialized in gathering context for test creation
- **memory-health.md**: Monitors memory system health and performance
- **memory-consolidate.md**: Maintains memory system organization and cleanup

#### Python Intelligence Layer (`src/agents/`)
These are Python modules that provide the core intelligence:

- **AgentOrchestrator**: Decides when and which agents to invoke
- **TaskDecomposer**: Breaks down complex tasks into searchable components
- **ContextBuilder**: Assembles comprehensive context from multiple sources
- **RelevanceScorer**: Multi-dimensional relevance scoring for search results

## Key Features

### 🤖 Autonomous Decision-Making
- **Trigger Detection**: Automatically recognizes when decisions are made, errors occur, or context is needed
- **Smart Storage**: Decides what information is worth preserving based on content analysis
- **Proactive Context**: Gathers relevant context before complex tasks begin

### 🧠 Intelligent Context Assembly
- **Task Decomposition**: Breaks complex tasks into searchable components
- **Multi-Source Search**: Searches across different types of context (technical patterns, similar implementations, best practices)
- **Relevance Scoring**: Uses multi-dimensional scoring considering semantic similarity, temporal relevance, and contextual factors
- **Organized Presentation**: Assembles context into well-structured, prioritized sections

### 🔄 Seamless Integration
- **Backward Compatible**: Existing MCP Memory Service functionality remains unchanged
- **Optional Enhancement**: Can be enabled/disabled without affecting core operations
- **Command Migration**: Existing commands can be enhanced with agent capabilities
- **API Extensions**: New endpoints for agent-driven operations

### 📊 Advanced Features
- **Technology Alignment**: Considers technology stack when scoring relevance
- **Temporal Intelligence**: Weighs recency vs. historical context based on task type
- **Usage Patterns**: Learns from memory access patterns
- **Quality Maintenance**: Automatic consolidation and cleanup

## Usage Examples

### Autonomous Storage
```python
from src.agents import autonomous_store_memory

# Claude automatically analyzes and stores important decisions
result = await autonomous_store_memory(
    "We decided to use PostgreSQL instead of MongoDB for the user service because we need ACID transactions"
)

# Result:
# {
#   "stored": True,
#   "hash": "abc123...",
#   "reason": "Decision detected with technical justification",
#   "tags": ["decision", "database", "postgresql", "architecture"],
#   "agent_analysis": "Triggered by decision_made"
# }
```

### Intelligent Context Assembly
```python
from src.agents import autonomous_retrieve_context

# Automatically decomposes task and gathers relevant context
context = await autonomous_retrieve_context(
    "I need to implement JWT authentication for a Python Flask API"
)

# Returns comprehensive context including:
# - Similar implementations from memory
# - Best practices for JWT auth
# - Common security pitfalls to avoid  
# - Flask-specific patterns
# - Recent related work
```

### Server Integration
```python
from src.agents import initialize_agent_server
from src.mcp_memory_service.storage.sqlite_vec import SQLiteVecStorage

# Create agent-enabled server
storage = SQLiteVecStorage()
server = await initialize_agent_server(storage)

# Server now has autonomous capabilities while maintaining MCP compatibility
```

## Configuration

### Environment Variables
```bash
# Enable agent system (default: true)
MCP_AGENTS_ENABLED=true

# Agent decision sensitivity (low, medium, high)
MCP_AGENTS_SENSITIVITY=medium

# Enable autonomous storage (default: true)
MCP_AGENTS_AUTO_STORE=true

# Context assembly complexity (simple, comprehensive)
MCP_AGENTS_CONTEXT_MODE=comprehensive
```

### Claude Code Integration
The system automatically integrates with Claude Code through:

1. **Sub-agent definitions** in `.claude/agents/`
2. **Autonomous invocation** via the Task tool
3. **Context-aware decision making** based on conversation analysis
4. **Memory service API** integration for storage/retrieval

## API Reference

### Autonomous Operations
```python
# Storage with agent analysis
async def autonomous_store_memory(content: str, metadata: dict = None) -> dict

# Context assembly with task decomposition  
async def autonomous_retrieve_context(query: str, metadata: dict = None) -> dict

# Agent system status
async def get_agent_status() -> dict
```

### Server Integration
```python
# Create agent-enabled server
def create_agent_enabled_server(storage_backend: BaseStorageBackend) -> AgentEnabledMemoryServer

# Add agents to existing server
async def add_agent_middleware(server: MemoryServer) -> AgentMiddleware

# Initialize complete agent system
async def initialize_agent_server(storage_backend: BaseStorageBackend) -> AgentEnabledMemoryServer
```

### Agent Orchestration
```python
# Analyze content for agent triggers
async def analyze_context(content: str, metadata: dict = None) -> List[AgentInvocation]

# Execute agent invocations
async def execute_invocations(invocations: List[AgentInvocation]) -> List[AgentResult]
```

## Development

### Adding New Sub-Agents
1. Create `.claude/agents/new-agent.md` with:
   ```yaml
   ---
   name: new-agent
   description: Agent description
   tools: Read, Grep, Bash
   model: sonnet
   ---
   
   Agent system prompt and instructions...
   ```

2. Add trigger logic in `AgentOrchestrator.analyze_context()`

3. Update integration to handle new agent results

### Extending Intelligence Components
- **TaskDecomposer**: Add new task categories and context types
- **ContextBuilder**: Create new context section types
- **RelevanceScorer**: Add new scoring dimensions
- **Integration**: Add new autonomous operation types

### Testing
```bash
# Run agent system demo
python examples/agent_system_demo.py

# Run integration tests
pytest tests/agents/

# Test individual components
python -m src.agents.task_decomposer
python -m src.agents.context_builder
python -m src.agents.relevance_scorer
```

## Performance Considerations

### Memory Usage
- **Model Caching**: Models loaded once and cached globally
- **Result Caching**: Frequent queries cached with TTL
- **Lazy Loading**: Components initialized only when needed

### Response Time
- **Parallel Execution**: Multiple searches executed concurrently
- **Smart Limits**: Result limits based on context type and priority
- **Early Termination**: Stop processing when confidence threshold reached

### Scalability
- **Asynchronous Design**: All operations use async/await
- **Resource Limits**: Configurable limits on search depth and result counts
- **Graceful Degradation**: Falls back to simple operations if agent system fails

## Troubleshooting

### Common Issues
1. **Agent Not Triggering**: Check trigger patterns in orchestrator
2. **Context Too Sparse**: Reduce similarity thresholds
3. **Performance Issues**: Enable caching and reduce search limits
4. **Memory Errors**: Check storage backend connectivity

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python -m src.agents.integration --debug
```

### Health Checks
```python
from src.agents import get_agent_status

status = await get_agent_status()
print(json.dumps(status, indent=2))
```

## Roadmap

### Phase 1: Core System ✅
- Agent orchestration and coordination
- Task decomposition and context assembly
- Multi-dimensional relevance scoring
- Basic server integration

### Phase 2: Enhanced Intelligence 🚧
- Machine learning-based relevance scoring
- Dynamic agent selection based on success rates
- Advanced context understanding with NLP
- Cross-session learning and adaptation

### Phase 3: Distributed Operations 📋
- Multi-server agent coordination
- Federated memory search across instances
- Load balancing and failover
- Advanced analytics and insights

## Contributing

1. **Architecture Changes**: Discuss in issues before implementing
2. **New Agents**: Follow existing patterns and documentation standards
3. **Intelligence Components**: Include comprehensive tests
4. **Performance**: Profile changes and include benchmarks

## License

Same as MCP Memory Service - see project LICENSE file.