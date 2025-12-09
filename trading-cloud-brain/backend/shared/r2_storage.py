"""
💾 R2 DATA LAKE STORAGE
Handles Parquet/JSON storage for infinite market history.
"""

import json
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
import io

class CandleStorageR2:
    def __init__(self, bucket):
        self.bucket = bucket

    async def store_candles(self, symbol: str, candles: list):
        """
        Store candles as Parquet for efficient querying.
        Path: candles/SYMBOL/YYYY/MM/DD/HH.parquet
        """
        if not candles:
            return {"status": "skipped", "reason": "empty_data"}

        try:
            # 1. Prepare Data
            # Ensure consistent schema
            processed_candles = []
            for c in candles:
                processed_candles.append({
                    "timestamp": c.get("timestamp"),
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volume", 0))
                })

            now = datetime.fromisoformat(processed_candles[0]["timestamp"].replace("Z", "+00:00"))
            key = f"candles/{symbol}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}.parquet"

            # 2. Convert to Parquet (using pyarrow)
            table = pa.Table.from_pylist(processed_candles)
            sink = io.BytesIO()
            pq.write_table(table, sink, compression='snappy')
            
            # 3. Save to R2
            await self.bucket.put(key, sink.getvalue())
            
            return {"status": "success", "key": key, "count": len(candles)}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_candles(self, symbol: str, date_str: str):
        """
        Retrieve candles for a specific hour.
        date_str format: YYYY/MM/DD/HH
        """
        key = f"candles/{symbol}/{date_str}.parquet"
        
        try:
            obj = await self.bucket.get(key)
            if not obj:
                return []
            
            # Read Parquet
            content = await obj.arrayBuffer()
            buffer = io.BytesIO(content)
            table = pq.read_table(buffer)
            return table.to_pylist()
            
        except Exception as e:
            print(f"Failed to read {key}: {e}")
            return []
