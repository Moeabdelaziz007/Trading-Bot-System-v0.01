"""
📦 DATABASE BATCHER - Write Optimization for D1 Database
Reduces write operations by 95%+ through intelligent batching

This module implements:
1. In-memory buffering of records
2. Automatic batch flushing (size or time-based)
3. Transaction-safe bulk inserts
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import json


class DatabaseBatcher:
    """
    The Database Batcher reduces D1 write operations by buffering records
    and flushing them in bulk transactions.
    
    Instead of 85,000 individual INSERTs, we do ~1,000 batched INSERTs.
    Each batch can contain 50-100 records in a single transaction.
    """
    
    def __init__(
        self, 
        batch_size: int = 50, 
        flush_interval: int = 10,
        on_flush: Optional[Callable] = None
    ):
        """
        Args:
            batch_size: Max records before auto-flush (default: 50)
            flush_interval: Seconds between periodic flushes (default: 10)
            on_flush: Optional callback when flush occurs
        """
        self.buffer: Dict[str, List[Dict[str, Any]]] = {}  # Table -> Records
        self.BATCH_SIZE = batch_size
        self.FLUSH_INTERVAL = flush_interval
        self.on_flush = on_flush
        self.stats = {
            "records_buffered": 0,
            "flushes_performed": 0,
            "records_written": 0,
            "writes_saved": 0  # Individual writes we avoided
        }
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the periodic flush background task"""
        if self._running:
            return
        self._running = True
        self._flush_task = asyncio.create_task(self._periodic_flush())
        print(f"📦 DatabaseBatcher started (batch_size={self.BATCH_SIZE}, interval={self.FLUSH_INTERVAL}s)")
    
    async def stop(self):
        """Stop the batcher and flush remaining records"""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        await self.flush_all()
        print("📦 DatabaseBatcher stopped")
    
    async def add_record(self, table: str, record: Dict[str, Any]):
        """
        Add a record to the buffer for the specified table.
        Auto-flushes when batch size is reached.
        
        Args:
            table: The table name (e.g., 'trades', 'signals')
            record: The record to insert
        """
        if table not in self.buffer:
            self.buffer[table] = []
        
        # Add timestamp if not present
        if "created_at" not in record:
            record["created_at"] = datetime.utcnow().isoformat()
        
        self.buffer[table].append(record)
        self.stats["records_buffered"] += 1
        
        # Check if we need to flush this table
        if len(self.buffer[table]) >= self.BATCH_SIZE:
            await self.flush_table(table)
    
    async def flush_table(self, table: str):
        """Flush all buffered records for a specific table"""
        if table not in self.buffer or not self.buffer[table]:
            return
        
        records = self.buffer[table]
        count = len(records)
        
        # Calculate writes saved (count - 1 because we're doing 1 bulk insert)
        self.stats["writes_saved"] += count - 1
        self.stats["records_written"] += count
        self.stats["flushes_performed"] += 1
        
        print(f"📉 FLUSHING {table}: Writing {count} records in 1 transaction (saved {count - 1} writes)")
        
        # Call the flush handler if provided
        if self.on_flush:
            await self.on_flush(table, records)
        
        # Clear the buffer
        self.buffer[table] = []
    
    async def flush_all(self):
        """Flush all tables"""
        tables = list(self.buffer.keys())
        for table in tables:
            await self.flush_table(table)
    
    async def _periodic_flush(self):
        """Background task that flushes periodically"""
        while self._running:
            try:
                await asyncio.sleep(self.FLUSH_INTERVAL)
                await self.flush_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Periodic flush error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batching statistics"""
        total_buffered = sum(len(records) for records in self.buffer.values())
        return {
            **self.stats,
            "currently_buffered": total_buffered,
            "tables_with_data": list(self.buffer.keys()),
            "efficiency": f"{(self.stats['writes_saved'] / max(1, self.stats['records_written']) * 100):.1f}%"
        }
    
    def get_buffer_status(self) -> Dict[str, int]:
        """Get current buffer sizes per table"""
        return {table: len(records) for table, records in self.buffer.items()}


class D1BatchWriter:
    """
    D1-specific batch writer that generates optimized SQL.
    Inherits from DatabaseBatcher with D1-specific flush logic.
    """
    
    def __init__(self, db_binding=None, **kwargs):
        """
        Args:
            db_binding: The D1 database binding from Cloudflare env
        """
        self.db = db_binding
        self.batcher = DatabaseBatcher(
            on_flush=self._execute_batch,
            **kwargs
        )
    
    async def _execute_batch(self, table: str, records: List[Dict[str, Any]]):
        """Execute a batch insert using D1's batch API"""
        if not records:
            return
        
        if not self.db:
            print(f"⚠️ D1 not configured, skipping batch write for {table}")
            return
        
        # Build the bulk INSERT statement
        columns = list(records[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        values_list = []
        params = []
        
        for record in records:
            values_list.append(f"({placeholders})")
            params.extend([record.get(col) for col in columns])
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES {', '.join(values_list)}"
        
        try:
            await self.db.prepare(sql).bind(*params).run()
            print(f"✅ D1 Batch: Inserted {len(records)} records into {table}")
        except Exception as e:
            print(f"❌ D1 Batch Error: {e}")
            # Fallback: Try individual inserts
            for record in records:
                try:
                    single_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                    await self.db.prepare(single_sql).bind(*list(record.values())).run()
                except Exception as inner_e:
                    print(f"❌ Individual insert failed: {inner_e}")
    
    async def insert(self, table: str, record: Dict[str, Any]):
        """Add a record to be batched"""
        await self.batcher.add_record(table, record)
    
    async def start(self):
        await self.batcher.start()
    
    async def stop(self):
        await self.batcher.stop()
    
    def get_stats(self):
        return self.batcher.get_stats()


# Singleton instance for global use
db_batcher = DatabaseBatcher()
