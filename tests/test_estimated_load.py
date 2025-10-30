#!/usr/bin/env python3
import sys
import os
from unittest.mock import patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from system_metrics import calculate_estimated_load


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


