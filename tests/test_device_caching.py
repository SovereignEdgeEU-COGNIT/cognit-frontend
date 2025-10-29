#!/usr/bin/env python3
"""
Manual test script for device assignment caching logic.
Tests the 3 cases:
1. Device ID not in DB - insert new assignment
2. Device ID exists, same app_reqs - update last_seen only
3. Device ID exists, different app_reqs - update assignment with new cluster
"""

import sys
import os
from datetime import datetime
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.db_manager import DBManager


@pytest.fixture(scope="session")
def db():
    """Shared DBManager instance for all tests."""
    return DBManager('./database/device_cluster_assignment.db')


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_data(db):
    """Clean up test data from database after all tests complete."""
    yield  # Run tests first

    # Cleanup after all tests
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM device_cluster_assignment WHERE device_id LIKE 'test_device_%'")
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} test device assignments from database")


# Test data
device_id = "test_device_001"

# Global variable for test modifications
test_device_id = device_id

app_reqs_1 = {
    "ID": test_device_id,  # Will be updated in test
    "FLAVOUR": "TestOVH",
    "GEOLOCATION": "43.05,-2.53",
    "IS_CONFIDENTIAL": "false",
    "PROVIDERS": "provider_1,provider_2",
    "MAX_CAPACITY": "15"
}

app_reqs_2 = {
    "ID": test_device_id,  # Will be updated in test
    "FLAVOUR": "TestOVH",
    "GEOLOCATION": "43.05,-2.53",
    "IS_CONFIDENTIAL": "true",  # Changed
    "PROVIDERS": "provider_3",  # Changed
    "MAX_CAPACITY": "20"        # Changed
}

def test_case_1_device_not_in_db(db):
    """Test Case 1: Device ID not in database - should insert new assignment"""
    # Use a unique device ID for testing to avoid conflicts
    global test_device_id
    test_device_id = f"test_device_{int(__import__('time').time())}"

    # Update app_reqs with the test device ID
    app_reqs_1["ID"] = test_device_id
    app_reqs_2["ID"] = test_device_id

    # Verify device doesn't exist
    assignment = db.get_device_assignment(test_device_id)
    assert assignment is None, f"Device {test_device_id} should not exist initially"

    # Simulate inserting new assignment (what our endpoint does)
    cluster_id = 5  # Mock selected cluster
    flavour = app_reqs_1['FLAVOUR']
    app_req_id = 123  # Mock OpenNebula document ID
    estimated_load = 1.0

    db.insert_device_assignment(test_device_id, cluster_id, flavour, app_req_id, app_reqs_1, estimated_load)

    # Verify it was inserted
    assignment = db.get_device_assignment(test_device_id)
    assert assignment is not None, "Device assignment should exist"
    assert assignment['device_id'] == test_device_id
    assert assignment['cluster_id'] == cluster_id
    assert assignment['flavour'] == flavour
    assert assignment['app_req_id'] == app_req_id
    assert assignment['app_req_json'] == app_reqs_1


def test_case_2_same_app_reqs(db):
    """Test Case 2: Device exists, same app requirements - should only update last_seen"""
    # Get current assignment
    assignment_before = db.get_device_assignment(test_device_id)

    # Simulate what endpoint does when app_reqs are the same
    db.update_last_seen(test_device_id)

    # Verify only last_seen was updated, other fields unchanged
    assignment_after = db.get_device_assignment(test_device_id)

    assert assignment_after['device_id'] == assignment_before['device_id']
    assert assignment_after['cluster_id'] == assignment_before['cluster_id']
    assert assignment_after['flavour'] == assignment_before['flavour']
    assert assignment_after['app_req_id'] == assignment_before['app_req_id']
    assert assignment_after['app_req_json'] == assignment_before['app_req_json']

    # Parse timestamps and verify the update was more recent
    before_time = datetime.fromisoformat(assignment_before['last_seen'])
    after_time = datetime.fromisoformat(assignment_after['last_seen'])
    assert after_time > before_time, "last_seen should be updated to a more recent timestamp"


def test_case_3_different_app_reqs(db):
    """Test Case 3: Device exists, different app requirements - should update assignment"""
    # Simulate updating with new requirements (what our endpoint does)
    new_cluster_id = 7  # Mock newly selected cluster
    new_app_req_id = 456  # Mock new OpenNebula document ID
    estimated_load = 0.5

    db.update_device_assignment(test_device_id, new_cluster_id, app_reqs_2['FLAVOUR'], new_app_req_id, app_reqs_2, estimated_load)

    # Verify assignment was updated
    assignment_after = db.get_device_assignment(test_device_id)

    assert assignment_after['device_id'] == test_device_id
    assert assignment_after['cluster_id'] == new_cluster_id  # Changed
    assert assignment_after['flavour'] == app_reqs_2['FLAVOUR']  # Same in this case
    assert assignment_after['app_req_id'] == new_app_req_id  # Changed
    assert assignment_after['app_req_json'] == app_reqs_2  # Changed


def test_cleanup_old_records(db):
    """Test Case 4: Cleanup removes records older than configured days"""
    from datetime import timedelta
    
    old_device = f"test_device_old_{int(__import__('time').time())}"
    recent_device = f"test_device_recent_{int(__import__('time').time())}"
    
    # Insert a device with old timestamp (35 days ago)
    with db._get_connection() as conn:
        cursor = conn.cursor()
        old_timestamp = (datetime.now() - timedelta(days=35)).isoformat()
        cursor.execute(
            'INSERT INTO device_cluster_assignment '
            '(device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json, estimated_load) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (old_device, 1, "OVH", old_timestamp, 1, "{}", 1.0)
        )
    
    # Insert a recent device (1 day ago)
    with db._get_connection() as conn:
        cursor = conn.cursor()
        recent_timestamp = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute(
            'INSERT INTO device_cluster_assignment '
            '(device_id, cluster_id, flavour, last_seen, app_req_id, app_req_json, estimated_load) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (recent_device, 1, "OVH", recent_timestamp, 1, "{}", 1.0)
        )
    
    # Verify both exist before cleanup
    assert db.get_device_assignment(old_device) is not None
    assert db.get_device_assignment(recent_device) is not None
    
    # Trigger cleanup (called on init, but we call manually for testing)
    db.cleanup_old_records()
    
    # Old device should be deleted, recent should remain
    assert db.get_device_assignment(old_device) is None, "Old device should be cleaned up"
    assert db.get_device_assignment(recent_device) is not None, "Recent device should remain"
    
    # Cleanup test data
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM device_cluster_assignment WHERE device_id = ?", (recent_device,))


