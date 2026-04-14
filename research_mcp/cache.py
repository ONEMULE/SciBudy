from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path


class SQLiteStateStore:
    def __init__(self, db_path: Path) -> None:
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limits (
                    bucket TEXT PRIMARY KEY,
                    available_at REAL NOT NULL
                )
                """
            )

    def get_cache(self, key: str) -> str | None:
        now = time.time()
        with self._lock, self._conn:
            row = self._conn.execute(
                "SELECT value, expires_at FROM cache_entries WHERE key = ?",
                (key,),
            ).fetchone()
            if not row:
                return None
            if row["expires_at"] <= now:
                self._conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                return None
            return str(row["value"])

    def set_cache(self, key: str, value: str, ttl_sec: float) -> None:
        now = time.time()
        expires_at = now + max(ttl_sec, 0.0)
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO cache_entries(key, value, expires_at, created_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    expires_at = excluded.expires_at,
                    created_at = excluded.created_at
                """,
                (key, value, expires_at, now),
            )

    def throttle(self, bucket: str, min_interval_sec: float) -> None:
        if min_interval_sec <= 0:
            return
        now = time.time()
        with self._lock, self._conn:
            row = self._conn.execute(
                "SELECT available_at FROM rate_limits WHERE bucket = ?",
                (bucket,),
            ).fetchone()
            available_at = float(row["available_at"]) if row else now
            wait_for = max(0.0, available_at - now)
            next_available_at = max(now, available_at) + min_interval_sec
            self._conn.execute(
                """
                INSERT INTO rate_limits(bucket, available_at)
                VALUES(?, ?)
                ON CONFLICT(bucket) DO UPDATE SET
                    available_at = excluded.available_at
                """,
                (bucket, next_available_at),
            )
        if wait_for > 0:
            time.sleep(wait_for)
