"""docstring と docs/tutorial.md の doctest の準備

docstring の例が使う `col` / `ld` / `coord` / `strain` / `cyclic` は docs/api/sample_data.md のコードブロックで定義し、
ここではそれを実行して doctest の名前空間に入れる（docs とテストの前提を1か所にするため）。
"""

import re
from pathlib import Path

import numpy as np
import pytest

SAMPLE_DATA_DOC = Path(__file__).parent / "docs" / "api" / "sample_data.md"


def sample_namespace() -> dict:
    match = re.search(r"```python\n(.*?)```", SAMPLE_DATA_DOC.read_text(encoding="utf-8"), re.S)
    assert match, f"{SAMPLE_DATA_DOC} に python のコードブロックがありません"
    namespace: dict = {}
    exec(match.group(1), namespace)
    return {name: namespace[name] for name in ("col", "ld", "coord", "strain", "cyclic")}


@pytest.fixture(scope="session", autouse=True)
def _doctest_samples(doctest_namespace):
    doctest_namespace.update(np=np, **sample_namespace())


@pytest.fixture(autouse=True)
def _doctest_workdir(request, tmp_path, monkeypatch):
    """doctest は一時ディレクトリで実行し、読み込みの例に使う data.txt を置いておく（図は終了時に閉じる）"""
    if getattr(request.node, "dtest", None) is None:
        yield
        return
    monkeypatch.chdir(tmp_path)
    sample_namespace()["col"].io.save("data.txt")
    yield
    import matplotlib.pyplot as plt

    plt.close("all")
