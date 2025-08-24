# Claude Setup - Universal Installer

This directory contains everything needed to install the complete Claude Code integration system with autonomous sub-agents, enhanced commands, and session hooks.

## Quick Start

```bash
cd claude_setup/
python install.py
```

## What Gets Installed

### 🤖 **Autonomous Sub-Agents** → `~/.claude/agents/`
- **memory-store**: Proactively stores decisions, insights, and solutions
- **memory-health**: Monitors memory system health and performance  
- **memory-recall**: Retrieves relevant memories and historical context
- **debug-context**: Gathers debugging context from past similar issues
- **test-context**: Provides comprehensive context for test creation
- **memory-context**: Analyzes tasks and retrieves all relevant context
- **memory-consolidate**: Maintains and optimizes memory system organization

Each agent has enhanced descriptions with specific trigger conditions following Anthropic best practices for automatic delegation.

### ⌨️ **Enhanced Commands** → `~/.claude/commands/`
- **memory-store**: Uses memory-store sub-agent instead of direct API calls
- **memory-recall**: Uses memory-recall sub-agent for intelligent retrieval
- **memory-health**: Uses memory-health sub-agent for comprehensive diagnostics
- **memory-context**: Uses memory-context sub-agent for task analysis

### 🪝 **Session Hooks** → `~/.claude/hooks/`
- **session-start**: Automatically injects relevant memories at session start
- **session-end**: Consolidates session outcomes and stores as memories
- **Project detection**: Multi-language project context awareness
- **Memory scoring**: Advanced relevance algorithms for context selection

### ⚙️ **Centralized Configuration**
- **memory-service.conf**: Secure credential storage
- **memory-service-config.sh**: Centralized functions for all components
- **Template system**: No hardcoded URLs, API keys, or endpoints

## Directory Structure

```
claude_setup/
├── install.py              # Universal installer script
├── README.md               # This file
├── agents/                 # Sub-agent templates and enhanced versions
│   ├── *.md                # Enhanced agents with detailed triggers
│   └── *.template.md       # Templates with placeholder variables
├── commands/               # Enhanced Claude Code commands
│   ├── memory-store.md     # Uses memory-store sub-agent
│   ├── memory-recall.md    # Uses memory-recall sub-agent
│   ├── memory-health.md    # Uses memory-health sub-agent
│   └── memory-context.md   # Uses memory-context sub-agent
└── hooks/                  # Session awareness hooks system
    ├── core/               # Core hook implementations
    ├── utilities/          # Support utilities
    ├── config.template.json # Hook configuration template
    └── install.sh          # Hooks-specific installer
```

## Installation Process

1. **Configuration**: Prompts for memory service URL, API key, client hostname
2. **Security**: Masked API key input, secure file permissions, auto-generation option
3. **Agent Installation**: Deploys all 7 sub-agents with enhanced trigger descriptions
4. **Command Integration**: Installs commands that delegate to sub-agents
5. **Hooks Setup**: Configures session-start/end hooks for memory awareness
6. **Testing**: Verifies connectivity and component installation

## Key Features

### 🎯 **No Hardcoded Dependencies**
- Template system with placeholder variables
- Dynamic configuration via centralized script
- Adapts to any memory service endpoint/credentials

### 🧠 **Enhanced Agent Intelligence** 
- Detailed trigger conditions using "PROACTIVELY" and "MUST BE USED"
- 10+ specific triggers per agent for automatic delegation
- Follows Anthropic best practices for sub-agent activation

### 🔗 **System Integration**
- Sub-agents, commands, and hooks work together seamlessly
- Centralized configuration prevents duplication
- Enhanced commands delegate to intelligent sub-agents

### 🚀 **Production Ready**
- Complete isolation from Claude's actual directories
- Secure credential handling and file permissions
- Comprehensive error handling and rollback capability

## Advanced Usage

### Manual Component Installation
You can install individual components:

```bash
# Install only agents
python install.py --agents-only

# Install only commands  
python install.py --commands-only

# Install only hooks
python install.py --hooks-only
```

### Custom Configuration
Edit templates in the respective directories before installation:
- `agents/`: Modify sub-agent behavior and triggers
- `commands/`: Customize command descriptions and functionality
- `hooks/`: Adjust session awareness and memory injection logic

### Troubleshooting
- Check `~/.claude/memory-service.conf` for configuration issues
- Test connectivity: `~/.claude/memory-service-config.sh test`
- Verify components: Check `~/.claude/{agents,commands,hooks}/` directories
- Review logs: Installation provides detailed feedback and error messages

## System Requirements

- Python 3.8+ for installer
- Claude Code CLI installed and configured
- MCP Memory Service running and accessible
- Network connectivity to memory service endpoint

The installer automatically detects existing configurations and provides intelligent defaults for seamless setup.