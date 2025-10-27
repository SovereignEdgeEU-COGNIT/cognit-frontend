import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any

class DBManager:
    def __init__(self, DB_PATH: str):
        self.DB_PATH = DB_PATH
        self.init_db()

    def init_db(self) -> None:
        """Initialize SQLite database and create device_cluster_assignment table if it doesn't exist."""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_cluster_assignment (
                device_id TEXT PRIMARY KEY,
                cluster_id TEXT NOT NULL,
                flavour TEXT NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                app_req_id TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()


    def get_device_assignment(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve device cluster assignment from database.

        Args:
            device_id: The device identifier

        Returns:
            Dictionary with assignment data or None if not found
        """
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT device_id, cluster_id, flavour, last_seen, app_req_id FROM device_cluster_assignment WHERE device_id = ?',
            (device_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'device_id': row[0],
                'cluster_id': row[1],
                'flavour': row[2],
                'last_seen': row[3],
                'app_req_id': row[4]
            }
        return None


    def insert_device_assignment(self, device_id: str, cluster_id: str, flavour: str, app_req_id: str) -> None:
        """Insert new device cluster assignment into database.

        Args:
            device_id: The device identifier
            cluster_id: The assigned cluster identifier
            flavour: The device flavour
            app_req_id: The application requirement identifier
        """
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            'INSERT INTO device_cluster_assignment (device_id, cluster_id, flavour, last_seen, app_req_id) VALUES (?, ?, ?, ?, ?)',
            (device_id, cluster_id, flavour, now, app_req_id)
        )

        conn.commit()
        conn.close()


    def update_device_assignment(self, device_id: str, last_seen: str, app_req_id: str) -> None:
        """Update existing device cluster assignment.

        Args:
            device_id: The device identifier
            last_seen: Timestamp of last activity
            app_req_id: The application requirement identifier
        """
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            'UPDATE device_cluster_assignment SET last_seen = ?, app_req_id = ? WHERE device_id = ?',
            (last_seen, app_req_id, device_id)
        )

        conn.commit()
        conn.close()
