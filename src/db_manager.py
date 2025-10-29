import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, Any
import cognit_conf as conf

class DBManager:
    def __init__(self, DB_PATH: str, DB_CLEANUP_DAYS: int = conf.DB_CLEANUP_DAYS):
        self.DB_PATH = DB_PATH
        self._write_lock = threading.Lock()
        self.init_db()
        self.DB_CLEANUP_DAYS = DB_CLEANUP_DAYS
        self.cleanup_old_records()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.DB_PATH)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize SQLite database and create device_cluster_assignment table if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_cluster_assignment (
                    device_id TEXT PRIMARY KEY,
                    cluster_id INTEGER NOT NULL,
                    flavour TEXT NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    app_req_id INTEGER NOT NULL,
                    app_req_json TEXT NOT NULL,
                    estimated_load REAL DEFAULT 1.0
                )
            ''')


    def cleanup_old_records(self) -> None:
        """Delete records older than configured days on initialization."""
        with self._write_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM device_cluster_assignment "
                    "WHERE last_seen <= datetime('now', '-' || ? || ' days')",
                    (self.DB_CLEANUP_DAYS,)
                )
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    print(f"Cleaned up {deleted_count} old device assignments (>{self.DB_CLEANUP_DAYS} days)")

    def get_device_assignment(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve device cluster assignment from database.

        Args:
            device_id: The device identifier

        Returns:
            Dictionary with assignment data or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json, estimated_load '
                'FROM device_cluster_assignment WHERE device_id = ?',
                (device_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'device_id': row[0],
                    'cluster_id': row[1],
                    'flavour': row[2],
                    'last_seen': row[3],
                    'app_req_id': row[4],
                    'app_req_json': json.loads(row[5]) if row[5] else {},
                    'estimated_load': row[6]
                }
            return None


    def insert_device_assignment(
        self,
        device_id: str,
        cluster_id: int,
        flavour: str,
        app_req_id: int,
        app_req_json: Dict[str, Any],
        estimated_load: float = 1.0
    ) -> None:
        """Insert new device cluster assignment into database.

        Args:
            device_id: The device identifier
            cluster_id: The assigned cluster identifier
            flavour: The device flavour
            app_req_id: The application requirement identifier
            app_req_json: Application requirements as JSON
            estimated_load: Estimated load for the device (default 1.0)
        """
        with self._write_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                app_req_json_str = json.dumps(app_req_json)

                cursor.execute(
                    'INSERT INTO device_cluster_assignment '
                    '(device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json, estimated_load) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (device_id, cluster_id, flavour, now, app_req_id, app_req_json_str, estimated_load)
                )


    def update_device_assignment(
        self,
        device_id: str,
        cluster_id: int,
        flavour: str,
        app_req_id: int,
        app_req_json: Dict[str, Any]
    ) -> None:
        """Update existing device cluster assignment.

        Args:
            device_id: The device identifier
            cluster_id: The assigned cluster identifier
            flavour: The device flavour
            app_req_id: The application requirement identifier
            app_req_json: Application requirements as JSON
        """
        with self._write_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                app_req_json_str = json.dumps(app_req_json)

                cursor.execute(
                    'UPDATE device_cluster_assignment '
                    'SET cluster_id = ?, flavour = ?, last_seen = ?, app_req_id = ?, app_req_json = ?'
                    'WHERE device_id = ?',
                    (cluster_id, flavour, now, app_req_id, app_req_json_str, device_id)
                )


    def update_last_seen(self, device_id: str) -> None:
        """Update last_seen timestamp for a device assignment."""
        with self._write_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()

                cursor.execute(
                    'UPDATE device_cluster_assignment SET last_seen = ? WHERE device_id = ?',
                    (now, device_id)
                )

    def update_estimated_load(self, device_id: str, estimated_load: float) -> None:
        """Update only estimated_load for a device assignment.
        
        Args:
            device_id: The device identifier
            estimated_load: New estimated load value
        """
        with self._write_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE device_cluster_assignment SET estimated_load = ? WHERE device_id = ?',
                    (estimated_load, device_id)
                )

    def get_distinct_device_count(self) -> int:
        """Get count of distinct device_ids in the database.
        
        Returns:
            Number of unique devices registered in the system
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DISTINCT device_id) FROM device_cluster_assignment')
            result = cursor.fetchone()
            return result[0] if result else 0
