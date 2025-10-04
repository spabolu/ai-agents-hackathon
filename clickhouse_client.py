"""
ClickHouse client for AI Agent analytics and logging.

This module provides a centralized client for interacting with ClickHouse,
including connection management, table initialization, and data insertion.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import clickhouse_connect
from dotenv import load_dotenv

# Configuration constants
load_dotenv()

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "ai_agent")


class ClickHouseClient:
    """Singleton client for ClickHouse operations."""

    _instance: Optional[ClickHouseClient] = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Don't connect immediately - lazy initialization
        pass

    @property
    def client(self):
        """Lazy-load the ClickHouse client."""
        if self._client is None:
            self._client = clickhouse_connect.get_client(
                host=CLICKHOUSE_HOST,
                port=CLICKHOUSE_PORT,
                username=CLICKHOUSE_USER,
                password=CLICKHOUSE_PASSWORD,
                database=CLICKHOUSE_DATABASE
            )
        return self._client

    def init_tables(self):
        """Initialize all required ClickHouse tables."""
        self._create_api_requests_table()
        self._create_search_queries_table()
        self._create_image_metrics_table()

    def _create_api_requests_table(self):
        """Create the main API requests logging table."""
        query = """
        CREATE TABLE IF NOT EXISTS api_requests_log (
            id UUID,
            timestamp DateTime64(3),
            api_type String,
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
        PARTITION BY toYYYYMM(timestamp)
        """
        self.client.command(query)

    def _create_search_queries_table(self):
        """Create the search queries analytics table."""
        query = """
        CREATE TABLE IF NOT EXISTS search_queries (
            id UUID,
            timestamp DateTime64(3),
            query_text String,
            api_source String,
            depth Nullable(String),
            output_type Nullable(String),
            result_count Int32,
            response_time_ms Float64,
            success Bool
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, api_source)
        PARTITION BY toYYYYMM(timestamp)
        """
        self.client.command(query)

    def _create_image_metrics_table(self):
        """Create the image generation metrics table."""
        query = """
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
        PARTITION BY toYYYYMM(timestamp)
        """
        self.client.command(query)

    def log_api_request(
        self,
        api_type: str,
        endpoint: str,
        request_method: str,
        request_payload: Dict[str, Any],
        response_status: int,
        response_body: Dict[str, Any],
        response_time_ms: float,
        error_message: Optional[str] = None,
        client_ip: str = "unknown",
        user_agent: str = "unknown"
    ):
        """Log an API request to ClickHouse."""
        data = [[
            str(uuid4()),
            datetime.now(),
            api_type,
            endpoint,
            request_method,
            json.dumps(request_payload),
            response_status,
            json.dumps(response_body),
            response_time_ms,
            error_message,
            client_ip,
            user_agent
        ]]

        self.client.insert(
            'api_requests_log',
            data,
            column_names=[
                'id', 'timestamp', 'api_type', 'endpoint', 'request_method',
                'request_payload', 'response_status', 'response_body',
                'response_time_ms', 'error_message', 'client_ip', 'user_agent'
            ]
        )

    def log_search_query(
        self,
        query_text: str,
        api_source: str,
        depth: Optional[str] = None,
        output_type: Optional[str] = None,
        result_count: int = 0,
        response_time_ms: float = 0.0,
        success: bool = True
    ):
        """Log a search query to ClickHouse."""
        data = [[
            str(uuid4()),
            datetime.now(),
            query_text,
            api_source,
            depth,
            output_type,
            result_count,
            response_time_ms,
            success
        ]]

        self.client.insert(
            'search_queries',
            data,
            column_names=[
                'id', 'timestamp', 'query_text', 'api_source', 'depth',
                'output_type', 'result_count', 'response_time_ms', 'success'
            ]
        )

    def log_image_generation(
        self,
        prompt: str,
        model: str,
        style: str,
        aspect_ratio: str,
        generation_time_ms: float,
        polling_iterations: int = 0,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log image generation metrics to ClickHouse."""
        data = [[
            str(uuid4()),
            datetime.now(),
            prompt,
            model,
            style,
            aspect_ratio,
            generation_time_ms,
            polling_iterations,
            success,
            error_message
        ]]

        self.client.insert(
            'image_generation_metrics',
            data,
            column_names=[
                'id', 'timestamp', 'prompt', 'model', 'style', 'aspect_ratio',
                'generation_time_ms', 'polling_iterations', 'success', 'error_message'
            ]
        )

    def query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        result = self.client.query(sql)
        return result.result_rows

    def get_api_stats(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get API usage statistics for the last N hours."""
        query = f"""
        SELECT
            api_type,
            count() as request_count,
            avg(response_time_ms) as avg_response_time,
            max(response_time_ms) as max_response_time,
            countIf(response_status >= 400) as error_count
        FROM api_requests_log
        WHERE timestamp >= now() - INTERVAL {hours} HOUR
        GROUP BY api_type
        ORDER BY request_count DESC
        """
        return self.query(query)

    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        query = f"""
        SELECT
            query_text,
            api_source,
            count() as query_count,
            avg(response_time_ms) as avg_response_time
        FROM search_queries
        WHERE timestamp >= now() - INTERVAL 7 DAY
        GROUP BY query_text, api_source
        ORDER BY query_count DESC
        LIMIT {limit}
        """
        return self.query(query)

    def get_image_gen_stats(self) -> List[Dict[str, Any]]:
        """Get image generation statistics."""
        query = """
        SELECT
            model,
            style,
            count() as generation_count,
            avg(generation_time_ms) as avg_generation_time,
            countIf(success = 1) as success_count,
            countIf(success = 0) as failure_count
        FROM image_generation_metrics
        WHERE timestamp >= now() - INTERVAL 7 DAY
        GROUP BY model, style
        ORDER BY generation_count DESC
        """
        return self.query(query)


# Singleton instance
clickhouse_client = ClickHouseClient()
