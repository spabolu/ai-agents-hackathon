# ClickHouse Analytics Integration

## Overview

This project includes a comprehensive ClickHouse analytics system that logs and analyzes all API requests, search queries, and image generation metrics from the AI Agent platform.

## Features

- **Automatic Request Logging**: Middleware automatically logs all API requests with timing, status codes, and payloads
- **Search Analytics**: Track and analyze search queries from Perplexity and Linkup APIs
- **Image Generation Metrics**: Monitor Freepik/Gemini image generation performance
- **Analytics Endpoints**: Query aggregated statistics via REST API
- **Graceful Degradation**: Application runs normally even if ClickHouse is unavailable

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f fastapi

# Initialize ClickHouse tables (first time only)
curl -X POST http://localhost:8000/analytics/init-tables

# Test the analytics
curl http://localhost:8000/analytics/api-stats
```

### Option 2: Manual Setup

1. **Install and start ClickHouse**:
   ```bash
   # macOS with Homebrew
   brew install clickhouse
   clickhouse server

   # Or use Docker
   docker run -d -p 8123:8123 -p 9000:9000 --name clickhouse clickhouse/clickhouse-server:24.1
   ```

2. **Install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Configure environment** (`.env`):
   ```bash
   CLICKHOUSE_HOST=localhost
   CLICKHOUSE_PORT=8123
   CLICKHOUSE_USER=default
   CLICKHOUSE_PASSWORD=
   CLICKHOUSE_DATABASE=ai_agent
   ```

4. **Initialize tables and start server**:
   ```bash
   # Start FastAPI
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   # Initialize ClickHouse tables
   curl -X POST http://localhost:8000/analytics/init-tables
   ```

## Database Schema

### Tables

#### 1. `api_requests_log`
Logs all API requests with full context:
- `id` - UUID
- `timestamp` - DateTime64(3)
- `api_type` - Enum ('perplexity', 'freepik', 'linkup')
- `endpoint` - String
- `request_method` - String
- `request_payload` - JSON String
- `response_status` - Int32
- `response_body` - JSON String
- `response_time_ms` - Float64
- `error_message` - Nullable(String)
- `client_ip` - String
- `user_agent` - String

**Partitioning**: By month (`toYYYYMM(timestamp)`)
**Ordering**: `(timestamp, api_type)`

#### 2. `search_queries`
Search-specific analytics:
- `id` - UUID
- `timestamp` - DateTime64(3)
- `query_text` - String
- `api_source` - Enum ('perplexity', 'linkup')
- `depth` - Nullable(String)
- `output_type` - Nullable(String)
- `result_count` - Int32
- `response_time_ms` - Float64
- `success` - Bool

**Partitioning**: By month
**Ordering**: `(timestamp, api_source)`

#### 3. `image_generation_metrics`
Image generation performance tracking:
- `id` - UUID
- `timestamp` - DateTime64(3)
- `prompt` - String
- `model` - String
- `style` - String
- `aspect_ratio` - String
- `generation_time_ms` - Float64
- `polling_iterations` - Int32
- `success` - Bool
- `error_message` - Nullable(String)

**Partitioning**: By month
**Ordering**: `(timestamp, model)`

## API Endpoints

### Analytics Endpoints

#### 1. Initialize Tables
```bash
POST /analytics/init-tables
```
Creates all required ClickHouse tables. Run once on first setup.

#### 2. API Statistics
```bash
GET /analytics/api-stats?hours=24
```
Returns usage statistics for all APIs:
- Request count by API type
- Average/max response times
- Error counts

**Response**:
```json
{
  "stats": [
    {
      "api_type": "perplexity",
      "request_count": 150,
      "avg_response_time": 245.5,
      "max_response_time": 1203.0,
      "error_count": 2
    }
  ],
  "period_hours": 24
}
```

#### 3. Popular Searches
```bash
GET /analytics/popular-searches?limit=10
```
Returns most frequent search queries from the last 7 days.

**Response**:
```json
{
  "searches": [
    {
      "query_text": "What is AI?",
      "api_source": "perplexity",
      "query_count": 45,
      "avg_response_time": 320.5
    }
  ]
}
```

#### 4. Image Generation Stats
```bash
GET /analytics/image-stats
```
Returns image generation statistics grouped by model and style.

**Response**:
```json
{
  "stats": [
    {
      "model": "gemini-2-5-flash",
      "style": "studio-shot",
      "generation_count": 23,
      "avg_generation_time": 12500.0,
      "success_count": 22,
      "failure_count": 1
    }
  ]
}
```

## Direct ClickHouse Queries

### Connect to CLI
```bash
# If using Docker
docker exec -it ai-agent-clickhouse clickhouse-client --database=ai_agent

