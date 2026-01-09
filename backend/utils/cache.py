import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Any

class Cache:
    """
    Simple SQLite-based cache to store API responses and scraped data.
    Reduces API calls and respects rate limits.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv("DATABASE_PATH", "./cache.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the cache database table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache if it exists and hasn't expired.
        Returns None if not found or expired.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value, expires_at FROM cache
            WHERE key = ? AND expires_at > datetime('now')
        """, (key,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])

        return None

    def set(self, key: str, value: Any, ttl_hours: Optional[int] = None) -> None:
        """
        Store a value in cache with optional TTL in hours.
        Default TTL is 24 hours.
        """
        if ttl_hours is None:
            ttl_hours = int(os.getenv("CACHE_EXPIRY_HOURS", 24))

        expires_at = datetime.now() + timedelta(hours=ttl_hours)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO cache (key, value, expires_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), expires_at))

        conn.commit()
        conn.close()

    def delete(self, key: str) -> None:
        """Delete a specific key from cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))

        conn.commit()
        conn.close()

    def clear_expired(self) -> int:
        """Remove all expired entries. Returns number of deleted entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache WHERE expires_at <= datetime('now')")
        deleted = cursor.rowcount

        conn.commit()
        conn.close()

        return deleted

    def clear_all(self) -> None:
        """Clear all cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache")

        conn.commit()
        conn.close()
