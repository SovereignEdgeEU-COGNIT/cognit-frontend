import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, Any

class DBManager:
    def __init__(self, DB_PATH: str):
        self.DB_PATH = DB_PATH
        self.init_db()

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
                    cluster_id TEXT NOT NULL,
                    flavour TEXT NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    app_req_id TEXT NOT NULL,
                    app_req_json TEXT NOT NULL
                )
            ''')


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
                'SELECT device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json FROM device_cluster_assignment WHERE device_id = ?',
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
                    'app_req_json': json.loads(row[5]) if row[5] else {}
                }
            return None


    def insert_device_assignment(
        self,
        device_id: str,
        cluster_id: str,
        flavour: str,
        app_req_id: str,
        app_req_json: Dict[str, Any],
    ) -> None:
        """Insert new device cluster assignment into database.

        Args:
            device_id: The device identifier
            cluster_id: The assigned cluster identifier
            flavour: The device flavour
            app_req_id: The application requirement identifier
            app_req_json: Application requirements as JSON
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            app_req_json_str = json.dumps(app_req_json)

            cursor.execute(
                'INSERT INTO device_cluster_assignment (device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json) VALUES (?, ?, ?, ?, ?, ?)',
                (device_id, cluster_id, flavour, now, app_req_id, app_req_json_str)
            )


    def update_device_assignment(
        self,
        device_id: str,
        cluster_id: str,
        flavour: str,
        app_req_id: str,
        app_req_json: Dict[str, Any],
    ) -> None:
        """Update existing device cluster assignment.

        Args:
            device_id: The device identifier
            cluster_id: The assigned cluster identifier
            flavour: The device flavour
            app_req_id: The application requirement identifier
            app_req_json: Application requirements as JSON
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            app_req_json_str = json.dumps(app_req_json)

            cursor.execute(
                'UPDATE device_cluster_assignment SET cluster_id = ?, flavour = ?, last_seen = ?, app_req_id = ?, app_req_json = ? WHERE device_id = ?',
                (cluster_id, flavour, now, app_req_id, app_req_json_str, device_id)
            )


    def update_last_seen(self, device_id: str) -> None:
        """Update last_seen timestamp for a device assignment."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute(
                'UPDATE device_cluster_assignment SET last_seen = ? WHERE device_id = ?',
                (now, device_id)
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
