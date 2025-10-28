"""
Unit test for cluster filtering functionality in clusters_ids_get function.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import Mock

from opennebula import clusters_ids_get


def create_mock_clusters():
    """Create mock clusters with different attributes for testing."""
    clusters = []

    # Cluster 1: Non-confidential, multiple providers, medium capacity (Spain - same as device)
    c1 = Mock()
    c1.ID = 1
    c1.TEMPLATE = {
        "FLAVOURS": "TestOVH",
        "GEOLOCATION": "43.05,-2.53",  # Spain - 0km from device
        "IS_CONFIDENTIAL": "false",
        "PROVIDERS": "provider_1,provider_2",
        "MAX_CAPACITY": "15"
    }
    clusters.append(c1)

    # Cluster 2: Confidential, different provider, high capacity (Stockholm - farthest)
    c2 = Mock()
    c2.ID = 2
    c2.TEMPLATE = {
        "FLAVOURS": "TestOVH",
        "GEOLOCATION": "59.3294,18.0687",  # Stockholm - 2290km from device
        "IS_CONFIDENTIAL": "true",
        "PROVIDERS": "provider_3",
        "MAX_CAPACITY": "25"
    }
    clusters.append(c2)

    # Cluster 3: Non-confidential, single provider, low capacity (Paris - medium distance)
    c3 = Mock()
    c3.ID = 3
    c3.TEMPLATE = {
        "FLAVOURS": "TestOVH",
        "GEOLOCATION": "48.8566,2.3522",
        "IS_CONFIDENTIAL": "false",
        "PROVIDERS": "provider_1",
        "MAX_CAPACITY": "10"
    }
    clusters.append(c3)

    return clusters


def create_mock_one(clusters):
    """Create mock OpenNebula client with clusters."""
    mock_clusterpool_result = Mock()
    mock_clusterpool_result.CLUSTER = clusters

    mock_one = Mock()
    mock_one.clusterpool.info.return_value = mock_clusterpool_result

    return mock_one


def test_no_filters():
    """Test with no filters - should return all clusters sorted by distance."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",  # Near cluster 1
        flavour="TestOVH",
        is_confidential=None,
        providers=None,
        target_cardinality=None
    )

    assert result == [1, 3, 2]  # Sorted by distance: closest first


def test_confidential_filter():
    """Test filtering by confidential requirement."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    # Request confidential clusters only
    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",
        flavour="TestOVH",
        is_confidential="True",
        providers=None,
        target_cardinality=None
    )

    assert result == [2]  # Only cluster 2 is confidential


def test_non_confidential_filter():
    """Test filtering by non-confidential requirement."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    # Request non-confidential clusters only
    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",
        flavour="TestOVH",
        is_confidential="False",
        providers=None,
        target_cardinality=None
    )

    assert result == [1, 3]  # Clusters 1 and 3 are non-confidential


def test_provider_filter():
    """Test filtering by provider requirement."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    # Request clusters with provider_1
    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",
        flavour="TestOVH",
        is_confidential=None,
        providers="['provider_1']",  # String representation of list
        target_cardinality=None
    )

    assert result == [1, 3]  # Clusters 1 and 3 have provider_1


def test_capacity_filter():
    """Test filtering by capacity requirement."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    # Request clusters with capacity >= 20
    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",
        flavour="TestOVH",
        is_confidential=None,
        providers=None,
        target_cardinality="20"
    )

    assert result == [2]  # Only cluster 2 has capacity >= 20


def test_combined_filters():
    """Test multiple filters combined."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    # Request non-confidential clusters with provider_1 and capacity >= 12
    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",
        flavour="TestOVH",
        is_confidential="False",
        providers="['provider_1']",
        target_cardinality="12"
    )

    assert result == [1]  # Only cluster 1 matches all criteria


def test_wrong_flavour():
    """Test that clusters with wrong flavour are filtered out."""
    clusters = create_mock_clusters()
    mock_one = create_mock_one(clusters)

    # Request Nature flavour, but all clusters are TestOVH
    result = clusters_ids_get(
        mock_one,
        geolocation="43.05,-2.53",
        flavour="Nature",
        is_confidential=None,
        providers=None,
        target_cardinality=None
    )

    assert result == []  # No clusters match


if __name__ == "__main__":
    # Run all tests
    test_no_filters()
    test_confidential_filter()
    test_non_confidential_filter()
    test_provider_filter()
    test_capacity_filter()
    test_combined_filters()
    test_wrong_flavour()