# If installed locally
clickhouse-client --database=ai_agent
```

### Example Queries

```sql
-- View recent API requests
SELECT
    timestamp,
    api_type,
    endpoint,
    response_time_ms,
    response_status
FROM api_requests_log
ORDER BY timestamp DESC
LIMIT 10;

-- Analyze search patterns
SELECT
    query_text,
    count() as frequency,
    avg(response_time_ms) as avg_time
FROM search_queries
WHERE timestamp >= now() - INTERVAL 7 DAY
GROUP BY query_text
ORDER BY frequency DESC
LIMIT 20;

-- Image generation performance by model
SELECT
    model,
    count() as total_generations,
    avg(generation_time_ms) as avg_time,
    max(generation_time_ms) as max_time,
    countIf(success = 1) as successful
FROM image_generation_metrics
WHERE timestamp >= now() - INTERVAL 7 DAY
GROUP BY model;

-- API error analysis
SELECT
    api_type,
    endpoint,
    count() as error_count,
    groupArray(error_message) as errors
FROM api_requests_log
WHERE response_status >= 400
  AND timestamp >= now() - INTERVAL 24 HOUR
GROUP BY api_type, endpoint;

-- Hourly request volume
SELECT
    toStartOfHour(timestamp) as hour,
    api_type,
    count() as requests,
    avg(response_time_ms) as avg_response_time
FROM api_requests_log
WHERE timestamp >= now() - INTERVAL 24 HOUR
GROUP BY hour, api_type
ORDER BY hour DESC;
```

## Python Client Usage

### Manual Logging

```python
from clickhouse_client import clickhouse_client

# Log a search query
clickhouse_client.log_search_query(
    query_text="What is machine learning?",
    api_source="perplexity",
    result_count=5,
    response_time_ms=234.5,
    success=True
)

# Log image generation
clickhouse_client.log_image_generation(
    prompt="A beautiful sunset",
    model="gemini-2-5-flash",
    style="photo",
    aspect_ratio="16:9",
    generation_time_ms=15000.0,
    polling_iterations=8,
    success=True
)

# Custom queries
results = clickhouse_client.query(
    "SELECT * FROM api_requests_log WHERE api_type = 'perplexity' LIMIT 10"
)
for row in results:
    print(row)
```

### Automatic Logging

The FastAPI middleware automatically logs:
- All HTTP requests (except `/`, `/docs`, `/openapi.json`)
- Request/response timing
- Error conditions
- Client information

No manual logging needed for API requests!

## Performance Considerations

### Partitioning
All tables are partitioned by month (`toYYYYMM(timestamp)`) to optimize:
- Query performance for time-range queries
- Data lifecycle management
- Storage efficiency

### Indexing
Tables use MergeTree engine with optimal ordering keys:
- `(timestamp, api_type)` for api_requests_log
- `(timestamp, api_source)` for search_queries
- `(timestamp, model)` for image_generation_metrics

### Data Retention

To configure automatic data cleanup, add TTL to tables:

```sql
ALTER TABLE api_requests_log
MODIFY TTL timestamp + INTERVAL 90 DAY;

ALTER TABLE search_queries
MODIFY TTL timestamp + INTERVAL 180 DAY;

ALTER TABLE image_generation_metrics
MODIFY TTL timestamp + INTERVAL 365 DAY;
```

## Troubleshooting

### ClickHouse not connecting
1. Verify ClickHouse is running: `docker ps` or `ps aux | grep clickhouse`
2. Check connection settings in `.env`
3. Test connection: `curl http://localhost:8123/ping`

### Tables not initializing
```bash
# Check ClickHouse logs
docker logs ai-agent-clickhouse

# Manually create database
docker exec -it ai-agent-clickhouse clickhouse-client --query "CREATE DATABASE IF NOT EXISTS ai_agent"

# Re-run initialization
curl -X POST http://localhost:8000/analytics/init-tables
```

### FastAPI not logging to ClickHouse
1. Check that CLICKHOUSE_ENABLED is True: `curl http://localhost:8000/` (look for `clickhouse_enabled`)
2. Review FastAPI logs for connection errors
3. Verify tables exist: `docker exec -it ai-agent-clickhouse clickhouse-client --query "SHOW TABLES FROM ai_agent"`

## Architecture Notes

- **Lazy Connection**: ClickHouse client only connects when first used
- **Graceful Degradation**: App runs normally if ClickHouse unavailable
- **Singleton Pattern**: Single shared ClickHouse client instance
- **Async Middleware**: Non-blocking request logging
- **Error Handling**: All ClickHouse operations wrapped in try/except

## Future Enhancements

Potential additions:
- Real-time dashboards (Grafana integration)
- Alert system for anomalies
- A/B testing analytics
- User segmentation analysis
- Cost tracking per API
- ML-based usage predictions
