from typing import Any, List, Dict, Optional, Union, Callable
import operator
from ...core.collection import ColumnCollection
from ...core.column import Column
from ..registry import operation


@operation(domain="core")
def search_by_value(
    collection: ColumnCollection, column_name: str, op_str: str, value: Any
) -> ColumnCollection:
    """値による検索
    Args:
        collection: 対象コレクション
        column_name: 列名
        op_str: 演算子文字列 (">", "<", ">=", "<=", "==", "!=")
        value: 比較する値
    Returns:
        ColumnCollection: フィルタリングされたコレクション
    """
    # 演算子マッピング
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
    }
    
    # 演算子の検証
    if op_str not in ops:
        raise ValueError(f"演算子 '{op_str}' は無効です。有効な演算子: {list(ops.keys())}")
    
    # 指定された列が存在するか確認
    if column_name not in collection.columns:
        raise KeyError(f"列 '{column_name}' は存在しません")
    
    # フィルタリング処理
    column = collection.columns[column_name]
    op_func = ops[op_str]
    
    indices = []
    for i, val in enumerate(column.values):
        if val is not None and op_func(val, value):
            indices.append(i)
    
    # 新しいコレクションの作成
    result = collection.clone()
    
    # 指定のインデックスでフィルタリング
    result.step = result.step.__class__(values=[result.step.values[i] for i in indices])
    
    for col_name, col in result.columns.items():
        col.values = [col.values[i] for i in indices]
    
    return result


@operation(domain="core")
def search_by_range(
    collection: ColumnCollection, column_name: str, min_value: Any, max_value: Any, inclusive: bool = True
) -> ColumnCollection:
    """範囲による検索
    Args:
        collection: 対象コレクション
        column_name: 列名
        min_value: 最小値
        max_value: 最大値
        inclusive: 境界値を含むかどうか
    Returns:
        ColumnCollection: フィルタリングされたコレクション
    """
    # 指定された列が存在するか確認
    if column_name not in collection.columns:
        raise KeyError(f"列 '{column_name}' は存在しません")
    
    # 演算子の選択
    if inclusive:
        min_op, max_op = operator.ge, operator.le
    else:
        min_op, max_op = operator.gt, operator.lt
    
    # フィルタリング処理
    column = collection.columns[column_name]
    
    indices = []
    for i, val in enumerate(column.values):
        if val is not None and min_op(val, min_value) and max_op(val, max_value):
            indices.append(i)
    
    # 新しいコレクションの作成
    result = collection.clone()
    
    # 指定のインデックスでフィルタリング
    result.step = result.step.__class__(values=[result.step.values[i] for i in indices])
    
    for col_name, col in result.columns.items():
        col.values = [col.values[i] for i in indices]
    
    return result


@operation(domain="core")
def search_by_step_range(
    collection: ColumnCollection, min_step: Any, max_step: Any, inclusive: bool = True
) -> ColumnCollection:
    """ステップ範囲による検索
    Args:
        collection: 対象コレクション
        min_step: 最小ステップ値
        max_step: 最大ステップ値
        inclusive: 境界値を含むかどうか
    Returns:
        ColumnCollection: フィルタリングされたコレクション
    """
    # 演算子の選択
    if inclusive:
        min_op, max_op = operator.ge, operator.le
    else:
        min_op, max_op = operator.gt, operator.lt
    
    # フィルタリング処理
    indices = []
    for i, val in enumerate(collection.step.values):
        if val is not None and min_op(val, min_step) and max_op(val, max_step):
            indices.append(i)
    
    # 新しいコレクションの作成
    result = collection.clone()
    
    # 指定のインデックスでフィルタリング
    result.step = result.step.__class__(values=[result.step.values[i] for i in indices])
    
    for col_name, col in result.columns.items():
        col.values = [col.values[i] for i in indices]
    
    return result


@operation(domain="core")
def search_by_condition(
    collection: ColumnCollection, condition_func: Callable[[Dict[str, Any]], bool]
) -> ColumnCollection:
    """条件関数による検索
    Args:
        collection: 対象コレクション
        condition_func: 各行データを受け取り、真偽値を返す関数
    Returns:
        ColumnCollection: フィルタリングされたコレクション
    """
    # 各行のデータを辞書に変換
    indices = []
    for i in range(len(collection)):
        row_data = {}
        for col_name, col in collection.columns.items():
            row_data[col_name] = col.values[i] if i < len(col.values) else None
        
        # 条件関数を適用
        if condition_func(row_data):
            indices.append(i)
    
    # 新しいコレクションの作成
    result = collection.clone()
    
    # 指定のインデックスでフィルタリング
    result.step = result.step.__class__(values=[result.step.values[i] for i in indices])
    
    for col_name, col in result.columns.items():
        col.values = [col.values[i] for i in indices]
    
    return result


@operation(domain="core")
def search_missing_values(
    collection: ColumnCollection, columns: Optional[List[str]] = None
) -> ColumnCollection:
    """欠損値がある行を検索
    Args:
        collection: 対象コレクション
        columns: 検査対象の列名リスト（Noneの場合は全列）
    Returns:
        ColumnCollection: 欠損値を持つ行だけのコレクション
    """
    # 検査対象の列を決定
    target_columns = columns if columns is not None else list(collection.columns.keys())
    
    # 列の存在確認
    for col_name in target_columns:
        if col_name not in collection.columns:
            raise KeyError(f"列 '{col_name}' は存在しません")
    
    # 欠損値を持つ行のインデックスを収集
    indices = []
    for i in range(len(collection)):
        has_missing = False
        for col_name in target_columns:
            col = collection.columns[col_name]
            if i >= len(col.values) or col.values[i] is None:
                has_missing = True
                break
        
        if has_missing:
            indices.append(i)
    
    # 新しいコレクションの作成
    result = collection.clone()
    
    # 指定のインデックスでフィルタリング
    result.step = result.step.__class__(values=[result.step.values[i] for i in indices])
    
    for col_name, col in result.columns.items():
        col.values = [col.values[i] for i in indices]
    
    return result


@operation(domain="core")
def search_top_n(
    collection: ColumnCollection, column_name: str, n: int, descending: bool = True
) -> ColumnCollection:
    """指定した列の上位N件を検索
    Args:
        collection: 対象コレクション
        column_name: 列名
        n: 上位件数
        descending: 降順ソート（True）または昇順ソート（False）
    Returns:
        ColumnCollection: フィルタリングされたコレクション
    """
    # 列が存在するか確認
    if column_name not in collection.columns:
        raise KeyError(f"列 '{column_name}' は存在しません")
    
    # インデックスと値のペアを作成し、ソート
    column = collection.columns[column_name]
    pairs = [(i, val) for i, val in enumerate(column.values) if val is not None]
    pairs.sort(key=lambda x: x[1], reverse=descending)
    
    # 上位N件のインデックスを取得
    indices = [pair[0] for pair in pairs[:n]]
    indices.sort()  # 元の順序でインデックスをソート
    
    # 新しいコレクションの作成
    result = collection.clone()
    
    # 指定のインデックスでフィルタリング
    result.step = result.step.__class__(values=[result.step.values[i] for i in indices])
    
    for col_name, col in result.columns.items():
        col.values = [col.values[i] for i in indices]
    
    return result