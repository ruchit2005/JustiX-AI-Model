# Docker Quick Start Guide

## Prerequisites
- Docker installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)
- OpenAI API Key

## Quick Start

### 1. Configure Environment
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
notepad .env
```

Make sure your `.env` contains:
```env
OPENAI_API_KEY=sk-your-key-here
```

### 2. Start Services
```bash
# Start both Qdrant and AI Engine
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Test the Service
```bash
# Health check
curl http://localhost:8000/

# Or open in browser
start http://localhost:8000/docs
```

### 4. Stop Services
```bash
# Stop services
docker-compose down

# Stop and remove volumes (delete all data)
docker-compose down -v
```

## Service URLs

- **AI Engine**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Qdrant API**: http://localhost:6333

## Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-engine
docker-compose logs -f qdrant
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart ai-engine
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up -d --build
```

### Access Container Shell
```bash
# AI Engine
docker-compose exec ai-engine /bin/bash

# Qdrant
docker-compose exec qdrant /bin/sh
```

### Check Resource Usage
```bash
docker stats
```

## Troubleshooting

### Port Already in Use
If ports 8000 or 6333 are in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change external port
```

### Container Won't Start
```bash
# Check logs
docker-compose logs ai-engine

# Common issues:
# 1. Missing OPENAI_API_KEY in .env
# 2. Port conflict
# 3. Insufficient memory
```

### Qdrant Connection Error
```bash
# Ensure Qdrant is healthy
docker-compose ps

# Should show:
# verdictech-qdrant   Up (healthy)
```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose up -d --build
```

## Production Deployment

### Use Environment-Specific Compose File
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  ai-engine:
    image: verdictech-ai:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=${QDRANT_CLOUD_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    # Remove volume mount for production
    # Use Qdrant Cloud instead of local Qdrant
```

### Deploy
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

### Health Checks
```bash
# Check health status
docker inspect verdictech-ai-engine | grep -A 5 Health
docker inspect verdictech-qdrant | grep -A 5 Health
```

### Resource Limits
Add to `docker-compose.yml`:
```yaml
services:
  ai-engine:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 1G
```
