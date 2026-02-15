from typing import Any, Optional, Union, List, Dict
from ...core.collection import ColumnCollection
from ...core.column import Column
from ...core.step import Step
from ..registry import operation
from ..abstraction import inject_columns, filter_rows
import numpy as np


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1)
def filter_by_value(
    vals: Union[np.ndarray, List[Any]],
    value: Any,
    tolerance: Optional[float] = None,
) -> List[bool]:
    """指定された列の値が指定された値と等しい行をフィルタリングします

    指定された列の値が特定の値と一致する行だけを含む新しいコレクションを返します。
    許容誤差（tolerance）を指定すると、その範囲内の値も含めることができます。

    Args:
        collection: ColumnCollection オブジェクト
        column_name: フィルタリングする列の名前
        value: フィルタリングする値
        tolerance: 値の許容範囲（デフォルトは None）

    Returns:
        ColumnCollection: フィルタリングされた ColumnCollection オブジェクト

    Raises:
        KeyError: 指定された列名が存在しない場合
        TypeError: 指定された列が Column オブジェクトでない場合
    """
    vals = np.array(vals) if isinstance(vals, list) else vals
    
    # 値のフィルタリング
    if tolerance is not None:
        return [
            (val >= value - tolerance) and (val <= value + tolerance)
            for val in vals
        ]
    else:
        return [val == value for val in vals]


@operation(domain="core")
@filter_rows
def filter_out_none(
    collection: ColumnCollection, columns: Optional[List[str]] = None, mode: str = "any"
) -> List[bool]:
    """None値およびNaN値を含む行をフィルタリングして除外します

    指定された列にNone値またはNaN値を含む行を除外した新しいコレクションを返します。
    モードによって、いずれかの列が欠損値の場合に除外するか、全ての列が欠損値の場合に除外するかを選択できます。

    Args:
        collection: ColumnCollection オブジェクト
        columns: フィルタリングする対象の列名リスト（デフォルトは None、すべての列が対象）
        mode: フィルタリングモード 'any'（いずれかの列が欠損値の行を除外）または
              'all'（すべての列が欠損値の行を除外）

    Returns:
        ColumnCollection: フィルタリングされた ColumnCollection オブジェクト

    Raises:
        ValueError: 不正なモードが指定された場合
        KeyError: 指定された列名が存在しない場合
    """
    import math
    try:
        import numpy as np
        HAS_NUMPY = True
    except ImportError:
        HAS_NUMPY = False

    if mode not in ["any", "all"]:
        raise ValueError("モードは'any'または'all'のいずれかである必要があります")

    # フィルタリング対象の列を決定
    target_columns = columns if columns is not None else list(collection.columns.keys())

    # 指定された列が存在するか確認
    for col_name in target_columns:
        if col_name not in collection.columns:
            raise KeyError(f"列'{col_name}'が存在しません")

    # NoneとNaN値をチェックする関数
    def is_valid_value(value):
        # Noneチェック
        if value is None:
            return False

        # NaNチェック（mathモジュール）
        try:
            if isinstance(value, float) and math.isnan(value):
                return False
        except (TypeError, ValueError):
            pass

        # NumpyのNaNチェック
        if HAS_NUMPY:
            try:
                if isinstance(value, (float, np.number)) and np.isnan(value):
                    return False
            except (TypeError, ValueError):
                pass

        return True

    # NoneとNaN値をフィルタリングするマスクを作成
    if mode == "any":
        # いずれかの列が欠損値の行を除外
        return [
            all(is_valid_value(collection[col_name][i]) for col_name in target_columns)
            for i in range(len(collection.step))
        ]
    else:  # mode == "all"
        # すべての列が欠損値の行を除外
        return [
            any(is_valid_value(collection[col_name][i]) for col_name in target_columns)
            for i in range(len(collection.step))
        ]


