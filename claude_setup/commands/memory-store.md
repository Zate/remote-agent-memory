# Store Memory with Context

I'll use the **memory-store sub-agent** to intelligently store information in your MCP Memory Service with proper context and tagging. This command leverages the autonomous agent system for optimal memory storage.

## What I'll do:

I'll immediately invoke the `memory-store` sub-agent, which will:

1. **Analyze Content**: Understand what needs to be stored and classify its importance
2. **Detect Context**: Automatically capture current project, git repository, and session context
3. **Generate Smart Tags**: Add relevant tags based on content analysis and project detection
4. **Store Efficiently**: Use the centralized memory service configuration for secure storage
5. **Provide Feedback**: Confirm storage with content hash and applied tags

## Usage Examples:

```bash
claude /memory-store "We decided to use SQLite-vec instead of ChromaDB for better performance"
claude /memory-store --tags "decision,architecture" "Database backend choice rationale" 
claude /memory-store --type "note" "Remember to update the Docker configuration after the database change"
```

## Sub-Agent Integration:

Instead of making direct API calls, I'll use the `memory-store` sub-agent which:
- **Uses Centralized Config**: Pulls configuration from `~/.claude/memory-service-config.sh`
- **No Hardcoded Values**: Dynamically configured for your memory service setup
- **Enhanced Intelligence**: Leverages past storage patterns and best practices
- **Automatic Context**: Captures project context, git info, and session details
- **Smart Tagging**: Uses established tag patterns and naming conventions

The sub-agent automatically handles:
- **Service Configuration**: Uses your configured memory service endpoint and credentials
- **Error Handling**: Graceful degradation if service is unavailable
- **Content Analysis**: Intelligent classification and metadata generation
- **Tag Management**: Consistent tagging following established patterns
- **Storage Optimization**: Efficient content formatting and duplicate detection

## Arguments:

- `$ARGUMENTS` - The content to store as memory, or additional flags:
  - `--tags "tag1,tag2"` - Explicit tags to add (merged with auto-generated tags)
  - `--type "note|decision|task|reference|architecture"` - Memory type classification
  - `--project "name"` - Override automatic project name detection
  - `--private` - Mark as private/sensitive content
  - `--session` - Store current session summary and context

The memory-store sub-agent will handle all the technical details including service discovery, authentication, and optimal storage formatting. You'll receive confirmation of successful storage with the memory hash and applied tags.