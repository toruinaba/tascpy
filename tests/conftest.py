import pytest
import os
from pathlib import Path
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

# W-N.txt content for testing
TEST_WN_CONTENT = """無題
ﾃﾞｰﾀ番号\t日付\t時刻\tCH0\tCH1\tCH2\tCH3\tCH4\tCH5\tCH6\tCH7\tCH8\tCH9\tCH10\tCH11\tCH12\tCH13\tCH14\tCH15\tCH16
\t\t\tForce1\tForce2\tDisplacement1\tDisplacement2\tP_total\t梁変位\t梁変位ﾜｲﾔ\tb11\tb21\tb31\tb41\tb51\tb12\tb22\tb32\tb42\tb52
\t\t\tkN\tkN\tmm\tmm\tkN\tmm\tmm\tu\tu\tu\tu\tu\tu\tu\tu\tu\tu
1\t2020/11/30\t17:21:36\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone
2\t2020/11/30\t17:29:40\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone\tnone
3\t2020/12/01\t13:22:11\t0.0\t0.0\t0.00\t0.00\t0.0\t0.0\t0.0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
4\t2020/12/01\t13:22:12\t0.1\t0.1\t0.01\t0.1\t1.0\t0.05\t0.05\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
5\t2020/12/01\t13:22:13\t0.2\t0.2\t0.02\t0.2\t2.0\t0.10\t0.10\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
6\t2020/12/01\t13:22:14\t0.3\t0.3\t0.03\t0.3\t3.0\t0.15\t0.15\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
7\t2020/12/01\t13:22:15\t0.4\t0.4\t0.04\t0.4\t4.0\t0.20\t0.20\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
8\t2020/12/01\t13:22:16\t0.5\t0.5\t0.05\t0.5\t5.0\t0.25\t0.25\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
9\t2020/12/01\t13:22:17\t0.6\t0.6\t0.06\t0.6\t6.0\t0.30\t0.30\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
10\t2020/12/01\t13:22:18\t0.7\t0.7\t0.07\t0.7\t7.0\t0.35\t0.35\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
11\t2020/12/01\t13:22:19\t0.8\t0.8\t0.08\t0.8\t8.0\t0.40\t0.40\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
12\t2020/12/01\t13:22:20\t0.9\t0.9\t0.09\t0.9\t9.0\t0.45\t0.45\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
13\t2020/12/01\t13:22:21\t1.0\t1.0\t0.10\t1.0\t10.0\t0.50\t0.50\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
14\t2020/12/01\t13:22:22\t1.1\t1.1\t0.11\t1.1\t11.0\t0.55\t0.55\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
15\t2020/12/01\t13:22:23\t1.2\t1.2\t0.12\t1.2\t12.0\t0.60\t0.60\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
16\t2020/12/01\t13:22:24\t1.28\t1.28\t0.128\t1.28\t12.8\t0.64\t0.64\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
17\t2020/12/01\t13:22:25\t1.2\t1.2\t0.12\t1.2\t12.0\t0.60\t0.60\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
18\t2020/12/01\t13:22:26\t1.0\t1.0\t0.10\t1.0\t10.0\t0.50\t0.50\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
19\t2020/12/01\t13:22:27\t0.5\t0.5\t0.05\t0.5\t5.0\t0.25\t0.25\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
20\t2020/12/01\t13:22:28\t0.0\t0.0\t0.00\t0.0\t0.0\t0.00\t0.00\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0"""

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def tasc_file(test_data_dir):
    """Create a dummy W-N.txt file"""
    file_path = test_data_dir / "W-N.txt"
    with open(file_path, "w", encoding="shift_jis") as f:
        f.write(TEST_WN_CONTENT)
    return file_path

@pytest.fixture
def large_collection():
    """Create a large ColumnCollection for testing"""
    steps = list(range(100))
    columns = {
        "Time": Column("1", "Time", "s", list(range(100))),
        "Force": Column("2", "Force", "N", [i * 0.5 for i in range(100)]),
        "Displacement": Column(
            "3", "Displacement", "mm", [i * 0.01 for i in range(100)]
        ),
        "Temperature": Column(
            "4", "Temperature", "C", [20 + i * 0.1 for i in range(100)]
        ),
    }
    return ColumnCollection(step=steps, columns=columns)
