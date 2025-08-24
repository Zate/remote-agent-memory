# Analyze Complex Tasks and Retrieve Context

I'll use the **memory-context sub-agent** to analyze complex tasks and automatically retrieve all relevant context and prior knowledge. This command is essential for comprehensive context assembly before significant work begins.

## What I'll do:

I'll immediately invoke the `memory-context` sub-agent, which will:

1. **Task Analysis**: Break down complex requests into components and requirements
2. **Memory Retrieval**: Search for all relevant past experiences and knowledge
3. **Context Assembly**: Organize scattered information into actionable intelligence
4. **Gap Identification**: Highlight missing knowledge or potential challenges  
5. **Strategic Planning**: Provide informed recommendations and next steps

## Sub-Agent Intelligence:

Instead of basic session capture, the `memory-context` sub-agent provides:
- **Comprehensive Knowledge Assembly**: Gathers all relevant historical context
- **Strategic Task Decomposition**: Breaks complex work into manageable components
- **Multi-dimensional Context**: Technical, architectural, domain, and risk perspectives
- **Historical Pattern Analysis**: Leverages past project experiences and decisions
- **Proactive Context Building**: Assembles context BEFORE work begins, not after

The sub-agent operates proactively:
- **MUST BE USED** before significant implementation or development work
- **Essential for** architectural design and system planning
- **Required for** complex problem-solving and technical decisions
- **Critical for** refactoring, debugging, and deployment planning

## Usage Examples:

```bash
claude /memory-context
claude /memory-context --summary "Architecture planning session"
claude /memory-context --tags "planning,architecture" --type "session"
claude /memory-context --include-files --include-commits
```

## Implementation:

I'll automatically analyze our current session and project state, then store it to your MCP Memory Service at `http://node4.zate.systems:8001/` with API key `2pfUJusKAzyTwrIKGC8KjyuVwOaXcQg1to6q1rzsjKA=`:

1. **Conversation Analysis**: Extract key topics, decisions, and insights from our current chat
2. **Project State Capture**: 
   - Current working directory and git status
   - Recent commits and file changes
   - Branch information and repository state
3. **Context Synthesis**: Combine conversation and project context into a coherent summary
4. **Memory Creation**: Store the context with automatic tags including machine hostname
5. **Auto-Save**: Memory is stored immediately without confirmation prompts

The service uses HTTP with curl and Authorization header for secure communication and automatically detects client hostname using the `X-Client-Hostname` header.

The stored memory will include:
- **Source Machine**: Hostname tag for tracking memory origin (e.g., "source:your-machine-name")
- **Session Summary**: Concise overview of our conversation
- **Key Decisions**: Important choices or conclusions reached
- **Technical Details**: Code changes, configurations, or technical insights
- **Project Context**: Repository state, files modified, current focus
- **Action Items**: Next steps or follow-up tasks identified
- **Timestamp**: When the session context was captured

## Context Elements:

### Conversation Context
- **Topics Discussed**: Main subjects and themes from our chat
- **Problems Solved**: Issues resolved or questions answered
- **Decisions Made**: Choices made or approaches agreed upon
- **Insights Gained**: New understanding or knowledge acquired

### Project Context
- **Repository Info**: Git repository, branch, and recent commits
- **File Changes**: Modified, added, or deleted files
- **Directory Structure**: Current working directory and project layout
- **Development State**: Current development phase or focus area

### Technical Context
- **Code Changes**: Functions, classes, or modules modified
- **Configuration Updates**: Settings, dependencies, or environment changes
- **Architecture Decisions**: Design choices or structural changes
- **Performance Considerations**: Optimization or efficiency insights

## Arguments:

- `$ARGUMENTS` - Optional custom summary or context description
- `--summary "text"` - Custom session summary override
- `--tags "tag1,tag2"` - Additional tags to apply
- `--type "session|meeting|planning|development"` - Context type
- `--include-files` - Include detailed file change information
- `--include-commits` - Include recent commit messages and changes
- `--include-code` - Include snippets of important code changes
- `--private` - Mark as private/sensitive session content
- `--project "name"` - Override project name detection

## Automatic Features:

- **Smart Summarization**: Extract the most important points from our conversation
- **Duplicate Detection**: Avoid storing redundant session information
- **Context Linking**: Connect to related memories and previous sessions
- **Progress Tracking**: Identify progress made since last context capture
- **Knowledge Extraction**: Pull out reusable insights and patterns

This command is especially useful at the end of productive development sessions, after important architectural discussions, or when you want to preserve the current state of your thinking and progress for future reference.