@operation(domain="core")
@filter_rows
def remove_consecutive_duplicates_across(
    collection: ColumnCollection, columns: List[str], dup_type: str = "all"
) -> List[int]:
    """複数の列間で共通の連続重複データを削除した新しい ColumnCollection オブジェクトを返します

    すべての指定された列で、連続するデータポイントが同じ値を持つ場合にのみ、
    その重複を 1 つだけ残して削除します。重複判定のタイプによって動作が変わります。

    Args:
        collection: 処理する ColumnCollection オブジェクト
        columns: 処理対象の列名リスト
        dup_type: 重複判定のタイプ
                 'all': すべての列で値に変化がない場合に重複と判定
                 'any': 一部の列だけでも値に変化がある場合は重複と判定しない

    Returns:
        ColumnCollection: 連続する重複を削除したデータを持つ新しい ColumnCollection オブジェクト

    Raises:
        ValueError: 不正な dup_type が指定された場合
        KeyError: 指定された列名が存在しない場合

    Examples:
        >>> # collection["A"] = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]
        >>> # collection["B"] = [10.0, 20.0, 30.0, 30.0, 40.0, 50.0]
        >>> # collection["C"] = [5, 5, 2, 2, 8, 8]
        >>> result = remove_consecutive_duplicates_across(collection, ["A", "B", "C"])
        >>> # result["A"] = [1.0, 1.0, 2.0, 3.0, 3.0]
        >>> # result["B"] = [10.0, 20.0, 30.0, 40.0, 50.0]
        >>> # result["C"] = [5, 5, 2, 8, 8]
    """
    # dup_typeのバリデーション
    if dup_type not in ["all", "any"]:
        raise ValueError("dup_typeは'all'または'any'である必要があります")

    # 指定された列が存在するか確認
    for column_name in columns:
        if column_name not in collection.columns:
            raise KeyError(f"列'{column_name}'が存在しません")

    # データの長さが0の場合は空のコレクションを返す
    if len(collection) == 0:
        return []

    # 保持するインデックスを特定
    indices_to_keep = []

    # 最初のインデックスは常に保持
    indices_to_keep.append(0)

    # 2番目以降のインデックスをチェック
    for i in range(1, len(collection)):
        if dup_type == "all":
            # 「all」モード: すべての列で値が変化していない場合は重複とみなす
            # つまり、いずれかの列で値が変化していれば保持する
            should_keep = False
            for column_name in columns:
                if (
                    collection[column_name].values[i]
                    != collection[column_name].values[i - 1]
                ):
                    should_keep = True
                    break
            if should_keep:
                indices_to_keep.append(i)
        elif dup_type == "any":
            # 「any」モード: いずれかの列でも値が変化していれば保持する
            should_keep = False
            for column_name in columns:
                if (
                    collection[column_name].values[i]
                    != collection[column_name].values[i - 1]
                ):
                    should_keep = True
                    break
            if should_keep:
                indices_to_keep.append(i)

    return indices_to_keep


@operation(domain="core")
@filter_rows
def remove_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[bool]:
    """異常値を検出して除去した新しいコレクションを返します

    移動平均との差分比率を用いた異常値検出を行い、異常値とみなされた行を除外します。
    異常値の検出には detect_outliers 関数を使用します。

    Args:
        collection: 処理対象の ColumnCollection
        column: 異常値を検出する列の名前
        window_size: 移動平均のウィンドウサイズ（奇数推奨）
        threshold: 異常値とみなす移動平均との差分比率の閾値
        edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
        min_abs_value: 比率計算時の最小絶対値
        scale_factor: スケール調整係数

    Returns:
        ColumnCollection: 異常値を除去した新しい ColumnCollection オブジェクト

    Raises:
        KeyError: 指定された列が存在しない場合
        ValueError: 無効なエッジ処理方法やウィンドウサイズが指定された場合、または有効なデータがない場合
    """
    from ..core.stats import detect_outliers

    # 異常値を検出
    outlier_column = f"_temp_outlier_{column}"
    result = detect_outliers(
        collection,
        column=column,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
        result_column=outlier_column,
    )

    # 異常値フラグが1（異常値）のデータポイントを除外するマスクを作成
    # flag == 0 -> 正常値 -> True (Keep)
    return [flag == 0 for flag in result[outlier_column].values]


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1)
def filter_by_condition(
    vals: Any, condition: callable
) -> List[bool]:
    """指定された列の値が条件を満たす行をフィルタリングします

    Args:
        collection: ColumnCollection オブジェクト
        column_name: 条件を適用する列の名前
        condition: 値を引数に取り、bool値を返す関数

    Returns:
        ColumnCollection: 条件を満たす行のみを含む新しいコレクション
    """
    vals = np.array(vals) if isinstance(vals, list) else vals
    return [condition(val) for val in vals]


@operation(domain="core")
@filter_rows
def remove_steps(
    collection: ColumnCollection, steps: List[Any], tolerance: Optional[float] = None
) -> List[bool]:
    """指定されたステップ値を持つ行を削除します

    Args:
        collection: ColumnCollection オブジェクト
        steps: 削除するステップ値のリスト
        tolerance: ステップ値の比較における許容誤差

    Returns:
        ColumnCollection: 指定ステップが削除された新しいコレクション
    """
    import numpy as np

    current_steps = collection.step.values
    steps_to_remove = set(steps)

    if tolerance is None:
        mask = [s not in steps_to_remove for s in current_steps]
    else:
        # toleranceがある場合は近似比較
        mask = []
        steps_arr = np.array(steps)
        for s in current_steps:
            # sがいずれかのremove_stepに近いか?
            is_close = np.any(np.abs(steps_arr - s) <= tolerance)
            mask.append(not is_close)

    return mask


@operation(domain="core")
def filter_val(
    collection: ColumnCollection,
    column_name: str,
    value: Any,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """filter_by_value のエイリアス"""
    return filter_by_value(
        collection, column_name, value, tolerance=tolerance
    )


@operation(domain="core")
def filter_cond(
    collection: ColumnCollection, column_name: str, condition: callable
) -> ColumnCollection:
    """filter_by_condition のエイリアス"""
    return filter_by_condition(collection, column_name, condition)


@operation(domain="core")
def rm_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> ColumnCollection:
    """remove_outliers のエイリアス"""
    return remove_outliers(
        collection,
        column,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )

