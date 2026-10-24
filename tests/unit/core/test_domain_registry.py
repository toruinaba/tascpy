import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Self

import pytest

from tascpy.core.collection import ColumnCollection, domain_class
from tascpy.core.io import load_parquet, save_parquet

SRC = Path(__file__).resolve().parents[3] / "src"


class _TaggedCollection(ColumnCollection):
    """テスト用の外部ドメイン（core を変更せずに追加できることの確認）"""

    domain = "test_tagged"

    @classmethod
    def from_collection(cls, collection: ColumnCollection, *, tag: Optional[str] = None) -> Self:
        new = collection._as_class(cls)
        new._tag = tag
        return new

    @classmethod
    def _from_config(cls, collection: ColumnCollection, config: Mapping[str, Any]) -> Self:
        return cls.from_collection(collection, **config)

    def _domain_config(self) -> Dict[str, Any]:
        return {"tag": self._tag}


def test_subclass_with_domain_is_registered():
    assert domain_class("test_tagged") is _TaggedCollection
    assert domain_class("core") is ColumnCollection


def test_external_domain_roundtrips_through_parquet(tmp_path):
    col = _TaggedCollection.from_collection(ColumnCollection({"A": [1.0, 2.0]}), tag="x")
    save_parquet(col, tmp_path / "t.parquet")
    loaded = load_parquet(tmp_path / "t.parquet")
    assert isinstance(loaded, _TaggedCollection)
    assert loaded._tag == "x"


def test_unknown_domain_raises():
    with pytest.raises(ValueError, match="登録されていません"):
        domain_class("no_such_domain")


def test_top_level_load_parquet_registers_builtin_domains(tmp_path):
    path = tmp_path / "ld.parquet"
    code = f"""
        import tascpy
        from tascpy.domains import as_load_displacement
        col = tascpy.ColumnCollection({{"P": [0.0, 1.0], "d": [0.0, 1.0]}})
        col.ops.as_domain(as_load_displacement, "P", "d").end().io.to_parquet({str(path)!r})
    """
    reload_code = f"""
        import tascpy
        loaded = tascpy.load_parquet({str(path)!r})
        assert type(loaded).__name__ == "LoadDisplacementCollection", type(loaded)
        assert loaded.load_column == "P"
    """
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    for snippet in (code, reload_code):
        result = subprocess.run([sys.executable, "-c", textwrap.dedent(snippet)], env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
