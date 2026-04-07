import pytest
import numpy as np
from tascpy.analytics.functional.coordinate.clustering import simple_kmeans, find_nearest_neighbors_logic

def test_simple_kmeans():
    X = np.array([
        [0.0, 0.0], [0.1, 0.1], [0.2, 0.2],
        [10.0, 10.0], [10.1, 10.1], [10.2, 10.2]
    ])
    labels = simple_kmeans(X, n_clusters=2, max_iter=10)
    assert len(labels) == 6
    
    # Check that they are grouped correctly
    group1 = labels[:3]
    group2 = labels[3:]
    assert np.all(group1 == group1[0])
    assert np.all(group2 == group2[0])
    assert group1[0] != group2[0]

def test_find_nearest_neighbors_logic():
    distances = [
        ("id1", 10.0),
        ("id2", 5.0),
        ("id3", np.nan),
        ("id4", 1.0),
        ("id5", None)
    ]
    
    neighbors = find_nearest_neighbors_logic(distances, n_neighbors=2)
    assert len(neighbors) == 2
    assert neighbors[0][0] == "id4"
    assert neighbors[1][0] == "id2"
    
    # Test more neighbors than available valid
    neighbors_all = find_nearest_neighbors_logic(distances, n_neighbors=10)
    assert len(neighbors_all) == 3
