#!/usr/bin/env python3
import sys
import os
import threading
import uuid
from datetime import datetime, timedelta
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.db_manager import DBManager

TEST_DB_PATH = './database/test_device_cluster_assignment.db'


@pytest.fixture(scope="session")
def db():
    return DBManager(TEST_DB_PATH)


@pytest.fixture(autouse=True, scope="session")
def populate_test_data(db):
    fake_devices = [
        {"device_id": "fake_device_001", "cluster_id": 1, "flavour": "OVH", "app_req_id": 101, "estimated_load": 0.5},
        {"device_id": "fake_device_002", "cluster_id": 2, "flavour": "OVH", "app_req_id": 102, "estimated_load": 0.7},
        {"device_id": "fake_device_003", "cluster_id": 1, "flavour": "AWS", "app_req_id": 103, "estimated_load": 0.3},
        {"device_id": "fake_device_004", "cluster_id": 3, "flavour": "OVH", "app_req_id": 104, "estimated_load": 0.9},
        {"device_id": "fake_device_005", "cluster_id": 2, "flavour": "AWS", "app_req_id": 105, "estimated_load": 0.2},
    ]
    
    for device in fake_devices:
        app_reqs = {
            "ID": device["device_id"],
            "FLAVOUR": device["flavour"],
            "GEOLOCATION": "43.05,-2.53",
            "IS_CONFIDENTIAL": "false",
            "PROVIDERS": "provider_1",
            "MAX_CAPACITY": "10"
        }
        db.insert_device_assignment(
            device["device_id"],
            device["cluster_id"],
            device["flavour"],
            device["app_req_id"],
            app_reqs,
            device["estimated_load"]
        )
    
    yield
    
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


class TestSingleton:
    def test_singleton_pattern(self, db):
        db1 = DBManager(TEST_DB_PATH)
        db2 = DBManager(TEST_DB_PATH)
        db3 = DBManager()
        
        assert db1 is db2
        assert db1 is db3
        assert db1.DB_PATH == db2.DB_PATH
        assert db1.DB_PATH == db3.DB_PATH

    def test_singleton_thread_safety(self):
        instances = []
        
        def create_instance():
            instances.append(DBManager(TEST_DB_PATH))
        
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance


class TestGetAllDeviceIds:
    def test_get_all_device_ids_returns_list(self, db):
        device_ids = db.get_all_device_ids()
        assert isinstance(device_ids, list)
        assert len(device_ids) >= 5

    def test_get_all_device_ids_includes_fake_data(self, db):
        device_ids = db.get_all_device_ids()
        assert "fake_device_001" in device_ids
        assert "fake_device_002" in device_ids
        assert "fake_device_003" in device_ids
        assert "fake_device_004" in device_ids
        assert "fake_device_005" in device_ids

    def test_get_all_device_ids_distinct(self, db):
        device_id = "test_get_all_distinct"
        db.insert_device_assignment(device_id, 0, "OVH", 1, {}, 1.0)
        db.update_device_assignment(device_id, 1, "OVH", 2, {})
        
        device_ids = db.get_all_device_ids()
        assert device_ids.count(device_id) == 1


