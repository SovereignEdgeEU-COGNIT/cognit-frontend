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
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "sum_cpu_faas_role": 50.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=0) == 1.0
    
    def test_backlog_conservative(self):
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 5, "sum_cpu_faas_role": 80.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=3) == 1.0
    
    def test_idle_system_zero(self):
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "sum_cpu_faas_role": 0.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=3) == 0.0
    
    def test_normal_load_calculation(self):
        """60% CPU / 2 devices = 30% -> normalized to 0.30"""
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "sum_cpu_faas_role": 60.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=2) == pytest.approx(0.30)
    
    def test_multiple_services_aggregation(self):
        """(40% + 20%) / 4 devices = 15% -> normalized to 0.15"""
        mock = [
            {"service_id": 70, "service_name": "test1", "queue_total": 0, "sum_cpu_faas_role": 40.0},
            {"service_id": 71, "service_name": "test2", "queue_total": 0, "sum_cpu_faas_role": 20.0}
        ]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=4) == pytest.approx(0.15)
    
    def test_max_load_capped_at_one(self):
        """200% CPU / 1 device = 200% -> capped at 1.0"""
        mock = [{"service_id": 70, "service_name": "test", "queue_total": 0, "sum_cpu_faas_role": 200.0}]
        with patch('system_metrics.collect_system_metrics', return_value=mock):
            assert calculate_estimated_load(device_count=1) == 1.0


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
            self.db.insert_device_assignment(device_id, 0, "OVH", i+1, {}, 1.0)
        
        count = self.db.get_distinct_device_count()
        assert count >= len(self.test_devices)
    
    def test_duplicate_counted_once(self):
        self.test_devices = ["test_load_004"]
        
        self.db.insert_device_assignment(self.test_devices[0], 0, "OVH", 1, {}, 1.0)
        initial_count = self.db.get_distinct_device_count()
        
        self.db.update_device_assignment(self.test_devices[0], 1, "OVH", 2, {})
        updated_count = self.db.get_distinct_device_count()
        
        assert initial_count == updated_count

