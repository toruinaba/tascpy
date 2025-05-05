from typing import Any, Dict, List, Optional, Union, Callable

from ...core.collection import ColumnCollection
from ...core.column import NumberColumn, Column
from ..registry import operation


def linear_interpolate(x_points, y_points, x_new):
    """純粋なPythonで実装した線形内挿関数（範囲外は線形外挿を行う）
    
    Args:
        x_points: 元のx座標値のリスト
        y_points: 元のy座標値のリスト
        x_new: 内挿する新しいx座標値のリスト
        
    Returns:
        内挿されたy座標値のリスト
    """
    y_new = []
    
    # 単一点のケースを特別扱い
    if len(x_points) == 1:
        return [y_points[0]] * len(x_new)
    
    for xi in x_new:
        # 範囲外の値の処理（線形外挿）
        if xi < x_points[0]:
            # 最小値より小さい場合、最初の2点を使って線形外挿
            if len(x_points) >= 2:
                x1, x2 = x_points[0], x_points[1]
                y1, y2 = y_points[0], y_points[1]
                # 勾配を計算
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                # 線形外挿
                yi = y1 + slope * (xi - x1)
                y_new.append(yi)
            else:
                # データが1点しかない場合は最初の値を使用
                y_new.append(y_points[0])
            continue
            
        if xi > x_points[-1]:
            # 最大値より大きい場合、最後の2点を使って線形外挿
            if len(x_points) >= 2:
                x1, x2 = x_points[-2], x_points[-1]
                y1, y2 = y_points[-2], y_points[-1]
                # 勾配を計算
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                # 線形外挿
                yi = y2 + slope * (xi - x2)
                y_new.append(yi)
            else:
                # データが1点しかない場合は最後の値を使用
                y_new.append(y_points[-1])
            continue
            
        # 通常の線形内挿処理（範囲内の値）
        for j in range(len(x_points)-1):
            if x_points[j] <= xi <= x_points[j+1]:
                # 線形補間の式: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
                x1, x2 = x_points[j], x_points[j+1]
                y1, y2 = y_points[j], y_points[j+1]
                
                # 線形補間を計算
                yi = y1 + (xi - x1) * (y2 - y1) / (x2 - x1)
                y_new.append(yi)
                break
    
    return y_new


def linspace(start, stop, num):
    """等間隔の数値シーケンスを生成"""
    if num <= 1:
        return [start]
    
    step = (stop - start) / (num - 1)
    return [start + step * i for i in range(num)]


def find_nearest_index(x_points, x_value):
    """最も近い値のインデックスを探す
    
    距離が等しい場合は小さい方のインデックスを選択
    """
    min_dist = float('inf')
    min_idx = 0
    
    for i, xi in enumerate(x_points):
        dist = abs(xi - x_value)
        if dist < min_dist:
            min_dist = dist
            min_idx = i
            
    return min_idx


