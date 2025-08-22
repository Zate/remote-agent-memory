# Docker Stack Deployment Guide for MCP Memory Service

This guide provides complete instructions for deploying the MCP Memory Service on Docker Swarm for remote AI agent access.

## Overview

The MCP Memory Service is a semantic memory system that provides:
- **Semantic memory storage** with vector embeddings
- **Multiple storage backends**: SQLite-Vec (recommended), ChromaDB, Cloudflare
- **HTTP/REST API** for remote access
- **Web dashboard** for memory management
- **Multi-client support** with API key authentication
- **Real-time Server-Sent Events (SSE)** for live updates

## Prerequisites

- Docker Swarm cluster initialized
- Docker registry access (Docker Hub or private registry)
- SSL certificates (optional, service can generate self-signed)
- Network access to target deployment hosts

## Quick Deployment

### 1. Create API Key Secret

```bash
# Generate and store secure API key
echo "$(openssl rand -base64 32)" | docker secret create mcp_api_key -

# Verify secret creation
docker secret ls
```

### 2. Deploy Stack

```bash
# Save the stack configuration below as docker-stack-mcp.yml
# Deploy to swarm
docker stack deploy -c docker-stack-mcp.yml mcp-memory

# Verify deployment
docker stack services mcp-memory
docker service ps mcp-memory_mcp-memory-service
```

## Production Stack Configuration

Save as `docker-stack-mcp.yml`:

```yaml
version: '3.8'

services:
  mcp-memory-service:
    image: mcp-memory-service:latest
    ports:
      - "8443:8443"  # HTTPS port for secure remote access
      - "8000:8000"  # HTTP port for API access
    environment:
      # === CORE CONFIGURATION ===
      - MCP_MODE=http
      - MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
      
      # === HTTP/HTTPS SETTINGS ===
      - MCP_HTTP_ENABLED=true
      - MCP_HTTP_HOST=0.0.0.0
      - MCP_HTTP_PORT=8000
      - MCP_HTTPS_ENABLED=true
      - MCP_HTTPS_PORT=8443
      - MCP_HTTP_AUTO_START=true
      
      # === SECURITY ===
      - MCP_API_KEY_FILE=/run/secrets/mcp_api_key
      
      # === STORAGE CONFIGURATION ===
      - MCP_MEMORY_SQLITE_PATH=/app/data/sqlite_vec.db
      - MCP_MEMORY_BACKUPS_PATH=/app/data/backups
      
      # === PERFORMANCE TUNING ===
      - LOG_LEVEL=INFO
      - MAX_RESULTS_PER_QUERY=100
      - SIMILARITY_THRESHOLD=0.7
      
      # === SERVICE DISCOVERY ===
      - MCP_MDNS_ENABLED=true
      - MCP_MDNS_SERVICE_NAME=MCP Memory Service - Production
      - MCP_MEMORY_INCLUDE_HOSTNAME=true
      
      # === MEMORY CONSOLIDATION ===
      - MCP_CONSOLIDATION_ENABLED=true
      - MCP_CONSOLIDATION_INTERVAL=24
      - MCP_CONSOLIDATION_MIN_MEMORIES=100
      
      # === PYTHON CONFIGURATION ===
      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app/src
      - PYTORCH_ENABLE_MPS_FALLBACK=1
      - HF_HUB_OFFLINE=1
      - TRANSFORMERS_OFFLINE=1
    
    volumes:
      - memory_data:/app/data
      - memory_backups:/app/data/backups
    
    secrets:
      - mcp_api_key
    
    networks:
      - mcp_network
    
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == worker
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 60s
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        monitor: 60s
      rollback_config:
        parallelism: 1
        delay: 10s
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.mcp-memory.rule=Host(`memory.yourdomain.com`)"
        - "traefik.http.services.mcp-memory.loadbalancer.server.port=8443"
    
    healthcheck:
      test: ["CMD", "curl", "-f", "-k", "https://localhost:8443/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Optional: Nginx reverse proxy for advanced load balancing
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - nginx_config:/etc/nginx/conf.d:ro
      - ssl_certs:/etc/nginx/certs:ro
    configs:
      - source: nginx_conf
        target: /etc/nginx/conf.d/default.conf
    networks:
      - mcp_network
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    depends_on:
      - mcp-memory-service

volumes:
  memory_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/mcp-memory/data
  memory_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/mcp-memory/backups
  nginx_config:
    driver: local
  ssl_certs:
    driver: local

networks:
  mcp_network:
    driver: overlay
    attachable: true
    ipam:
      config:
        - subnet: 10.1.0.0/24

secrets:
  mcp_api_key:
    external: true

configs:
  nginx_conf:
    external: true
```

## Nginx Configuration

Create nginx config and add to Docker config:

```bash
# Create nginx configuration
cat > nginx.conf << 'EOF'
upstream mcp_backend {
    least_conn;
    server mcp-memory-service:8443 max_fails=3 fail_timeout=30s backup;
    server mcp-memory-service:8000 max_fails=3 fail_timeout=30s;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name _;
    
    # SSL configuration
    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Proxy configuration
    location / {
        proxy_pass https://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Authorization $http_authorization;
        
        # WebSocket support for SSE
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass https://mcp_backend/api/health;
    }
}
EOF

# Add to Docker config
docker config create nginx_conf nginx.conf
```

## Pre-Deployment Setup

### 1. Create Required Directories

```bash
# Create data directories on Docker nodes
sudo mkdir -p /opt/mcp-memory/{data,backups}
sudo chown -R 1000:1000 /opt/mcp-memory
sudo chmod -R 755 /opt/mcp-memory
```

### 2. Build and Push Docker Image

```bash
# Build the image
docker build -t mcp-memory-service:latest .

# Tag for registry (replace with your registry)
docker tag mcp-memory-service:latest your-registry/mcp-memory-service:latest

# Push to registry
docker push your-registry/mcp-memory-service:latest
```

### 3. Network Configuration

```bash
# Create overlay network (if not using stack file)
docker network create --driver overlay --attachable mcp_network

# Configure firewall rules
sudo ufw allow 8443/tcp comment "MCP Memory HTTPS"
sudo ufw allow 8000/tcp comment "MCP Memory HTTP" 
sudo ufw allow 443/tcp comment "Nginx HTTPS"
sudo ufw allow 80/tcp comment "Nginx HTTP redirect"
```

## Remote Access Configuration

### REST API Access

```bash
# Get API key from secret
API_KEY=$(docker secret inspect mcp_api_key --format='{{.Spec.Data}}' | base64 -d)

# Health check
curl -k -H "Authorization: Bearer $API_KEY" \
  https://your-swarm-host:8443/api/health

# Store memory
curl -k -X POST https://your-swarm-host:8443/api/memories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "content": "Important project information",
    "tags": ["project", "notes", "ai-agent"],
    "metadata": {
      "type": "note",
      "priority": "high",
      "source": "ai-agent"
    }
  }'

# Search memories
curl -k -G "https://your-swarm-host:8443/api/memories/search" \
  -H "Authorization: Bearer $API_KEY" \
  -d "query=project information" \
  -d "limit=10" \
  -d "tags=ai-agent,project"

# Get all memories with pagination
curl -k -G "https://your-swarm-host:8443/api/memories" \
  -H "Authorization: Bearer $API_KEY" \
  -d "limit=50" \
  -d "offset=0"

# Delete memory by hash
curl -k -X DELETE "https://your-swarm-host:8443/api/memories/{memory_hash}" \
  -H "Authorization: Bearer $API_KEY"

# Bulk delete by tags
curl -k -X DELETE "https://your-swarm-host:8443/api/memories/by-tags" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"tags": ["temporary", "outdated"]}'
```

### Web Dashboard Access

Access the web interface at:
- **HTTPS**: `https://your-swarm-host:8443/`
- **HTTP**: `http://your-swarm-host:8000/` (redirects to HTTPS)

Features available:
- Memory search and filtering
- Real-time memory additions
- Tag management
- Memory export/import
- System health monitoring
- Database statistics

### Server-Sent Events (SSE)

For real-time updates in AI applications:

```javascript
// Connect to SSE endpoint
const eventSource = new EventSource(
  'https://your-swarm-host:8443/api/events',
  {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    }
  }
);

// Handle memory events
eventSource.addEventListener('memory_stored', (event) => {
  const memory = JSON.parse(event.data);
  console.log('New memory stored:', memory);
});

eventSource.addEventListener('memory_deleted', (event) => {
  const { hash } = JSON.parse(event.data);
  console.log('Memory deleted:', hash);
});

// Handle errors
eventSource.onerror = (error) => {
  console.error('SSE connection error:', error);
};
```

### MCP Protocol Integration

For Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "memory": {
      "command": "curl",
      "args": [
        "-X", "POST", 
        "https://your-swarm-host:8443/mcp",
        "-H", "Authorization: Bearer YOUR_API_KEY",
        "-H", "Content-Type: application/json"
      ]
    }
  }
}
```

## Management Commands

### Service Management

```bash
# Check service status
docker stack services mcp-memory

# View service logs
docker service logs mcp-memory_mcp-memory-service --follow

# Scale service
docker service scale mcp-memory_mcp-memory-service=3

# Update service image
docker service update --image your-registry/mcp-memory-service:v2 \
  mcp-memory_mcp-memory-service

# Restart service
docker service update --force mcp-memory_mcp-memory-service

# Remove stack
docker stack rm mcp-memory
```

### Health Monitoring

```bash
# Check all service health
docker stack ps mcp-memory

# Test API health
curl -k https://your-swarm-host:8443/api/health

# Check service stats
curl -k -H "Authorization: Bearer $API_KEY" \
  https://your-swarm-host:8443/api/status

# Monitor resource usage
docker stats $(docker ps -q --filter "label=com.docker.stack.namespace=mcp-memory")
```

### Database Management

```bash
# Backup memories
docker exec $(docker ps -q -f name=mcp-memory_mcp-memory-service) \
  python scripts/backup_memories.py

# Check database health
docker exec $(docker ps -q -f name=mcp-memory_mcp-memory-service) \
  python -c "
from src.mcp_memory_service.storage.sqlite_vec import SqliteVecStorage
storage = SqliteVecStorage()
print('Database health check passed')
"

# Optimize database
curl -k -X POST https://your-swarm-host:8443/mcp \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "optimize_db",
      "arguments": {}
    }
  }'
```

## Security Best Practices

### 1. API Key Management

```bash
# Rotate API key
NEW_API_KEY=$(openssl rand -base64 32)
echo "$NEW_API_KEY" | docker secret create mcp_api_key_v2 -
docker service update --secret-rm mcp_api_key --secret-add mcp_api_key_v2 \
  mcp-memory_mcp-memory-service
```

### 2. Network Security

```bash
# Restrict network access (example with iptables)
sudo iptables -A INPUT -p tcp --dport 8443 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8443 -j DROP

# Use Docker secrets for sensitive data
echo "sensitive-config-value" | docker secret create app_config -
```

### 3. SSL/TLS Configuration

The service automatically generates self-signed certificates. For production, mount custom certificates:

```yaml
# Add to service volumes
volumes:
  - ssl_certs:/app/certs:ro

# Environment variables for custom certs
environment:
  - MCP_SSL_CERT_FILE=/app/certs/cert.pem
  - MCP_SSL_KEY_FILE=/app/certs/key.pem
```

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check service logs
docker service logs mcp-memory_mcp-memory-service

# Check node constraints
docker node ls
docker service ps mcp-memory_mcp-memory-service
```

**Memory/Performance issues:**
```bash
# Check resource usage
docker stats $(docker ps -q --filter "label=com.docker.stack.namespace=mcp-memory")

# Adjust resource limits in stack file
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4.0'
```

**Database connectivity:**
```bash
# Test database connection
docker exec -it $(docker ps -q -f name=mcp-memory_mcp-memory-service) bash
python -c "from src.mcp_memory_service.storage.sqlite_vec import SqliteVecStorage; SqliteVecStorage()"
```

**API authentication:**
```bash
# Verify API key
docker secret inspect mcp_api_key

# Test API access
curl -k -v -H "Authorization: Bearer $API_KEY" \
  https://your-swarm-host:8443/api/health
```

### Performance Tuning

```yaml
# High-performance configuration additions
environment:
  # Increase worker processes
  - UVICORN_WORKERS=4
  
  # Optimize embedding cache
  - MCP_MEMORY_EMBEDDING_CACHE_SIZE=2000
  
  # Enable query result caching
  - MCP_MEMORY_QUERY_CACHE_TTL=3600
  
  # SQLite optimizations
  - SQLITE_VEC_BATCH_SIZE=200
  - SQLITE_VEC_CACHE_SIZE=4000

# Resource adjustments
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
    reservations:
      cpus: '2.0'
      memory: 4G
```

## Monitoring and Alerting

### Prometheus Integration

```yaml
# Add to docker-stack-mcp.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - prometheus_config:/etc/prometheus
    networks:
      - mcp_network
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
```

### Health Check Automation

```bash
#!/bin/bash
# save as check_mcp_health.sh
API_KEY="your-api-key"
ENDPOINT="https://your-swarm-host:8443/api/health"

response=$(curl -k -s -H "Authorization: Bearer $API_KEY" "$ENDPOINT")
status=$(echo "$response" | jq -r '.status // "unknown"')

if [ "$status" != "healthy" ]; then
    echo "MCP Memory Service unhealthy: $response"
    # Add alerting logic here
    exit 1
fi

echo "MCP Memory Service healthy"
```

## Backup and Recovery

### Automated Backup

```bash
#!/bin/bash
# save as backup_mcp_memories.sh
BACKUP_DIR="/opt/mcp-memory/backups"
DATE=$(date +%Y%m%d_%H%M%S)
API_KEY="your-api-key"

# Create backup via API
curl -k -X POST "https://your-swarm-host:8443/api/backup" \
  -H "Authorization: Bearer $API_KEY" \
  -o "$BACKUP_DIR/memories_backup_$DATE.json"

# Compress and archive
gzip "$BACKUP_DIR/memories_backup_$DATE.json"

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "memories_backup_*.json.gz" -mtime +7 -delete
```

### Disaster Recovery

```bash
# Export all memories
docker exec $(docker ps -q -f name=mcp-memory_mcp-memory-service) \
  python scripts/backup_memories.py --format json --output /app/data/full_backup.json

# Copy backup off-site
docker cp $(docker ps -q -f name=mcp-memory_mcp-memory-service):/app/data/full_backup.json ./

# Restore from backup
docker cp ./full_backup.json $(docker ps -q -f name=mcp-memory_mcp-memory-service):/app/data/
docker exec $(docker ps -q -f name=mcp-memory_mcp-memory-service) \
  python scripts/restore_memories.py /app/data/full_backup.json
```

This configuration provides a production-ready, scalable MCP Memory Service deployment suitable for AI agent remote access with comprehensive monitoring, security, and maintenance capabilities.