# Recall Memories by Time and Context

I'll use the **memory-recall sub-agent** to intelligently retrieve memories using natural language time expressions and contextual queries. This command leverages the autonomous agent system for comprehensive memory retrieval and analysis.

## What I'll do:

I'll immediately invoke the `memory-recall` sub-agent, which will:

1. **Parse Time Expressions**: Interpret natural language queries like "yesterday", "last week", "before the database migration"
2. **Pattern Match Problems**: Connect current challenges with similar historical issues
3. **Solution Context**: Provide information about what worked, what didn't, and why
4. **Historical Analysis**: Gather comprehensive background for informed decision-making
5. **Present Insights**: Format results with actionable recommendations and lessons learned

## Sub-Agent Intelligence:

Instead of basic time-based search, the `memory-recall` sub-agent provides:
- **Smart Pattern Recognition**: Connects current issues with past solutions
- **Solution Effectiveness Analysis**: Information about outcomes and side effects
- **Alternative Approaches**: Multiple solution options with trade-offs
- **Historical Context**: Background knowledge for better decision-making
- **Prevention Strategies**: How to avoid repeating past problems

The sub-agent uses specialized search strategies:
- **Error-Based Retrieval**: Finds similar error patterns and their solutions
- **Solution Pattern Matching**: Identifies proven implementation approaches  
- **Domain Knowledge Assembly**: Gathers expertise and best practices
- **Decision Context Retrieval**: Provides architectural and design decision background

## Usage Examples:

```bash
claude /memory-recall "what did we decide about the database last week?"
claude /memory-recall "similar connection timeout errors"
claude /memory-recall "authentication implementation patterns"
claude /memory-recall --domain "docker deployment" "container configuration"
```

## Time Expression Examples:

- **Relative**: "yesterday", "last week", "two days ago", "this month"
- **Seasonal**: "last summer", "this winter", "spring 2024"

**Note**: Some expressions like "last hour" may not be supported by the time parser. Standard expressions like "today", "yesterday", "last week" work reliably.
- **Event-based**: "before the refactor", "since we switched to SQLite", "during the testing phase"
- **Specific**: "January 15th", "last Tuesday morning", "end of last month"

## Arguments:

- `$ARGUMENTS` - The time-based query, with optional flags:
  - `--limit N` - Maximum number of memories to retrieve (default: 10)
  - `--project "name"` - Filter by specific project
  - `--tags "tag1,tag2"` - Additional tag filtering
  - `--type "note|decision|task"` - Filter by memory type
  - `--include-context` - Show full session context for each memory

If no memories are found for the specified time period, I'll suggest broadening the search or checking if the MCP Memory Service contains data for that timeframe.