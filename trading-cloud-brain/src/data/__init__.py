"""
📊 Data Module for Axiom Antigravity
Contains data sinks and streaming utilities for BigQuery integration.
"""

from .bq_sink import (
    BigQueryStreamWriter,
    LocalFileSink,
    DataSink,
    get_data_sink,
    init_data_sink,
    BIGQUERY_AVAILABLE
)

__all__ = [
    "BigQueryStreamWriter",
    "LocalFileSink", 
    "DataSink",
    "get_data_sink",
    "init_data_sink",
    "BIGQUERY_AVAILABLE"
]