@operation(domain="core")
def interpolate(
    collection: ColumnCollection,
    base_column_name: str = "step",  # デフォルトでステップを使用
    x_values: Optional[List[float]] = None,
    point_count: Optional[int] = None,
    method: str = "linear",  # 現状はlinearのみサポート
    columns: Optional[List[str]] = None
) -> ColumnCollection:
    """指定した列の値に基づいてデータを内挿
    
    Args:
        collection: 内挿を行うColumnCollectionオブジェクト
        base_column_name: 内挿の基準となる列名 (デフォルト: "step")
        x_values: 内挿する目標値のリスト 
        point_count: 等間隔内挿を行う場合のポイント数
        method: 内挿方法 (現在は'linear'のみサポート)
        columns: 値の計算に使用する列名リスト (Noneの場合はすべての数値型列)
        
    Returns:
        ColumnCollection: 内挿された新しいColumnCollection
        
    Raises:
        ValueError: x_valuesとpoint_countの両方が指定された場合、または両方が指定されていない場合
        KeyError: 指定された列が存在しない場合
        TypeError: 指定された列が数値型でない場合
        
    Examples:
        # ステップ値に基づいて内挿
        >>> result = collection.ops.interpolate(point_count=100)
        
        # 特定のステップ値で内挿
        >>> result = collection.ops.interpolate(x_values=[1.0, 2.5, 3.0, 4.5])
        
        # position列の値に基づいて内挿
        >>> result = collection.ops.interpolate(
        ...     base_column_name="position", point_count=100
        ... )
    """
    # 内挿メソッドの検証
    if method != "linear":
        raise ValueError("現在はlinear内挿のみサポートしています")
    
    # 基準値の取得
    if base_column_name == "step":
        # ステップ値を使用する場合
        base_values = collection.step.values
    elif base_column_name not in collection.columns:
        raise KeyError(f"列 '{base_column_name}' が存在しません")
    else:
        # 指定した列が存在する場合
        column = collection[base_column_name]
        if not isinstance(column, NumberColumn):
            raise TypeError(f"列 '{base_column_name}' は数値型ではありません")
        
        if column.count_nones() > 0:
            raise ValueError(f"列 '{base_column_name}' にNone値が含まれています")
        
        base_values = column.values
    
    # パラメータチェック
    if x_values is None and point_count is None:
        raise ValueError("x_valuesまたはpoint_countのいずれかを指定してください")
    if x_values is not None and point_count is not None:
        raise ValueError("x_valuesとpoint_countは同時に指定できません")
    
    # 内挿ポイントの生成
    if x_values is None:
        min_val = min(base_values)
        max_val = max(base_values)
        x_values = linspace(min_val, max_val, point_count)
    
    # 内挿の計算に使用する列を決定（数値型のみ）
    calc_columns = []
    if columns is None:
        calc_columns = [
            name for name, col in collection.columns.items()
            if isinstance(col, NumberColumn) and col.count_nones() == 0
        ]
    else:
        for name in columns:
            if name not in collection.columns:
                raise KeyError(f"列 '{name}' が存在しません")
            if not isinstance(collection[name], NumberColumn):
                raise TypeError(f"列 '{name}' は数値型ではありません")
            if collection[name].count_nones() > 0:
                raise ValueError(f"列 '{name}' にNone値が含まれています")
            calc_columns.append(name)
    
    # 内挿に用いる基準列は計算対象から除外
    if base_column_name in calc_columns and base_column_name != "step":
        calc_columns.remove(base_column_name)
    
    # 新しい列データを作成
    new_data = {}
    
    # ステップ値の内挿
    new_steps = linear_interpolate(base_values, collection.step.values, x_values)
    
    # 各列の内挿
    for name, column in collection.columns.items():
        # 数値型かつ内挿計算対象の列は通常の内挿
        if name in calc_columns:
            try:
                new_values = linear_interpolate(base_values, column.values, x_values)
                
                new_column = column.clone()
                new_column.values = new_values
                new_data[name] = new_column
            except Exception as e:
                # 内挿に失敗した場合はNoneで埋める
                new_column = column.clone()
                new_column.values = [None] * len(x_values)
                new_data[name] = new_column
                print(f"Warning: {name} の内挿に失敗しました: {str(e)}")
        else:
            # 数値型でない列または計算対象外の列は最近傍法で値を割り当て
            try:
                # 最近傍法の実装
                new_values = []
                for xi in x_values:
                    # 最も近いインデックスを検索
                    idx = find_nearest_index(base_values, xi)
                    new_values.append(column.values[idx])
                
                new_column = column.clone()
                new_column.values = new_values
                new_data[name] = new_column
            except Exception as e:
                # 内挿に失敗した場合はNoneで埋める
                new_column = column.clone()
                new_column.values = [None] * len(x_values)
                new_data[name] = new_column
                print(f"Warning: {name} の最近傍内挿に失敗しました: {str(e)}")
    
    # 基準列がカラムの場合、それも新しいデータに追加
    if base_column_name != "step" and base_column_name in collection.columns:
        orig_column = collection[base_column_name]
        new_column = orig_column.clone()
        new_column.values = x_values
        new_data[base_column_name] = new_column
    
    # メタデータの処理
    new_metadata = collection.metadata.copy()
    
    # 日付と時間の処理（もし存在すれば）
    for meta_key in ["date", "time"]:
        if meta_key in new_metadata and new_metadata[meta_key]:
            try:
                meta_values = new_metadata[meta_key]
                
                # 最近傍法で日付/時間を内挿
                new_meta_values = []
                for xi in x_values:
                    # 最も近いインデックスを検索
                    idx = find_nearest_index(base_values, xi)
                    new_meta_values.append(meta_values[idx])
                
                new_metadata[meta_key] = new_meta_values
            except:
                new_metadata[meta_key] = [None] * len(x_values)
    
    # 内挿方法と基準列の情報をメタデータに追加
    new_metadata.update({
        "interpolation_method": method,
        "interpolation_basis": base_column_name
    })
    
    return ColumnCollection(new_steps, new_data, new_metadata)