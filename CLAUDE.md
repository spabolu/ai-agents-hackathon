# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Task Agent hackathon project that integrates:
- **Perplexity API** for search and query capabilities via FastAPI endpoint
- **Freepik API** for AI-powered text-to-image generation (Imagen3)

The project consists of two main Python scripts:
- `main.py` - FastAPI server with Perplexity search endpoint
- `freepik.py` - Standalone image generation script using Freepik API

## Commands

### Development

```bash
# Install dependencies with uv (preferred)
uv pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000

# Run with reload for development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Test the API endpoint
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query"}'

# Generate an image using Freepik
python freepik.py
```

### Docker

```bash
# Build the Docker image
docker build -t ai-task-agent .

# Run the container
docker run -p 8000:8000 ai-task-agent
```

## Environment Configuration

Required API keys in `.env`:
- `PERPLEXITY_API_KEY` - For Perplexity search API
- `FREEPIK_API_KEY` - For Freepik image generation API

## Architecture Notes

### FastAPI Server (main.py)
- Single POST endpoint `/search` that proxies queries to Perplexity API
- Uses model: `llama-3-sonar-large-32k-online`
- Returns JSON response from Perplexity API
- Root endpoint `/` for health checks

### Freepik Image Generator (freepik.py)
- Synchronous polling-based implementation (checks every 2 seconds)
- 5-minute timeout for image generation
- Generates images using Imagen3 model
- Configurable styling options (style, effects, lighting, framing)
- Downloads completed images to `generated_image.jpg` in script directory
- Safety settings: blocks medium and above harmful content
- Person generation: disabled by default

### Key Integration Points
Both scripts use:
- `requests` library for HTTP calls
- `python-dotenv` for environment variable management
- Direct API authentication via headers

## ClickHouse Analytics Integration

### Overview
The project includes a ClickHouse analytics system for logging and analyzing all API requests, search queries, and image generation metrics.

### Setup with Docker Compose

```bash
# Start all services (FastAPI + ClickHouse)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Environment Variables for ClickHouse

Add to `.env`:
```
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=ai_agent
```

### Database Schema

**Tables:**
1. `api_requests_log` - All API requests with timing and status
2. `search_queries` - Search-specific analytics (Perplexity + Linkup)
3. `image_generation_metrics` - Image generation performance tracking

### Analytics Endpoints

```bash
# Initialize ClickHouse tables (run once)
curl -X POST http://localhost:8000/analytics/init-tables

# Get API usage statistics (last 24 hours)
curl http://localhost:8000/analytics/api-stats?hours=24

# Get popular search queries
curl http://localhost:8000/analytics/popular-searches?limit=10

# Get image generation statistics
curl http://localhost:8000/analytics/image-stats
```

### ClickHouse Client Module

- **Location**: `clickhouse_client.py`
- **Singleton pattern**: Use `clickhouse_client` instance
- **Auto-logging**: Middleware automatically logs all API requests
- **Manual logging**: Use `clickhouse_client.log_search_query()` or `clickhouse_client.log_image_generation()`

### Direct ClickHouse Access

```bash
# Connect to ClickHouse CLI (when running in Docker)
docker exec -it ai-agent-clickhouse clickhouse-client --database=ai_agent

# Query examples:
SELECT * FROM api_requests_log ORDER BY timestamp DESC LIMIT 10;
SELECT query_text, count() FROM search_queries GROUP BY query_text;
SELECT model, avg(generation_time_ms) FROM image_generation_metrics GROUP BY model;
```

## Important Notes

- **Dependencies**: Includes `clickhouse-connect` for ClickHouse integration
- **Image Output**: freepik.py saves to `generated_image.jpg` in script directory
- **API Models**: Perplexity uses `llama-3-sonar-large-32k-online`, Freepik uses Imagen3/Gemini 2.5 Flash
- **Freepik Polling**: 2-second intervals with 5-minute timeout hardcoded at top of script
- **ClickHouse Optional**: App runs without ClickHouse; gracefully degrades if unavailable
