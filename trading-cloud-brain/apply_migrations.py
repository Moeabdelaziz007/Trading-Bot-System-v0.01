#!/usr/bin/env python3
"""
D1 Database Migration System for Trading Cloud Brain

This script manages database schema migrations for Cloudflare D1 (SQLite) databases.
It supports both local development and production Cloudflare Workers environments.

Features:
- Migration versioning and tracking
- Up and down migration support
- Rollback capabilities
- Environment-specific configuration
- Proper error handling and logging
"""

import os
import sys
import sqlite3
import hashlib
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages D1 database migrations for the trading system."""
    
    def __init__(self, db_path: str, migrations_dir: str = "migrations"):
        """
        Initialize the migration manager.
        
        Args:
            db_path: Path to the SQLite database file
            migrations_dir: Directory containing migration files
        """
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.conn = None
        
        # Ensure migrations directory exists
        if not self.migrations_dir.exists():
            raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return self.conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def initialize_migration_table(self):
        """Create the schema_migrations table if it doesn't exist."""
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at INTEGER NOT NULL,
                    checksum TEXT NOT NULL
                )
            """)
            self.conn.commit()
            logger.info("Migration tracking table initialized")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize migration table: {e}")
            raise
    
    def get_applied_migrations(self) -> Dict[str, Dict]:
        """Get list of applied migrations from the database."""
        try:
            cursor = self.conn.execute("""
                SELECT version, applied_at, checksum 
                FROM schema_migrations 
                ORDER BY applied_at
            """)
            return {row['version']: dict(row) for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return {}
    
    def get_pending_migrations(self) -> List[Tuple[str, Path]]:
        """Get list of pending migrations to be applied."""
        applied = self.get_applied_migrations().keys()
        
        # Get all migration files
        migration_files = []
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            version = file_path.stem
            if version not in applied:
                migration_files.append((version, file_path))
        
        return migration_files
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of migration file."""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def apply_migration(self, version: str, file_path: Path) -> bool:
        """
        Apply a single migration.
        
        Args:
            version: Migration version
            file_path: Path to migration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read migration SQL
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Calculate checksum
            checksum = self.calculate_checksum(file_path)
            
            # Execute migration
            cursor = self.conn.cursor()
            
            # Split SQL content by semicolons and execute each statement
            # This handles multi-statement migrations
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            
            # Record migration
            cursor.execute("""
                INSERT INTO schema_migrations (version, applied_at, checksum)
                VALUES (?, ?, ?)
            """, (version, int(datetime.now().timestamp() * 1000), checksum))
            
            self.conn.commit()
            logger.info(f"Applied migration {version} successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            self.conn.rollback()
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """
        Rollback a migration (remove from tracking table).
        Note: This doesn't undo the SQL changes, only removes the migration record.
        
        Args:
            version: Migration version to rollback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM schema_migrations 
                WHERE version = ?
            """, (version,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                logger.info(f"Rolled back migration {version}")
                return True
            else:
                logger.warning(f"Migration {version} not found in applied migrations")
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            self.conn.rollback()
            return False
    
    def apply_pending_migrations(self) -> bool:
        """Apply all pending migrations."""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations to apply")
            return True
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        success_count = 0
        for version, file_path in pending:
            if self.apply_migration(version, file_path):
                success_count += 1
            else:
                logger.error(f"Failed to apply migration {version}, stopping")
                break
        
        logger.info(f"Applied {success_count}/{len(pending)} migrations")
        return success_count == len(pending)
    
    def get_migration_status(self) -> Dict:
        """Get current migration status."""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': list(applied.keys()),
            'pending_migrations': [version for version, _ in pending],
            'last_migration': max(applied.keys()) if applied else None
        }
    
    def create_down_migration(self, version: str) -> bool:
        """
        Create a down migration file for the specified version.
        This is a placeholder for future implementation.
        
        Args:
            version: Migration version to create down migration for
            
        Returns:
            True if successful, False otherwise
        """
        down_file = self.migrations_dir / f"{version}_down.sql"
        
        if down_file.exists():
            logger.warning(f"Down migration already exists: {down_file}")
            return False
        
        # Create template down migration
        template = f"""-- Down Migration for {version}
-- Generated on {datetime.now().isoformat()}
-- WARNING: This is a template. Review and modify before use.

-- Add DROP statements and other cleanup operations here
-- Example:
-- DROP TABLE IF EXISTS example_table;
"""
        
        try:
            with open(down_file, 'w') as f:
                f.write(template)
            logger.info(f"Created down migration template: {down_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create down migration: {e}")
            return False


def get_database_path(environment: str) -> str:
    """Get database path based on environment."""
    if environment == "production":
        # For Cloudflare Workers D1, this would be handled differently
        # For now, we'll use an environment variable
        db_path = os.getenv("D1_DATABASE_PATH")
        if not db_path:
            raise ValueError("D1_DATABASE_PATH environment variable not set for production")
        return db_path
    else:
        # Local development
        return "trading_brain.db"


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description="D1 Database Migration System")
    parser.add_argument(
        "command",
        choices=["apply", "status", "rollback", "init"],
        help="Migration command to execute"
    )
    parser.add_argument(
        "--version",
        help="Migration version (for rollback command)"
    )
    parser.add_argument(
        "--env",
        choices=["dev", "production"],
        default="dev",
        help="Environment (dev or production)"
    )
    parser.add_argument(
        "--migrations-dir",
        default="migrations",
        help="Migrations directory path"
    )
    parser.add_argument(
        "--db-path",
        help="Custom database path (overrides environment)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get database path
    if args.db_path:
        db_path = args.db_path
    else:
        db_path = get_database_path(args.env)
    
    try:
        # Initialize migration manager
        manager = MigrationManager(db_path, args.migrations_dir)
        manager.connect()
        manager.initialize_migration_table()
        
        # Execute command
        if args.command == "apply":
            success = manager.apply_pending_migrations()
            sys.exit(0 if success else 1)
            
        elif args.command == "status":
            status = manager.get_migration_status()
            print(json.dumps(status, indent=2))
            
        elif args.command == "rollback":
            if not args.version:
                logger.error("Version required for rollback command")
                sys.exit(1)
            success = manager.rollback_migration(args.version)
            sys.exit(0 if success else 1)
            
        elif args.command == "init":
            logger.info("Migration system initialized")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        if 'manager' in locals():
            manager.close()


if __name__ == "__main__":
    main()