#!/bin/bash
set -e

# Wait for ClickHouse to be ready
sleep 5

# Create database
clickhouse-client --query "CREATE DATABASE IF NOT EXISTS ai_agent;"

# Create tables
clickhouse-client --database=ai_agent --query "
CREATE TABLE IF NOT EXISTS api_requests_log (
    id UUID,
    timestamp DateTime64(3),
    api_type Enum8('perplexity' = 1, 'freepik' = 2, 'linkup' = 3),
    endpoint String,
    request_method String,
    request_payload String,
    response_status Int32,
    response_body String,
    response_time_ms Float64,
    error_message Nullable(String),
    client_ip String,
    user_agent String
) ENGINE = MergeTree()
ORDER BY (timestamp, api_type)
PARTITION BY toYYYYMM(timestamp);
"

clickhouse-client --database=ai_agent --query "
CREATE TABLE IF NOT EXISTS search_queries (
    id UUID,
    timestamp DateTime64(3),
    query_text String,
    api_source Enum8('perplexity' = 1, 'linkup' = 2),
    depth Nullable(String),
    output_type Nullable(String),
    result_count Int32,
    response_time_ms Float64,
    success Bool
) ENGINE = MergeTree()
ORDER BY (timestamp, api_source)
PARTITION BY toYYYYMM(timestamp);
"

clickhouse-client --database=ai_agent --query "
CREATE TABLE IF NOT EXISTS image_generation_metrics (
    id UUID,
    timestamp DateTime64(3),
    prompt String,
    model String,
    style String,
    aspect_ratio String,
    generation_time_ms Float64,
    polling_iterations Int32,
    success Bool,
    error_message Nullable(String)
) ENGINE = MergeTree()
ORDER BY (timestamp, model)
PARTITION BY toYYYYMM(timestamp);
"

echo "ClickHouse tables initialized successfully!"
