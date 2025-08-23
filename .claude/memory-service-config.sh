#!/bin/bash
# Memory Service Configuration
# Centralized configuration for all Claude Code sub-agents
# This eliminates the need to store API keys and URLs in multiple files

# =============================================================================
# MEMORY SERVICE CONFIGURATION
# =============================================================================

# Memory Service Connection Details
export MEMORY_SERVICE_URL="${MEMORY_SERVICE_URL:-http://localhost:8443}"
export MEMORY_SERVICE_API_KEY="${MEMORY_SERVICE_API_KEY:-}"
export MEMORY_SERVICE_DOMAIN="${MEMORY_SERVICE_DOMAIN:-localhost}"
export CLIENT_HOSTNAME="${CLIENT_HOSTNAME:-$(hostname)}"

# =============================================================================
# CONFIGURATION DETECTION
# =============================================================================

detect_memory_service_config() {
    # Check for config file
    local config_file="$HOME/.claude/memory-service.conf"
    if [[ -f "$config_file" ]]; then
        source "$config_file"
        return 0
    fi
    
    # Check environment variables
    if [[ -n "$MEMORY_SERVICE_URL" && -n "$MEMORY_SERVICE_API_KEY" ]]; then
        return 0
    fi
    
    # Try to detect local service
    if curl -s "$MEMORY_SERVICE_URL/api/health" &>/dev/null; then
        echo "⚠️  Detected memory service at $MEMORY_SERVICE_URL but no API key configured"
        return 1
    fi
    
    echo "❌ No memory service configuration found"
    echo "   Set MEMORY_SERVICE_URL and MEMORY_SERVICE_API_KEY environment variables"
    echo "   Or create ~/.claude/memory-service.conf with these values"
    return 1
}

# =============================================================================
# MEMORY OPERATION FUNCTIONS
# =============================================================================

# Store a memory with automatic error handling
store_memory() {
    local content="$1"
    local tags="$2"
    local metadata="$3"
    local type="${4:-note}"
    
    if ! detect_memory_service_config; then
        echo "❌ Memory service not configured"
        return 1
    fi
    
    # Build JSON payload
    local json_payload
    json_payload=$(cat <<EOF
{
    "content": $(echo "$content" | jq -Rs .),
    "tags": $(echo "$tags" | jq -Rs 'split(",") | map(select(length > 0))'),
    "metadata": {
        "type": "$type",
        "agent": "claude-code-agent",
        "client_hostname": "$CLIENT_HOSTNAME",
        "timestamp": "$(date -Iseconds)",
        "auto_stored": true
        $(if [[ -n "$metadata" ]]; then echo ",$metadata"; fi)
    }
}
EOF
    )
    
    # Store the memory
    local response
    response=$(curl -s -X POST "$MEMORY_SERVICE_URL/api/memories" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MEMORY_SERVICE_API_KEY" \
        -H "X-Client-Hostname: $CLIENT_HOSTNAME" \
        -d "$json_payload" 2>/dev/null)
    
    if [[ $? -eq 0 ]] && echo "$response" | jq -e '.success' &>/dev/null; then
        local content_hash
        content_hash=$(echo "$response" | jq -r '.content_hash // .memory.content_hash // "unknown"')
        echo "✅ Memory stored: $content_hash"
        return 0
    else
        echo "❌ Memory storage failed: $response"
        return 1
    fi
}

# Search memories with automatic error handling
search_memory() {
    local query="$1"
    local limit="${2:-10}"
    local tags="$3"
    
    if ! detect_memory_service_config; then
        echo "❌ Memory service not configured"
        return 1
    fi
    
    local search_url="$MEMORY_SERVICE_URL/api/memories/search"
    local search_params="query=$(echo "$query" | jq -Rs @uri)&limit=$limit"
    
    if [[ -n "$tags" ]]; then
        search_params="$search_params&tags=$tags"
    fi
    
    curl -s "$search_url?$search_params" \
        -H "Authorization: Bearer $MEMORY_SERVICE_API_KEY" \
        -H "X-Client-Hostname: $CLIENT_HOSTNAME"
}

# Get memory service health
get_memory_health() {
    if ! detect_memory_service_config; then
        echo "❌ Memory service not configured"
        return 1
    fi
    
    curl -s "$MEMORY_SERVICE_URL/api/health" \
        -H "Authorization: Bearer $MEMORY_SERVICE_API_KEY" \
        -w "\nResponse Time: %{time_total}s | HTTP Code: %{http_code}\n"
}

# Get memory count
get_memory_count() {
    if ! detect_memory_service_config; then
        echo "❌ Memory service not configured"
        return 1
    fi
    
    curl -s "$MEMORY_SERVICE_URL/api/memories?page_size=1" \
        -H "Authorization: Bearer $MEMORY_SERVICE_API_KEY" \
        | jq -r '.pagination.total // "unknown"' 2>/dev/null || echo "unknown"
}

# =============================================================================
# CONFIGURATION SETUP FUNCTIONS
# =============================================================================

setup_memory_service() {
    echo "🔧 Memory Service Configuration Setup"
    echo "====================================="
    
    local config_file="$HOME/.claude/memory-service.conf"
    
    # Create .claude directory if it doesn't exist
    mkdir -p "$HOME/.claude"
    
    # Prompt for configuration
    read -p "Memory Service URL (e.g., http://localhost:8443): " service_url
    read -s -p "API Key: " api_key
    echo
    
    # Extract domain from URL
    local domain
    domain=$(echo "$service_url" | sed -E 's|https?://([^:/]+).*|\1|')
    
    # Write configuration file
    cat > "$config_file" <<EOF
# Memory Service Configuration
# Generated on $(date)
export MEMORY_SERVICE_URL="$service_url"
export MEMORY_SERVICE_API_KEY="$api_key"
export MEMORY_SERVICE_DOMAIN="$domain"
export CLIENT_HOSTNAME="$(hostname)"
EOF
    
    # Secure the config file
    chmod 600 "$config_file"
    
    echo "✅ Configuration saved to $config_file"
    
    # Test the configuration
    echo "🧪 Testing connection..."
    source "$config_file"
    
    if get_memory_health &>/dev/null; then
        echo "✅ Memory service connection successful!"
    else
        echo "⚠️  Could not connect to memory service. Please verify your configuration."
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# If script is executed directly, show configuration status
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-status}" in
        "setup")
            setup_memory_service
            ;;
        "test")
            echo "🧪 Testing Memory Service Configuration"
            echo "======================================"
            if detect_memory_service_config; then
                echo "✅ Configuration found"
                echo "   URL: $MEMORY_SERVICE_URL"
                echo "   Domain: $MEMORY_SERVICE_DOMAIN" 
                echo "   Client: $CLIENT_HOSTNAME"
                echo ""
                get_memory_health
            fi
            ;;
        "health")
            get_memory_health
            ;;
        "count")
            echo "Total memories: $(get_memory_count)"
            ;;
        *)
            echo "Memory Service Configuration Script"
            echo "Usage: $0 [setup|test|health|count]"
            echo ""
            echo "Commands:"
            echo "  setup  - Configure memory service connection"
            echo "  test   - Test current configuration" 
            echo "  health - Check memory service health"
            echo "  count  - Get total memory count"
            echo ""
            echo "Functions available when sourced:"
            echo "  store_memory <content> <tags> [metadata] [type]"
            echo "  search_memory <query> [limit] [tags]"
            echo "  get_memory_health"
            echo "  get_memory_count"
            ;;
    esac
fi