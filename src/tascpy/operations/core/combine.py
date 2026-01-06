"""Columnの合成操作

このモジュールでは、2つのColumnを合成するための操作関数を提供します。
特に、ステップやインデックスを基準にした条件付き合成やブレンド操作に焦点を当てています。
"""

from typing import Union, Optional, List, Dict, Any, Callable, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation


@operation(domain="core")
def switch_by_step(
    collection: ColumnCollection,
    column1: str,
    column2: str,
    threshold: Union[int, float],
    compare_mode: str = "value",  # "value" と "index" を意味的に反転
    by_step_value: bool = True,  # 追加：ステップ値を使うかインデックスを使うか
    result_column: Optional[str] = None,
    in_place: bool = False,
    tolerance: Optional[float] = None,  # 追加：ステップ値検索の許容範囲
) -> ColumnCollection:
    """ステップ値を基準に2つのColumnを切り替える

    指定されたステップ値またはインデックスを境界として、それより前はcolumn1、
    それ以降はcolumn2の値を使用した新しいColumnを生成します。

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 閾値より前（または以下）の値を取得する列名
        column2: 閾値より後（または以上）の値を取得する列名
        threshold: 切り替え基準となる値
            by_step_value=True かつ compare_mode="value" の場合：ステップ値
            by_step_value=True かつ compare_mode="index" の場合：ステップ値でインデックスを検索
            by_step_value=False の場合：インデックス値
        compare_mode: 比較モード ("value": ステップの値, "index": インデックス位置)
        by_step_value: Trueの場合はステップ値として解釈、Falseの場合はインデックスとして解釈
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        tolerance: ステップ値検索時の許容範囲（by_step_value=Trueの場合のみ有効）

    Returns:
        ColumnCollection: 切り替え結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、または無効な値が指定された場合
    """
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    if column2 not in collection.columns:
        raise KeyError(f"列 '{column2}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values1 = collection[column1].values
    values2 = collection[column2].values

    if len(values1) != len(values2):
        raise ValueError(f"列の長さが一致しません: {len(values1)} vs {len(values2)}")

    # ステップの取得
    steps = collection.step.values

    # 結果の列名を決定
    if result_column is None:
        mode_str = "step" if by_step_value else "index"
        result_column = f"switch({column1},{column2}@{threshold}_{mode_str})"

    # 新しい値の生成
    new_values = []

    # しきい値の処理
    threshold_idx = threshold
    if by_step_value and compare_mode == "index":
        # ステップ値からインデックスに変換
        threshold_idx = collection.step.find_step_index(
            threshold, tolerance=tolerance, default=len(collection) // 2
        )
        if threshold_idx is None:
            # 見つからない場合はデフォルト値（中間点）を使用
            threshold_idx = len(collection) // 2
            # 警告メッセージをメタデータに追加
            if "warnings" not in result.metadata:
                result.metadata["warnings"] = []
            result.metadata["warnings"].append(
                f"ステップ値 {threshold} が見つかりませんでした。インデックス {threshold_idx} を使用します。"
            )

    for i, step_val in enumerate(steps):
        if compare_mode == "value":
            # ステップ値による比較
            if by_step_value:
                # ステップ値を直接比較
                comparison_value = step_val
                use_column1 = comparison_value < threshold
            else:
                # インデックス値で比較
                comparison_value = i
                use_column1 = comparison_value < threshold
        else:  # compare_mode == "index"
            # インデックス位置による比較
            use_column1 = i < threshold_idx

        # 値の選択
        if use_column1:
            new_values.append(values1[i])
        else:
            new_values.append(values2[i])

    # 新しい列を追加
    # 元の列の単位を継承
    original_column = collection[column1]
    unit = original_column.unit if hasattr(original_column, "unit") else None
    # detect_column_typeを正しく呼び出す
    column = detect_column_type(None, result_column, unit, new_values)
    result.add_column(result_column, column)

    # メタデータを更新
    result.metadata.update(
        {
            "operation": "switch_by_step",
            "by_step_value": by_step_value,
            "compare_mode": compare_mode,
            "threshold": threshold,
        }
    )

    return result


@operation(domain="core")
def blend_by_step(
    collection: ColumnCollection,
    column1: str,
    column2: str,
    start: Union[int, float],
    end: Union[int, float],
    compare_mode: str = "value",  # "value" と "index" を意味的に反転
    by_step_value: bool = True,  # 追加：ステップ値を使うかインデックスを使うか
    blend_method: str = "linear",
    result_column: Optional[str] = None,
    in_place: bool = False,
    tolerance: Optional[float] = None,  # 追加：ステップ値検索の許容範囲
) -> ColumnCollection:
    """ステップ値の範囲内で2つのColumnをブレンドする

    指定された開始点から終了点までの間で、column1からcolumn2へ徐々に
    ブレンドした新しいColumnを生成します。開始点より前はcolumn1、終了点より後は
    column2の値のみを使用します。

    Args:
        collection: ColumnCollectionオブジェクト
        column1: ブレンド開始時（または範囲外の低い方）の値を取得する列名
        column2: ブレンド終了時（または範囲外の高い方）の値を取得する列名
        start: ブレンド開始点
            by_step_value=True かつ compare_mode="value" の場合：ステップ値
            by_step_value=True かつ compare_mode="index" の場合：ステップ値でインデックスを検索
            by_step_value=False の場合：インデックス値
        end: ブレンド終了点
            by_step_value=True かつ compare_mode="value" の場合：ステップ値
            by_step_value=True かつ compare_mode="index" の場合：ステップ値でインデックスを検索
            by_step_value=False の場合：インデックス値
        compare_mode: 比較モード ("value": ステップの値, "index": インデックス位置)
        by_step_value: Trueの場合はステップ値として解釈、Falseの場合はインデックスとして解釈
        blend_method: ブレンド方法 ("linear", "smooth", "log", "exp")
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        tolerance: ステップ値検索時の許容範囲（by_step_value=Trueの場合のみ有効）

    Returns:
        ColumnCollection: ブレンド結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、または無効な値や範囲が指定された場合
    """
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    if column2 not in collection.columns:
        raise KeyError(f"列 '{column2}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values1 = collection[column1].values
    values2 = collection[column2].values

    if len(values1) != len(values2):
        raise ValueError(f"列の長さが一致しません: {len(values1)} vs {len(values2)}")

    # ステップの取得
    steps = collection.step.values

    # 結果の列名を決定
    if result_column is None:
        mode_str = "step" if by_step_value else "index"
        result_column = f"blend({column1},{column2},{start}-{end}_{mode_str})"

    # ブレンド関数の選択
    blend_functions = {
        "linear": lambda t: t,  # 線形補間
        "smooth": lambda t: 3 * t**2 - 2 * t**3,  # スムーズなS字カーブ
        "log": lambda t: np.log(t * 9 + 1)
        / np.log(10),  # 対数的（初めは遅く、後に速く）
        "exp": lambda t: (np.exp(t) - 1)
        / (np.exp(1) - 1),  # 指数的（初めは速く、後に遅く）
    }

    if blend_method not in blend_functions:
        raise ValueError(
            f"無効なブレンドメソッド: {blend_method}。有効なオプション: {', '.join(blend_functions.keys())}"
        )

    blend_func = blend_functions[blend_method]

    # ステップ値/インデックスの変換処理
    start_idx = start
    end_idx = end

    # 初期値チェック
    if compare_mode == "value" and by_step_value:
        # ステップ値の範囲チェック
        if end <= start:
            raise ValueError(
                f"終了値({end})は開始値({start})より大きくなければなりません"
            )
    elif compare_mode == "index" and by_step_value:
        # ステップ値からインデックスに変換
        start_idx = collection.step.find_step_index(
            start, tolerance=tolerance, default=None
        )
        end_idx = collection.step.find_step_index(
            end, tolerance=tolerance, default=None
        )

        # 見つからない場合はデフォルト値を使用
        if start_idx is None:
            start_idx = 0
            # 警告メッセージをメタデータに追加
            if "warnings" not in result.metadata:
                result.metadata["warnings"] = []
            result.metadata["warnings"].append(
                f"ステップ値 {start} が見つかりませんでした。インデックス {start_idx} を使用します。"
            )

        if end_idx is None:
            end_idx = len(collection) - 1
            # 警告メッセージをメタデータに追加
            if "warnings" not in result.metadata:
                result.metadata["warnings"] = []
            result.metadata["warnings"].append(
                f"ステップ値 {end} が見つかりませんでした。インデックス {end_idx} を使用します。"
            )

        # インデックス範囲のチェック
        if end_idx <= start_idx:
            raise ValueError(
                f"終了インデックス({end_idx})は開始インデックス({start_idx})より大きくなければなりません"
            )
    else:  # インデックス直接指定の場合
        if end <= start:
            raise ValueError(
                f"終了インデックス({end})は開始インデックス({start})より大きくなければなりません"
            )

    # 新しい値の生成
    new_values = []

    for i, step_val in enumerate(steps):
        # 比較する値を決定
        if compare_mode == "value":
            if by_step_value:
                # ステップ値を直接比較
                comparison_value = step_val

                if comparison_value < start:
                    # 開始ステップ値より前は最初の列の値
                    new_values.append(values1[i])
                elif comparison_value > end:
                    # 終了ステップ値より後は2番目の列の値
                    new_values.append(values2[i])
                else:
                    # ブレンド範囲内では徐々に切り替え
                    t = (comparison_value - start) / (end - start)
                    t_transformed = blend_func(t)
                    blended_value = (
                        values1[i] * (1 - t_transformed) + values2[i] * t_transformed
                    )
                    new_values.append(blended_value)
            else:
                # インデックス値を直接比較
                comparison_value = i

                if comparison_value < start:
                    new_values.append(values1[i])
                elif comparison_value > end:
                    new_values.append(values2[i])
                else:
                    t = (comparison_value - start) / (end - start)
                    t_transformed = blend_func(t)
                    blended_value = (
                        values1[i] * (1 - t_transformed) + values2[i] * t_transformed
                    )
                    new_values.append(blended_value)
        else:  # compare_mode == "index"
            # インデックスでの比較
            if i < start_idx:
                new_values.append(values1[i])
            elif i > end_idx:
                new_values.append(values2[i])
            else:
                t = (i - start_idx) / (end_idx - start_idx)
                t_transformed = blend_func(t)
                blended_value = (
                    values1[i] * (1 - t_transformed) + values2[i] * t_transformed
                )
                new_values.append(blended_value)

    # 新しい列を追加
    # 元の列の単位を継承
    original_column = collection[column1]
    unit = original_column.unit if hasattr(original_column, "unit") else None
    # detect_column_typeを正しく呼び出す
    column = detect_column_type(None, result_column, unit, new_values)
    result.add_column(result_column, column)

    # メタデータを更新
    result.metadata.update(
        {
            "operation": "blend_by_step",
            "by_step_value": by_step_value,
            "compare_mode": compare_mode,
            "start": start,
            "end": end,
            "blend_method": blend_method,
        }
    )

    return result


@operation(domain="core")
def conditional_select(
    collection: ColumnCollection,
    column1: str,
    column2: str,
    condition_column: str,
    threshold: Union[int, float] = 0,
    compare: str = ">",
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """条件に基づいて2つのColumnから選択的に値を取得

    指定された条件列の値と閾値を比較し、条件を満たす場合はcolumn1、
    それ以外の場合はcolumn2の値を使用した新しいColumnを生成します。

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 条件を満たす場合に使用する列名
        column2: 条件を満たさない場合に使用する列名
        condition_column: 条件判定に使用する列名
        threshold: 条件判定の閾値
        compare: 比較演算子 (">", ">=", "<", "<=", "==", "!=")
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 条件選択結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、または無効な比較演算子が指定された場合
    """
    # 列の存在チェック
    for col in [column1, column2, condition_column]:
        if col not in collection.columns:
            raise KeyError(f"列 '{col}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values1 = collection[column1].values
    values2 = collection[column2].values
    cond_values = collection[condition_column].values

    # 入力検証
    lengths = [len(values1), len(values2), len(cond_values)]
    if len(set(lengths)) > 1:
        raise ValueError(f"すべての列の長さが一致する必要があります: {lengths}")

    # 比較演算子の検証と関数マッピング
    compare_ops = {
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
    }

    if compare not in compare_ops:
        raise ValueError(
            f"無効な比較演算子: {compare}。有効なオプション: {', '.join(compare_ops.keys())}"
        )

    compare_func = compare_ops[compare]

    # 結果の列名を決定
    if result_column is None:
        result_column = (
            f"select({column1},{column2},where:{condition_column}{compare}{threshold})"
        )

    # 新しい値の生成
    new_values = []

    for i in range(len(cond_values)):
        if cond_values[i] is not None and compare_func(cond_values[i], threshold):
            new_values.append(values1[i])
        else:
            new_values.append(values2[i])

    # 新しい列を追加
    # 元の列の単位を継承
    original_column = collection[column1]
    unit = original_column.unit if hasattr(original_column, "unit") else None
    # detect_column_typeを正しく呼び出す
    column = detect_column_type(None, result_column, unit, new_values)
    result.add_column(result_column, column)

    return result


@operation(domain="core")
def custom_combine(
    collection: ColumnCollection,
    column1: str,
    column2: str,
    combine_func: Callable[[Any, Any], Any],
    result_column: Optional[str] = None,
    func_name: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """カスタム関数を使用して2つのColumnを合成

    指定されたカスタム関数を使用して、2つの列の値を要素ごとに合成した
    新しいColumnを生成します。

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 1つ目の入力列名
        column2: 2つ目の入力列名
        combine_func: 2つの値を受け取り1つの値を返す関数
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        func_name: 関数名（自動生成される列名で使用される識別子）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: カスタム合成結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合
    """
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    if column2 not in collection.columns:
        raise KeyError(f"列 '{column2}' が存在しません")

    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()

    # 列の値を取得
    values1 = collection[column1].values
    values2 = collection[column2].values

    if len(values1) != len(values2):
        raise ValueError(f"列の長さが一致しません: {len(values1)} vs {len(values2)}")

    # 関数名の取得（デフォルトは関数のオブジェクト名）
    if func_name is None:
        func_name = (
            combine_func.__name__ if hasattr(combine_func, "__name__") else "custom"
        )

    # 結果の列名を決定
    if result_column is None:
        result_column = f"{func_name}({column1},{column2})"

    # 新しい値の生成
    new_values = []

    for i in range(len(values1)):
        # None値の処理（両方がNoneでない場合のみ計算）
        if values1[i] is None and values2[i] is None:
            new_values.append(None)
        elif values1[i] is None:
            new_values.append(values2[i])  # 1つ目がNoneなら2つ目を使用
        elif values2[i] is None:
            new_values.append(values1[i])  # 2つ目がNoneなら1つ目を使用
        else:
            # 両方の値が有効な場合、合成関数を適用
            new_values.append(combine_func(values1[i], values2[i]))

    # 新しい列を追加
    # 元の列の単位を継承
    original_column = collection[column1]
    unit = original_column.unit if hasattr(original_column, "unit") else None
    # detect_column_typeを正しく呼び出す
    column = detect_column_type(None, result_column, unit, new_values)
    result.add_column(result_column, column)

    return result


@operation(domain="core")
def sum_columns(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """複数の列を合計して新しい列を作成します。
    
    指定した複数の列の値を要素ごとに合計し、新しい列として追加します。
    列名を指定しない場合は、すべての数値列が対象となります。
    
    Args:
        collection: ColumnCollection オブジェクト
        columns: 合計対象の列名リスト（省略時はすべての数値列）
        result_column: 結果を格納する列名（デフォルトは None で自動生成）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
    
    Returns:
        ColumnCollection: 合計列を含む ColumnCollection
    
    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合
    """
    # 対象列の決定
    if columns is None:
        columns = [k for k, v in collection.columns.items() if hasattr(v, "values") and isinstance(v.values, (list, np.ndarray))]
    if not columns:
        raise ValueError("合計対象の列が指定されていません")
    for col in columns:
        if col not in collection.columns:
            raise KeyError(f"列 '{col}' が存在しません")
    # 長さチェック
    lengths = [len(collection[c].values) for c in columns]
    if len(set(lengths)) > 1:
        raise ValueError(f"すべての列の長さが一致する必要があります: {lengths}")
    # 合計計算
    stacked = np.stack([collection[c].values for c in columns], axis=0)
    new_values = np.sum(stacked, axis=0)
    # 結果の列名
    if result_column is None:
        result_column = f"sum({'_'.join(columns)})"
    # 元の列の単位を継承（最初の列）
    original_column = collection[columns[0]]
    unit = getattr(original_column, "unit", None)
    column = detect_column_type(None, result_column, unit, new_values)
    result = collection if in_place else collection.clone()
    result.add_column(result_column, column)
    return result


@operation(domain="core")
def average_columns(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """複数の列の平均値を計算して新しい列を作成します。
    
    指定した複数の列の値を要素ごとに平均し、新しい列として追加します。
    列名を指定しない場合は、すべての数値列が対象となります。
    
    Args:
        collection: ColumnCollection オブジェクト
        columns: 平均対象の列名リスト（省略時はすべての数値列）
        result_column: 結果を格納する列名（デフォルトは None で自動生成）
        in_place: True の場合は元のオブジェクトを変更、False の場合は新しいオブジェクトを作成
    
    Returns:
        ColumnCollection: 平均列を含む ColumnCollection
    
    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合
    """
    # 対象列の決定
    if columns is None:
        columns = [k for k, v in collection.columns.items() if hasattr(v, "values") and isinstance(v.values, (list, np.ndarray))]
    if not columns:
        raise ValueError("平均対象の列が指定されていません")
    for col in columns:
        if col not in collection.columns:
            raise KeyError(f"列 '{col}' が存在しません")
    # 長さチェック
    lengths = [len(collection[c].values) for c in columns]
    if len(set(lengths)) > 1:
        raise ValueError(f"すべての列の長さが一致する必要があります: {lengths}")
    # 平均計算
    stacked = np.stack([collection[c].values for c in columns], axis=0)
    new_values = np.mean(stacked, axis=0)
    # 結果の列名
    if result_column is None:
        result_column = f"average({'_'.join(columns)})"
    # 元の列の単位を継承（最初の列）
    original_column = collection[columns[0]]
    unit = getattr(original_column, "unit", None)
    column = detect_column_type(None, result_column, unit, new_values)
    result = collection if in_place else collection.clone()
    result.add_column(result_column, column)
    return result
