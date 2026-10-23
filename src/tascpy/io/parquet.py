"""Parquet 形式の保存・読み込み（列メタ・メタデータ・解析結果・ドメイン設定まで保持する）

データは Parquet の列として、それ以外は JSON にして Parquet のファイルメタデータ "tascpy" に格納します。
メタデータ・属性・解析結果は JSON で表せる値（数値・文字列・真偽値・None・list・dict、numpy のスカラー/配列）に限ります。
"""

import json
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import polars as pl

from ..core.collection import ColumnCollection
from ..core.column import Column, ColumnMeta
from ..core.result import AnalysisResult, GridResult, PointResult, ScalarResult, XYSeriesResult

METADATA_KEY = "tascpy"
FORMAT_VERSION = 1


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (tuple, set)):
        return list(value)
    raise TypeError(f"JSON で保存できない値です: {type(value).__name__}")


def _result_to_dict(result: AnalysisResult) -> Dict[str, Any]:
    if isinstance(result, ScalarResult):
        return {"type": "scalar", "name": result.name, "value": result.value, "unit": result.unit,
                "metadata": result.metadata}
    if isinstance(result, PointResult):
        return {"type": "point", "name": result.name, "x": result.x, "y": result.y,
                "x_unit": result.x_unit, "y_unit": result.y_unit, "metadata": result.metadata}
    if isinstance(result, XYSeriesResult):
        axes = {axis: {"name": col.name, "values": col.to_list(), "unit": col.unit, "ch": col.ch,
                       "attrs": dict(col.attrs)}
                for axis, col in (("x", result.x), ("y", result.y))}
        return {"type": "xy_series", "name": result.name, **axes, "metadata": result.metadata}
    if isinstance(result, GridResult):
        return {"type": "grid", "name": result.name, "x": result.x, "y": result.y,
                "values": [[None if np.isnan(v) else float(v) for v in row] for row in result.values],
                "unit": result.unit, "metadata": result.metadata}
    raise TypeError(f"Parquet に保存できない解析結果の型です: {type(result).__name__}")


def _result_from_dict(data: Dict[str, Any]) -> AnalysisResult:
    kind = data["type"]
    if kind == "scalar":
        return ScalarResult(data["name"], data["value"], data["unit"], data["metadata"])
    if kind == "point":
        return PointResult(data["name"], data["x"], data["y"], data["x_unit"], data["y_unit"], data["metadata"])
    if kind == "xy_series":
        x, y = (Column(d["name"], d["values"], unit=d["unit"], ch=d["ch"], attrs=d["attrs"])
                for d in (data["x"], data["y"]))
        return XYSeriesResult(data["name"], x, y, data["metadata"])
    if kind == "grid":
        values = np.array(data["values"], dtype=float).reshape(len(data["y"]), len(data["x"]))
        return GridResult(data["name"], data["x"], data["y"], values, data["unit"], data["metadata"])
    raise ValueError(f"未知の解析結果の型です: {kind}")


def _domain_classes() -> Dict[str, type]:
    from ..domains import CoordinateCollection, LoadDisplacementCollection, StrainCollection

    return {cls.domain: cls for cls in (LoadDisplacementCollection, CoordinateCollection, StrainCollection)}


def save_parquet(collection: ColumnCollection, path: Union[str, Path]) -> None:
    """コレクションを Parquet 形式で保存する（load_parquet で同じ内容に復元できる）

    Raises:
        TypeError: メタデータ・属性・解析結果に JSON で表せない値がある場合
    """
    payload = {
        "version": FORMAT_VERSION,
        "domain": collection.domain,
        "domain_config": collection._domain_config(),
        "meta": {name: {"unit": m.unit, "ch": m.ch, "attrs": dict(m.attrs)} for name, m in collection.meta.items()},
        "metadata": dict(collection.metadata),
        "results": [_result_to_dict(r) for r in collection.results.values()],
    }
    encoded = json.dumps(payload, default=_json_default, ensure_ascii=False)
    collection.df.write_parquet(path, metadata={METADATA_KEY: encoded})


def load_parquet(path: Union[str, Path]) -> ColumnCollection:
    """Parquet ファイルからコレクションを読み込む

    save_parquet で保存したファイルは、列メタ・メタデータ・解析結果・ドメインまで復元します。
    それ以外の Parquet ファイルは、列メタなしの ColumnCollection として読み込みます（"step" 列があれば step に使う）。
    """
    df = pl.read_parquet(path)
    raw = pl.read_parquet_metadata(path).get(METADATA_KEY)
    if raw is None:
        return ColumnCollection.from_frame(df)

    payload = json.loads(raw)
    if payload.get("version") != FORMAT_VERSION:
        raise ValueError(f"未対応の tascpy Parquet 形式のバージョンです: {payload.get('version')}")
    meta = {name: ColumnMeta(unit=m["unit"], ch=m["ch"], attrs=m["attrs"]) for name, m in payload["meta"].items()}
    collection = ColumnCollection.from_frame(df, meta=meta, metadata=payload["metadata"])
    for result in payload["results"]:
        collection = collection.with_result(_result_from_dict(result))

    domain = payload["domain"]
    if domain == ColumnCollection.domain:
        return collection
    classes = _domain_classes()
    if domain not in classes:
        raise ValueError(f"未知のドメインです: {domain}")
    return classes[domain].from_collection(collection, **payload["domain_config"])
