from typing import Optional, Any, Dict, List, Union, Tuple, Callable
from datetime import datetime, timedelta
import numpy as np
from ..core.collection import ColumnCollection
from ..core.step import Step


# ドメイン変換関数のレジストリ
_DOMAIN_CONVERTERS = {}


def register_domain_converter(source_domain: str = "core", target_domain: str = None):
    """ドメイン変換関数を登録するデコレータ

    Args:
        source_domain: 変換元のドメイン名
        target_domain: 変換先のドメイン名

    Returns:
        デコレータ関数
    """

    def decorator(func: Callable):
        key = (source_domain, target_domain)
        _DOMAIN_CONVERTERS[key] = func
        return func

    return decorator


def prepare_for_domain_conversion(
    collection: ColumnCollection, target_domain: str, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """ドメイン変換の前準備を行う

    Args:
        collection: 変換元のColumnCollection
        target_domain: 変換先のドメイン名
        **kwargs: 変換パラメータ

    Returns:
        変換準備が完了したColumnCollection と 更新されたkwargs
    """
    # 元のコレクションをクローン
    result = collection.clone()

    # 変換元ドメインを決定（メタデータから取得、なければ "core"）
    source_domain = collection.metadata.get("domain", "core")

    # coreドメインへの変換は汎用関数を使用
    if target_domain == "core" and source_domain != "core":
        return prepare_for_core(result, **kwargs)

    # 登録されている変換関数を探す
    converter_key = (source_domain, target_domain)
    if converter_key in _DOMAIN_CONVERTERS:
        # 登録されている変換関数を実行
        result, mod_kwargs = _DOMAIN_CONVERTERS[converter_key](result, **kwargs)
        return result, mod_kwargs

    # 従来の変換関数で対応（後方互換性のため）
    if target_domain == "timeseries":
        mod_kwargs = _prepare_for_timeseries(result, **kwargs)
        return result, mod_kwargs
    elif target_domain == "signal":
        mod_kwargs = _prepare_for_signal(result, **kwargs)
        return result, mod_kwargs
    elif target_domain == "load_displacement":
        mod_kwargs = _prepare_for_load_displacement(result, **kwargs)
        return result, mod_kwargs

    # 対応する変換関数がない場合は、そのまま返す
    return result, kwargs


def _prepare_for_timeseries(
    collection: ColumnCollection, **kwargs: Any
) -> Dict[str, Any]:
    """時系列ドメインへの変換前処理

    Args:
        collection: 前処理するコレクション
        **kwargs: 変換パラメータ

    Returns:
        更新されたkwargs
    """
    # ステップが数値で、start_dateが指定されている場合は日付に変換
    if (
        len(collection.step.values) > 0
        and not isinstance(collection.step.values[0], datetime)
        and "start_date" in kwargs
    ):

        # 開始日を解析
        if isinstance(kwargs["start_date"], str):
            start_date = datetime.fromisoformat(kwargs["start_date"])
        else:
            start_date = kwargs["start_date"]

        # 頻度を解析（デフォルトは1日）
        freq = kwargs.get("frequency", "1D")
        if freq == "1D":
            delta = timedelta(days=1)
        elif freq == "1H":
            delta = timedelta(hours=1)
        elif freq == "1min" or freq == "1m":
            delta = timedelta(minutes=1)
        elif freq == "1s":
            delta = timedelta(seconds=1)
        else:
            # カスタム形式の解析（例: "2H", "30min"）
            import re

            match = re.match(r"(\d+)([DHMSdhms])", freq)
            if match:
                value, unit = int(match.group(1)), match.group(2).upper()
                if unit == "D":
                    delta = timedelta(days=value)
                elif unit == "H":
                    delta = timedelta(hours=value)
                elif unit == "M":
                    delta = timedelta(minutes=value)
                elif unit == "S":
                    delta = timedelta(seconds=value)
                else:
                    delta = timedelta(days=1)  # デフォルト
            else:
                delta = timedelta(days=1)  # 解析失敗時はデフォルト

        # ステップを日付に変換
        step_values = [
            start_date + (delta * float(step)) for step in collection.step.values
        ]

        # 新しいStepオブジェクトを作成
        collection.step = Step(values=step_values)

        # 使用済みのキーをkwargsから削除
        kwargs.pop("start_date", None)
        return kwargs
    return kwargs


def _prepare_for_signal(collection: ColumnCollection, **kwargs: Any) -> Dict[str, Any]:
    """信号処理ドメインへの変換前処理

    Args:
        collection: 前処理するコレクション
        **kwargs: 変換パラメータ

    Returns:
        更新されたkwargs
    """
    # 日付ステップを時間軸に変換
    if len(collection.step.values) > 0 and isinstance(
        collection.step.values[0], datetime
    ):

        # サンプリングレートを取得
        sample_rate = kwargs.get("sample_rate", 1.0)

        # 開始時間を0とする時間軸に変換
        start_time = collection.step.values[0]
        time_values = [
            (dt - start_time).total_seconds() for dt in collection.step.values
        ]

        # 新しいStepオブジェクトを作成
        collection.step = Step(values=time_values)

        # 元の時間情報をメタデータに保存
        collection.metadata["original_timestamps"] = {
            "start": start_time.isoformat(),
            "sample_rate": sample_rate,
        }

        # 時間が等間隔でない場合、リサンプリングの警告をメタデータに追加
        time_diffs = np.diff(time_values)
        if len(time_diffs) > 0 and np.std(time_diffs) > 1e-6:
            collection.metadata["signal_warning"] = (
                "非等間隔データです。信号処理前にリサンプリングを検討してください。"
            )
        return kwargs
    return kwargs


def _prepare_for_load_displacement(
    collection: ColumnCollection, **kwargs: Any
) -> Dict[str, Any]:
    """一般コレクションから荷重-変位コレクションへの変換準備を行う

    Args:
        collection: 変換元のコレクション
        **kwargs: 追加のパラメータ

    Returns:
        Dict[str, Any]: 更新されたkwargs
    """
    # 荷重カラムと変位カラムを決定
    load_column = kwargs.get("load_column")
    disp_column = kwargs.get("displacement_column")

    # カラム名が指定されていない場合、既存カラムから推測
    if not load_column:
        # 荷重を含むカラム名を探す
        possible_load_columns = ["load", "force", "荷重", "力"]
        for colname in possible_load_columns:
            matching = [
                c for c in collection.columns.keys() if colname.lower() in c.lower()
            ]
            if matching:
                load_column = matching[0]
                break

    if not disp_column:
        # 変位を含むカラム名を探す
        possible_disp_columns = ["disp", "displacement", "変位", "変形"]
        for colname in possible_disp_columns:
            matching = [
                c for c in collection.columns.keys() if colname.lower() in c.lower()
            ]
            if matching:
                disp_column = matching[0]
                break

    # カラム名が見つからない場合は最初の数値カラムを使用
    if not load_column or not disp_column:
        numeric_columns = [
            name
            for name, col in collection.columns.items()
            if any(isinstance(v, (int, float)) for v in col.values)
        ]

        if len(numeric_columns) >= 2:
            if not load_column:
                load_column = numeric_columns[0]
            if not disp_column:
                disp_column = numeric_columns[1]

    # 必要なカラムが見つからない場合はエラー
    if not load_column and not disp_column:
        raise ValueError("荷重と変位のカラムを指定または検出できませんでした")
    elif not load_column:
        raise ValueError("load_column が指定されていないか、検出できませんでした")
    elif not disp_column:
        raise ValueError(
            "displacement_column が指定されていないか、検出できませんでした"
        )

    # 更新されたkwargsを返す
    kwargs.update({"load_column": load_column, "displacement_column": disp_column})

    return kwargs


@register_domain_converter(source_domain="core", target_domain="load_displacement")
def prepare_for_load_displacement(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """一般コレクションから荷重-変位コレクションへの変換準備を行う

    Args:
        collection: 変換元のコレクション
        **kwargs: 追加のパラメータ

    Returns:
        Tuple[ColumnCollection, Dict[str, Any]]:
            (変換用に準備されたコレクション, 更新されたkwargs)
    """
    # 従来の関数を利用して処理
    modified_kwargs = _prepare_for_load_displacement(collection, **kwargs)
    return collection, modified_kwargs


@register_domain_converter(source_domain="core", target_domain="coordinate")
def prepare_for_coordinate(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """一般コレクションから座標コレクションへの変換準備を行う

    Args:
        collection: 変換元のコレクション
        **kwargs: 追加のパラメータ

    Returns:
        Tuple[ColumnCollection, Dict[str, Any]]:
            (変換用に準備されたコレクション, 更新されたkwargs)
    """
    # 座標メタデータキーの設定
    coordinate_metadata_key = kwargs.get("coordinate_metadata_key", "coordinates")

    # 既存のカラムに座標情報が設定されているか確認
    coordinate_columns = {}
    for col_name, col in collection.columns.items():
        if hasattr(col, "metadata") and col.metadata:
            for meta_key, meta_value in col.metadata.items():
                if isinstance(meta_value, dict) and all(
                    k in meta_value for k in ["x", "y"]
                ):
                    # 座標情報っぽいメタデータが見つかった場合
                    coordinate_columns[col_name] = {
                        "x": meta_value.get("x"),
                        "y": meta_value.get("y"),
                        "z": meta_value.get("z", None),
                    }
                    break

    # 座標情報が見つかった場合、それをメタデータキーに設定
    if coordinate_columns:
        for col_name, coords in coordinate_columns.items():
            # メタデータが未設定の場合は初期化
            if not collection.columns[col_name].metadata:
                collection.columns[col_name].metadata = {}

            # 座標情報をメタデータに設定
            collection.columns[col_name].metadata[coordinate_metadata_key] = coords

    # 更新されたkwargsを返す
    kwargs.update({"coordinate_metadata_key": coordinate_metadata_key})
    return collection, kwargs


@register_domain_converter(source_domain="load_displacement", target_domain="core")
def prepare_for_core_from_load_displacement(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """荷重-変位コレクションから一般コレクションへの変換準備を行う

    Args:
        collection: 変換元の荷重-変位コレクション
        **kwargs: 追加のパラメータ

    Returns:
        Tuple[ColumnCollection, Dict[str, Any]]:
            (変換用に準備されたコレクション, 更新されたkwargs)
    """
    # 汎用変換関数を使用
    return prepare_for_core(collection, **kwargs)


@register_domain_converter(source_domain="coordinate", target_domain="core")
def prepare_for_core_from_coordinate(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """座標コレクションから一般コレクションへの変換準備を行う

    Args:
        collection: 変換元の座標コレクション
        **kwargs: 追加のパラメータ

    Returns:
        Tuple[ColumnCollection, Dict[str, Any]]:
            (変換用に準備されたコレクション, 更新されたkwargs)
    """
    # 汎用変換関数を使用
    return prepare_for_core(collection, **kwargs)


def prepare_for_core(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """任意のドメインからcoreドメインへの変換準備を行う汎用関数

    Args:
        collection: 変換元のコレクション
        **kwargs: 追加のパラメータ

    Returns:
        Tuple[ColumnCollection, Dict[str, Any]]:
            (変換用に準備されたコレクション, 更新されたkwargs)
    """
    # 元のドメインを取得
    source_domain = collection.metadata.get("domain", "core")

    # すでにcoreドメインの場合はそのまま返す
    if source_domain == "core":
        return collection, kwargs

    # ドメイン固有の属性や設定を保存
    if "domain_metadata" not in collection.metadata:
        collection.metadata["domain_metadata"] = {}

    domain_metadata = collection.metadata["domain_metadata"]
    if source_domain not in domain_metadata:
        domain_metadata[source_domain] = {}

    # 各ドメイン固有の属性を保存
    if source_domain == "load_displacement":
        # 荷重-変位ドメインの属性を保存
        # __dict__を使用して直接属性を取得
        obj_dict = vars(collection)
        if "_load_column" in obj_dict:
            domain_metadata["load_displacement"]["load_column"] = obj_dict[
                "_load_column"
            ]
        if "_displacement_column" in obj_dict:
            domain_metadata["load_displacement"]["displacement_column"] = obj_dict[
                "_displacement_column"
            ]

    elif source_domain == "coordinate":
        # 座標ドメインの属性を保存
        coordinate_metadata_key = kwargs.get("coordinate_metadata_key", "coordinates")
        if "coordinate_metadata_key" in collection.metadata:
            coordinate_metadata_key = collection.metadata["coordinate_metadata_key"]

        # 座標情報を収集
        coordinates = {}
        for col_name, col in collection.columns.items():
            if (
                hasattr(col, "metadata")
                and col.metadata
                and coordinate_metadata_key in col.metadata
            ):
                coordinates[col_name] = col.metadata[coordinate_metadata_key]

        # 明示的に属性をドメインメタデータに保存
        domain_metadata["coordinate"]["coordinates"] = coordinates
        domain_metadata["coordinate"][
            "coordinate_metadata_key"
        ] = coordinate_metadata_key

    elif source_domain == "timeseries":
        # 時系列ドメインの属性を保存
        frequency = collection.metadata.get("frequency")
        if frequency:
            domain_metadata["timeseries"]["frequency"] = frequency

    elif source_domain == "signal":
        # 信号処理ドメインの属性を保存
        if "original_timestamps" in collection.metadata:
            domain_metadata["signal"]["original_timestamps"] = collection.metadata[
                "original_timestamps"
            ]

        if "sample_rate" in collection.metadata:
            domain_metadata["signal"]["sample_rate"] = collection.metadata[
                "sample_rate"
            ]

    # その他の登録されているドメインの場合は、関連するメタデータを保存
    # ここでは不明な属性も含めて、ドメイン固有のメタデータをすべて保存
    for key, value in collection.metadata.items():
        if key not in ["domain", "domain_metadata"]:
            domain_metadata[source_domain][key] = value

    # 継承した属性やプロパティの取得と保存
    attributes_to_check = ["_domain_specific_attributes", "_custom_properties"]
    for attr_name in attributes_to_check:
        if hasattr(collection, attr_name) and getattr(collection, attr_name):
            domain_metadata[source_domain][attr_name] = getattr(collection, attr_name)

    # ドメイン名をcoreに変更
    collection.metadata["domain"] = "core"

    # 更新されたkwargsを返す
    return collection, kwargs
