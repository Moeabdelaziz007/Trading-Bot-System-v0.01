"""
📊 BigQuery Storage Write API Sink for Axiom Antigravity
Streams trade data and logs to BigQuery using the gRPC Storage Write API.

**Zero-Cost Design:**
- Uses Storage Write API (Default Stream) instead of tabledata.insertAll
- Batches writes to minimize API calls
- Async flush decoupled from trading logic

**Requirements:**
- google-cloud-bigquery-storage>=2.0.0
- protobuf>=3.20.0
- Service account with BigQuery Data Editor role

**Schema (Proto3-like):**
- timestamp: TIMESTAMP
- level: STRING
- event: STRING  
- module: STRING
- context: JSON (as STRING)
"""

import os
import json
import threading
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import deque

# BigQuery imports (optional - graceful fallback)
try:
    from google.cloud import bigquery_storage_v1
    from google.cloud.bigquery_storage_v1 import types as bq_types
    from google.protobuf import descriptor_pb2
    from google.api_core.exceptions import GoogleAPIError
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False


class BigQueryStreamWriter:
    """
    Async writer using BigQuery Storage Write API (Default Stream).
    
    Default Stream provides:
    - At-least-once delivery
    - Auto-scaling
    - No explicit stream creation needed
    
    Usage:
        writer = BigQueryStreamWriter("project.dataset.table")
        writer.append({"event": "trade", "symbol": "BTCUSD", ...})
        await writer.flush()  # Call periodically or on shutdown
    """
    
    def __init__(
        self,
        table_path: str,
        batch_size: int = 100,
        flush_interval: float = 5.0,
        credentials_json: Optional[str] = None
    ):
        """
        Initialize the BigQuery stream writer.
        
        Args:
            table_path: Full table path (project.dataset.table)
            batch_size: Max rows per batch before auto-flush
            flush_interval: Seconds between auto-flush attempts
            credentials_json: Optional JSON string for service account
        """
        self.table_path = table_path
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self._buffer: deque = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._client = None
        self._write_stream = None
        self._last_flush = time.time()
        
        # Parse table path
        parts = table_path.split(".")
        if len(parts) == 3:
            self.project, self.dataset, self.table = parts
        else:
            raise ValueError(f"Invalid table path: {table_path}. Expected: project.dataset.table")
        
        # Initialize client if BigQuery is available
        if BIGQUERY_AVAILABLE:
            self._init_client(credentials_json)
    
    def _init_client(self, credentials_json: Optional[str] = None) -> None:
        """Initialize BigQuery Storage client."""
        try:
            if credentials_json:
                # Use provided credentials JSON
                import google.auth
                from google.oauth2 import service_account
                
                creds_dict = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
                self._client = bigquery_storage_v1.BigQueryWriteClient(credentials=credentials)
            else:
                # Use default credentials (ADC)
                self._client = bigquery_storage_v1.BigQueryWriteClient()
            
            # Get default stream path
            self._parent = f"projects/{self.project}/datasets/{self.dataset}/tables/{self.table}"
            
        except Exception as e:
            print(f"[WARN] BigQuery client init failed: {e}. Logs will be buffered only.")
            self._client = None
    
    def append(self, row: Dict[str, Any]) -> None:
        """
        Add a row to the buffer.
        
        Args:
            row: Dictionary with log/trade data
        """
        # Normalize row to match BigQuery schema
        normalized = {
            "timestamp": row.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "level": str(row.get("level", "INFO")),
            "event": str(row.get("event", "LOG")),
            "module": str(row.get("module", "unknown")),
            "context": json.dumps(row.get("context", {}), default=str)
        }
        
        with self._lock:
            self._buffer.append(normalized)
        
        # Auto-flush if batch size reached
        if len(self._buffer) >= self.batch_size:
            self._try_flush()
    
    def _try_flush(self) -> int:
        """Attempt to flush buffer (non-blocking)."""
        if not self._client or len(self._buffer) == 0:
            return 0
        
        # Get rows to flush
        with self._lock:
            rows = list(self._buffer)
            self._buffer.clear()
        
        if not rows:
            return 0
        
        try:
            return self._write_rows(rows)
        except Exception as e:
            print(f"[ERROR] BigQuery flush failed: {e}")
            # Put rows back in buffer
            with self._lock:
                for row in rows:
                    self._buffer.appendleft(row)
            return 0
    
    def _write_rows(self, rows: List[Dict[str, Any]]) -> int:
        """
        Write rows to BigQuery using Storage Write API.
        
        Uses the default stream for simplicity and at-least-once delivery.
        """
        if not self._client:
            return 0
        
        try:
            # Convert rows to JSON strings for the proto payload
            serialized_rows = []
            for row in rows:
                # Create ProtoRows format
                serialized_rows.append(json.dumps(row, default=str).encode("utf-8"))
            
            # Build the request
            write_stream = f"{self._parent}/streams/_default"
            
            request = bq_types.AppendRowsRequest(
                write_stream=write_stream,
                proto_rows=bq_types.AppendRowsRequest.ProtoData(
                    rows=bq_types.ProtoRows(
                        serialized_rows=serialized_rows
                    )
                )
            )
            
            # Execute write
            response = self._client.append_rows(iter([request]))
            
            # Consume response
            for resp in response:
                if resp.error.code != 0:
                    print(f"[ERROR] BigQuery append error: {resp.error.message}")
                    return 0
            
            return len(rows)
            
        except GoogleAPIError as e:
            print(f"[ERROR] BigQuery API error: {e}")
            return 0
    
    def flush(self) -> int:
        """
        Flush all buffered rows to BigQuery.
        
        Returns:
            Number of rows flushed
        """
        self._last_flush = time.time()
        return self._try_flush()
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return len(self._buffer)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get writer statistics."""
        return {
            "buffer_size": len(self._buffer),
            "last_flush": self._last_flush,
            "bigquery_available": BIGQUERY_AVAILABLE,
            "client_ready": self._client is not None,
            "table_path": self.table_path
        }


class LocalFileSink:
    """
    Fallback sink that writes to local JSON file.
    Used when BigQuery is not available or for testing.
    """
    
    def __init__(self, filepath: str = "/tmp/axiom_logs.jsonl"):
        self.filepath = filepath
        self._lock = threading.Lock()
    
    def append(self, row: Dict[str, Any]) -> None:
        """Append row to file."""
        with self._lock:
            with open(self.filepath, "a") as f:
                f.write(json.dumps(row, default=str) + "\n")
    
    def flush(self) -> int:
        """No-op for file sink (writes are immediate)."""
        return 0


class DataSink:
    """
    High-level data sink that routes to BigQuery or local file.
    
    Usage:
        sink = DataSink.create()
        sink.log({"event": "trade", "symbol": "BTCUSD"})
        sink.trade(symbol="BTCUSD", side="buy", qty=0.1, price=50000)
    """
    
    def __init__(self, writer: Any):
        self._writer = writer
    
    @classmethod
    def create(
        cls,
        table_path: Optional[str] = None,
        credentials_json: Optional[str] = None
    ) -> "DataSink":
        """
        Create a data sink with auto-detection.
        
        Args:
            table_path: BigQuery table path (project.dataset.table)
            credentials_json: Service account JSON string
        
        Returns:
            Configured DataSink instance
        """
        # Try to get from environment
        table_path = table_path or os.getenv("BIGQUERY_TABLE_PATH")
        credentials_json = credentials_json or os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if BIGQUERY_AVAILABLE and table_path:
            writer = BigQueryStreamWriter(
                table_path=table_path,
                credentials_json=credentials_json
            )
        else:
            # Fallback to local file
            writer = LocalFileSink()
        
        return cls(writer)
    
    def log(self, entry: Dict[str, Any]) -> None:
        """Log a generic entry."""
        self._writer.append(entry)
    
    def trade(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        **kwargs
    ) -> None:
        """Log a trade event."""
        self._writer.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "event": "TRADE_EXECUTED",
            "module": "trading",
            "context": {
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "price": price,
                **kwargs
            }
        })
    
    def signal(
        self,
        symbol: str,
        action: str,
        confidence: float,
        engine: str = "unknown",
        **kwargs
    ) -> None:
        """Log a trading signal."""
        self._writer.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "event": "TRADE_SIGNAL",
            "module": engine,
            "context": {
                "symbol": symbol,
                "action": action,
                "confidence": confidence,
                **kwargs
            }
        })
    
    def flush(self) -> int:
        """Flush buffered data."""
        return self._writer.flush()
    
    def stats(self) -> Dict[str, Any]:
        """Get sink statistics."""
        if hasattr(self._writer, "get_stats"):
            return self._writer.get_stats()
        return {"type": type(self._writer).__name__}


# Global data sink instance
_data_sink: Optional[DataSink] = None


def get_data_sink() -> DataSink:
    """Get the global data sink instance."""
    global _data_sink
    if _data_sink is None:
        _data_sink = DataSink.create()
    return _data_sink


def init_data_sink(table_path: str, credentials_json: Optional[str] = None) -> DataSink:
    """Initialize the global data sink with specific config."""
    global _data_sink
    _data_sink = DataSink.create(table_path, credentials_json)
    return _data_sink
