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

from src.db_manager import DBManager


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_data():
    """Clean up test data from database after all tests complete."""
    yield  # Run tests first

    # Cleanup after all tests
    db = DBManager('./database/device_cluster_assignment.db')
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

def test_case_1_device_not_in_db():
    """Test Case 1: Device ID not in database - should insert new assignment"""

    db = DBManager('./database/device_cluster_assignment.db')

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
    cluster_id = "5"  # Mock selected cluster
    flavour = app_reqs_1['FLAVOUR']
    app_req_id = "123"  # Mock OpenNebula document ID

    db.insert_device_assignment(test_device_id, cluster_id, flavour, app_req_id, app_reqs_1)

    # Verify it was inserted
    assignment = db.get_device_assignment(test_device_id)
    assert assignment is not None, "Device assignment should exist"
    assert assignment['device_id'] == test_device_id
    assert assignment['cluster_id'] == cluster_id
    assert assignment['flavour'] == flavour
    assert assignment['app_req_id'] == app_req_id
    assert assignment['app_req_json'] == app_reqs_1


def test_case_2_same_app_reqs():
    """Test Case 2: Device exists, same app requirements - should only update last_seen"""

    db = DBManager('./database/device_cluster_assignment.db')

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


def test_case_3_different_app_reqs():
    """Test Case 3: Device exists, different app requirements - should update assignment"""

    db = DBManager('./database/device_cluster_assignment.db')

    # Simulate updating with new requirements (what our endpoint does)
    new_cluster_id = "7"  # Mock newly selected cluster
    new_app_req_id = "456"  # Mock new OpenNebula document ID

    db.update_device_assignment(test_device_id, new_cluster_id, app_reqs_2['FLAVOUR'], new_app_req_id, app_reqs_2)

    # Verify assignment was updated
    assignment_after = db.get_device_assignment(test_device_id)

    assert assignment_after['device_id'] == test_device_id
    assert assignment_after['cluster_id'] == new_cluster_id  # Changed
    assert assignment_after['flavour'] == app_reqs_2['FLAVOUR']  # Same in this case
    assert assignment_after['app_req_id'] == new_app_req_id  # Changed
    assert assignment_after['app_req_json'] == app_reqs_2  # Changed


