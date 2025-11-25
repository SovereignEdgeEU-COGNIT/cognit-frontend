import sqlite3
from datetime import datetime, timezone

from pyoneai.core import Entity

from ..config import (
    DATA_FILE,
)


def get_metric_date_range_from_db(metric_name, entity: Entity):
    table_name = (
        f"{entity.uid.type.value}_{entity.uid.id}_{metric_name}_monitoring"
    )
    query = f"SELECT MIN(timestamp), MAX(timestamp) FROM '{table_name}'"
    try:
        with sqlite3.connect(DATA_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute(query)
            min_ts, max_ts = cursor.fetchone()

        conn.close()
    except Exception as e:
        raise Exception(f"Error getting date range from database: {e}")

    if not min_ts or not max_ts:
        raise ValueError(
            f"No data found for metric {metric_name} in table {table_name}"
        )

    start_date = datetime.fromtimestamp(min_ts, tz=timezone.utc)
    end_date = datetime.fromtimestamp(max_ts, tz=timezone.utc)

    return start_date, end_date
