import os
import json
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages the 'Slow Lane' configuration (config.json).
    Uses a caching mechanism to avoid disk I/O on every tick.
    """
    
    CONFIG_FILE = "config.json"
    _last_mtime = 0
    _cached_config = None
    
    @classmethod
    def load_config(cls) -> Optional[Dict[str, Any]]:
        """
        Loads config only if the file has changed since the last load.
        Returns the cached config if no change.
        """
        try:
            if not os.path.exists(cls.CONFIG_FILE):
                logger.warning(f"Config file {cls.CONFIG_FILE} not found.")
                return cls._cached_config

            current_mtime = os.path.getmtime(cls.CONFIG_FILE)
            
            if current_mtime > cls._last_mtime:
                # File has changed, reload it
                with open(cls.CONFIG_FILE, 'r') as f:
                    cls._cached_config = json.load(f)
                
                cls._last_mtime = current_mtime
                logger.info("⚙️ Config reloaded from disk")
                
            return cls._cached_config
            
        except Exception as e:
            logger.error(f"⚠️ Error loading config: {e}")
            return cls._cached_config

    @classmethod
    def update_config(cls, updates: Dict[str, Any]) -> bool:
        """
        Updates specific keys in the config file.
        Used by the Voice Agent to change settings.
        """
        try:
            # Load current first to ensure we don't overwrite with stale data
            current = cls.load_config() or {}
            
            # Apply updates
            current.update(updates)
            
            # Write back to disk
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(current, f, indent=4)
            
            # Update cache immediately
            cls._cached_config = current
            cls._last_mtime = os.path.getmtime(cls.CONFIG_FILE)
            
            logger.info(f"✅ Config updated: {updates.keys()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
            return False