class TestDeviceCaching:
    def test_case_1_device_not_in_db(self, db):
        test_device_id = f"test_device_{uuid.uuid4().hex[:8]}"
        app_reqs = {
            "ID": test_device_id,
            "FLAVOUR": "TestOVH",
            "GEOLOCATION": "43.05,-2.53",
            "IS_CONFIDENTIAL": "false",
            "PROVIDERS": "provider_1,provider_2",
            "MAX_CAPACITY": "15"
        }

        assert db.get_device_assignment(test_device_id) is None

        db.insert_device_assignment(test_device_id, 5, app_reqs['FLAVOUR'], 123, app_reqs, 1.0)
        
        assignment = db.get_device_assignment(test_device_id)
        assert assignment is not None
        assert assignment['device_id'] == test_device_id
        assert assignment['cluster_id'] == 5
        assert assignment['flavour'] == app_reqs['FLAVOUR']
        assert assignment['app_req_id'] == 123
        assert assignment['app_req_json'] == app_reqs

    def test_case_2_same_app_reqs(self, db):
        test_device_id = f"test_device_{uuid.uuid4().hex[:8]}"
        app_reqs = {
            "ID": test_device_id,
            "FLAVOUR": "TestOVH",
            "GEOLOCATION": "43.05,-2.53",
            "IS_CONFIDENTIAL": "false",
            "PROVIDERS": "provider_1,provider_2",
            "MAX_CAPACITY": "15"
        }
        
        db.insert_device_assignment(test_device_id, 5, app_reqs['FLAVOUR'], 123, app_reqs, 1.0)
        assignment_before = db.get_device_assignment(test_device_id)
        db.update_last_seen(test_device_id)
        assignment_after = db.get_device_assignment(test_device_id)

        assert assignment_after['device_id'] == assignment_before['device_id']
        assert assignment_after['cluster_id'] == assignment_before['cluster_id']
        
        before_time = datetime.fromisoformat(assignment_before['last_seen'])
        after_time = datetime.fromisoformat(assignment_after['last_seen'])
        assert after_time > before_time

    def test_case_3_different_app_reqs(self, db):
        test_device_id = f"test_device_{uuid.uuid4().hex[:8]}"
        app_reqs_1 = {
            "ID": test_device_id,
            "FLAVOUR": "TestOVH",
            "GEOLOCATION": "43.05,-2.53",
            "IS_CONFIDENTIAL": "false",
            "PROVIDERS": "provider_1,provider_2",
            "MAX_CAPACITY": "15"
        }
        app_reqs_2 = {
            "ID": test_device_id,
            "FLAVOUR": "TestOVH",
            "GEOLOCATION": "43.05,-2.53",
            "IS_CONFIDENTIAL": "true",
            "PROVIDERS": "provider_3",
            "MAX_CAPACITY": "20"
        }
        
        db.insert_device_assignment(test_device_id, 5, app_reqs_1['FLAVOUR'], 123, app_reqs_1, 1.0)
        db.update_device_assignment(test_device_id, 7, app_reqs_2['FLAVOUR'], 456, app_reqs_2)
        
        assignment = db.get_device_assignment(test_device_id)
        assert assignment['device_id'] == test_device_id
        assert assignment['cluster_id'] == 7
        assert assignment['app_req_id'] == 456
        assert assignment['app_req_json'] == app_reqs_2

    def test_cleanup_old_records(self, db):
        old_device = f"test_device_old_{uuid.uuid4().hex[:8]}"
        recent_device = f"test_device_recent_{uuid.uuid4().hex[:8]}"
        
        with db._get_connection() as conn:
            cursor = conn.cursor()
            old_timestamp = (datetime.now() - timedelta(days=35)).isoformat()
            cursor.execute(
                'INSERT INTO device_cluster_assignment '
                '(device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json, estimated_load) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (old_device, 1, "OVH", old_timestamp, 1, "{}", 1.0)
            )
        
        with db._get_connection() as conn:
            cursor = conn.cursor()
            recent_timestamp = (datetime.now() - timedelta(days=1)).isoformat()
            cursor.execute(
                'INSERT INTO device_cluster_assignment '
                '(device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json, estimated_load) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (recent_device, 1, "OVH", recent_timestamp, 1, "{}", 1.0)
            )
        
        assert db.get_device_assignment(old_device) is not None
        assert db.get_device_assignment(recent_device) is not None
        
        db.cleanup_old_records()
        
        assert db.get_device_assignment(old_device) is None
        assert db.get_device_assignment(recent_device) is not None


class TestDeviceCount:
    def test_distinct_device_count_includes_fake_data(self, db):
        count = db.get_distinct_device_count()
        assert count >= 5

    def test_distinct_device_count(self, db):
        test_devices = ["test_count_001", "test_count_002", "test_count_003"]
        
        for i, device_id in enumerate(test_devices):
            db.insert_device_assignment(device_id, 0, "OVH", i+1, {}, 1.0)
        
        count = db.get_distinct_device_count()
        assert count >= 5 + len(test_devices)

    def test_duplicate_counted_once(self, db):
        device_id = "test_count_004"
        
        db.insert_device_assignment(device_id, 0, "OVH", 1, {}, 1.0)
        initial_count = db.get_distinct_device_count()
        
        db.update_device_assignment(device_id, 1, "OVH", 2, {})
        updated_count = db.get_distinct_device_count()
        
        assert initial_count == updated_count

