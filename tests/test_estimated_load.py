"""
TODO: WORK IN PROGRESS - ESTIMATED LOAD RANGE TO CLARIFY
"""

#!/usr/bin/env python3
import sys
import os
from unittest.mock import patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from system_metrics import calculate_estimated_load
from db_manager import DBManager


class TestEstimatedLoadCalculation:
    
    def test_no_services_returns_zero(self):
        with patch('system_metrics.collect_system_metrics', return_value=[]):
            assert calculate_estimated_load(device_count=0) == 0.0
    
    def test_first_device_conservative(self):
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "avg_cpu": 50.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=1) == pytest.approx(50.0)
    
    def test_backlog_conservative(self):
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 5, "avg_cpu": 80.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=3) == 1.0
    
    def test_idle_system_zero(self):
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "avg_cpu": 0.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=3) == 0.0
    
    def test_normal_load_calculation(self):
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "avg_cpu": 60.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=2) == pytest.approx(30.0)
    
    def test_multiple_services_aggregation(self):
        mock = [
            {"service_id": 70, "service_name": "test1", "queue_total": 0, "avg_cpu": 40.0},
            {"service_id": 71, "service_name": "test2", "queue_total": 0, "avg_cpu": 20.0}
        ]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=4) == pytest.approx(15.0)


class TestDBManagerDeviceCount:
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.db = DBManager('./database/device_cluster_assignment.db')
        self.test_devices = []
        yield
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            for device_id in self.test_devices:
                cursor.execute("DELETE FROM device_cluster_assignment WHERE device_id = ?", (device_id,))
    
    def test_distinct_device_count(self):
        self.test_devices = ["test_load_001", "test_load_002", "test_load_003"]
        
        for i, device_id in enumerate(self.test_devices):
            self.db.insert_device_assignment(device_id, "0", "OVH", str(i+1), {})
        
        count = self.db.get_distinct_device_count()
        assert count >= len(self.test_devices)
    
    def test_duplicate_counted_once(self):
        self.test_devices = ["test_load_004"]
        
        self.db.insert_device_assignment(self.test_devices[0], "0", "OVH", "1", {})
        initial_count = self.db.get_distinct_device_count()
        
        self.db.update_device_assignment(self.test_devices[0], "1", "OVH", "2", {})
        updated_count = self.db.get_distinct_device_count()
        
        assert initial_count == updated_count

