#!/usr/bin/env python3
"""Test SQLEngine: multiple VMs, multiple metrics, single point each."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from pyoneai.core.entity_uid import EntityType, EntityUID
from pyoneai.core.metric_types import Float, MetricAttributes, MetricType, UInt
from pyoneai.core.tsnumpy.io.sql import SQLEngine
from pyoneai.core.tsnumpy.timeseries import Timeseries


def create_single_point(vm_id: int, metric_attr: MetricAttributes, value: float):
    """Create a Timeseries with a single data point."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    entity_uid = EntityUID(type=EntityType.VIRTUAL_MACHINE, id=vm_id)
    
    ts = Timeseries(
        time_idx=np.array([now]),
        metric_idx=np.array([metric_attr]),
        entity_uid_idx=np.array([entity_uid]),
        data=np.array([[[value]]])
    )
    return ts, entity_uid


def list_all_tables(db_path: Path):
    """List all tables in the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [t[0] for t in tables]


def main():
    db_path = Path("./test.db")
    
    # Configuration
    vm_ids = [100, 101, 102]
    metrics = [
        MetricAttributes("cpu_usage", MetricType.GAUGE, Float(0.0, 100.0)),
        MetricAttributes("memory_usage", MetricType.GAUGE, Float(0.0, 100.0)),
        MetricAttributes("disk_iops", MetricType.RATE, UInt()),
    ]
    
    print(f"VMs: {vm_ids}")
    print(f"Metrics: {[m.name for m in metrics]}\n")
    
    # Insert data
    sql_engine = SQLEngine(path=db_path, suffix="monitoring")
    
    for vm_id in vm_ids:
        for metric in metrics:
            value = np.random.uniform(10.0, 90.0)
            ts, entity_uid = create_single_point(vm_id, metric, value)
            sql_engine.insert_data(ts)
            print(f"✓ VM {vm_id} | {metric.name}: {value:.2f}")


if __name__ == "__main__":
    main()

