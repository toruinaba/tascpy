from typing import Union, Optional, List, Dict, Any
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation


@operation(domain="core")
def add(
    collection: ColumnCollection,
    column1: str,
    column2_or_value: Union[str, int, float],
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """列または定数を加算

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 加算元の列名
        column2_or_value: 加算する列名または定数値
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 演算結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、または無効な値が指定された場合
    """
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values1 = collection[column1].values
    
    # 結果の列名を決定
    if result_column is None:
        if isinstance(column2_or_value, str):
            result_column = f"{column1}+{column2_or_value}"
        else:
            result_column = f"{column1}+{column2_or_value}"
    
    # 列同士の演算か定数との演算かを判定
    if isinstance(column2_or_value, str):
        # 列同士の演算
        if column2_or_value not in collection.columns:
            raise KeyError(f"列 '{column2_or_value}' が存在しません")
        
        values2 = collection[column2_or_value].values
        
        # 列のサイズチェック
        if len(values1) != len(values2):
            raise ValueError(f"列のサイズが一致しません: {column1}({len(values1)}) != {column2_or_value}({len(values2)})")
        
        # 加算処理
        result_values = [
            v1 + v2 if v1 is not None and v2 is not None else None
            for v1, v2 in zip(values1, values2)
        ]
    else:
        # 定数との演算
        try:
            value = float(column2_or_value)
            # 加算処理
            result_values = [
                v + value if v is not None else None
                for v in values1
            ]
        except (ValueError, TypeError):
            raise ValueError(f"無効な値が指定されました: {column2_or_value}")
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        from ...core.column import Column
        # 元の列の単位を継承
        original_column = collection[column1]
        unit = original_column.unit if hasattr(original_column, "unit") else None
        # detect_column_typeを正しく呼び出す
        column = detect_column_type(None, result_column, unit, result_values)
        result.add_column(result_column, column)
    
    return result


@operation(domain="core")
def subtract(
    collection: ColumnCollection,
    column1: str,
    column2_or_value: Union[str, int, float],
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """列または定数を減算

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 減算元の列名
        column2_or_value: 減算する列名または定数値
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 演算結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、または無効な値が指定された場合
    """
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values1 = collection[column1].values
    
    # 結果の列名を決定
    if result_column is None:
        if isinstance(column2_or_value, str):
            result_column = f"{column1}-{column2_or_value}"
        else:
            result_column = f"{column1}-{column2_or_value}"
    
    # 列同士の演算か定数との演算かを判定
    if isinstance(column2_or_value, str):
        # 列同士の演算
        if column2_or_value not in collection.columns:
            raise KeyError(f"列 '{column2_or_value}' が存在しません")
        
        values2 = collection[column2_or_value].values
        
        # 列のサイズチェック
        if len(values1) != len(values2):
            raise ValueError(f"列のサイズが一致しません: {column1}({len(values1)}) != {column2_or_value}({len(values2)})")
        
        # 減算処理
        result_values = [
            v1 - v2 if v1 is not None and v2 is not None else None
            for v1, v2 in zip(values1, values2)
        ]
    else:
        # 定数との演算
        try:
            value = float(column2_or_value)
            # 減算処理
            result_values = [
                v - value if v is not None else None
                for v in values1
            ]
        except (ValueError, TypeError):
            raise ValueError(f"無効な値が指定されました: {column2_or_value}")
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列の単位を継承
        original_column = collection[column1]
        unit = original_column.unit if hasattr(original_column, "unit") else None
        # detect_column_typeを正しく呼び出す
        column = detect_column_type(None, result_column, unit, result_values)
        result.add_column(result_column, column)
    
    return result


@operation(domain="core")
def multiply(
    collection: ColumnCollection,
    column1: str,
    column2_or_value: Union[str, int, float],
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """列または定数を乗算

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 乗算元の列名
        column2_or_value: 乗算する列名または定数値
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 演算結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、または無効な値が指定された場合
    """
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values1 = collection[column1].values
    
    # 結果の列名を決定
    if result_column is None:
        if isinstance(column2_or_value, str):
            result_column = f"{column1}*{column2_or_value}"
        else:
            # カラム名に+や-などが含まれている場合は括弧で囲む
            if any(op in column1 for op in ['+', '-', '*', '/']):
                result_column = f"({column1})*{column2_or_value}"
            else:
                result_column = f"{column1}*{column2_or_value}"
    
    # 列同士の演算か定数との演算かを判定
    if isinstance(column2_or_value, str):
        # 列同士の演算
        if column2_or_value not in collection.columns:
            raise KeyError(f"列 '{column2_or_value}' が存在しません")
        
        values2 = collection[column2_or_value].values
        
        # 列のサイズチェック
        if len(values1) != len(values2):
            raise ValueError(f"列のサイズが一致しません: {column1}({len(values1)}) != {column2_or_value}({len(values2)})")
        
        # 乗算処理
        result_values = [
            v1 * v2 if v1 is not None and v2 is not None else None
            for v1, v2 in zip(values1, values2)
        ]
    else:
        # 定数との演算
        try:
            value = float(column2_or_value)
            # 乗算処理
            result_values = [
                v * value if v is not None else None
                for v in values1
            ]
        except (ValueError, TypeError):
            raise ValueError(f"無効な値が指定されました: {column2_or_value}")
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列の単位を継承
        original_column = collection[column1]
        unit = original_column.unit if hasattr(original_column, "unit") else None
        # detect_column_typeを正しく呼び出す
        column = detect_column_type(None, result_column, unit, result_values)
        result.add_column(result_column, column)
    
    return result


@operation(domain="core")
def divide(
    collection: ColumnCollection,
    column1: str,
    column2_or_value: Union[str, int, float],
    result_column: Optional[str] = None,
    in_place: bool = False,
    handle_zero_division: str = "error"
) -> ColumnCollection:
    """列または定数で除算

    Args:
        collection: ColumnCollectionオブジェクト
        column1: 除算元の列名
        column2_or_value: 除算する列名または定数値
        result_column: 結果を格納する列名（デフォルトはNone、自動生成）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        handle_zero_division: ゼロ除算の処理方法
            "error": ゼロ除算エラーを発生させる
            "none": 結果をNoneとして扱う
            "inf": 結果を無限大（float('inf')）として扱う

    Returns:
        ColumnCollection: 演算結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 列の長さが一致しない場合、無効な値が指定された場合、またはゼロ除算が発生した場合
    """
    # ゼロ除算処理方法のバリデーション
    valid_zero_division_handlers = ["error", "none", "inf"]
    if handle_zero_division not in valid_zero_division_handlers:
        raise ValueError(f"handle_zero_divisionは{valid_zero_division_handlers}のいずれかを指定してください")
    
    # 列の存在チェック
    if column1 not in collection.columns:
        raise KeyError(f"列 '{column1}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values1 = collection[column1].values
    
    # 結果の列名を決定
    if result_column is None:
        if isinstance(column2_or_value, str):
            result_column = f"{column1}/{column2_or_value}"
        else:
            result_column = f"{column1}/{column2_or_value}"
    
    # 列同士の演算か定数との演算かを判定
    if isinstance(column2_or_value, str):
        # 列同士の演算
        if column2_or_value not in collection.columns:
            raise KeyError(f"列 '{column2_or_value}' が存在しません")
        
        values2 = collection[column2_or_value].values
        
        # 列のサイズチェック
        if len(values1) != len(values2):
            raise ValueError(f"列のサイズが一致しません: {column1}({len(values1)}) != {column2_or_value}({len(values2)})")
        
        # 除算処理
        result_values = []
        for v1, v2 in zip(values1, values2):
            if v1 is None or v2 is None:
                result_values.append(None)
            elif v2 == 0:
                # ゼロ除算の処理
                if handle_zero_division == "error":
                    raise ValueError("ゼロによる除算が発生しました")
                elif handle_zero_division == "none":
                    result_values.append(None)
                else:  # "inf"
                    result_values.append(float('inf') if v1 > 0 else float('-inf') if v1 < 0 else float('nan'))
            else:
                result_values.append(v1 / v2)
    else:
        # 定数との演算
        try:
            value = float(column2_or_value)
            if value == 0:
                # ゼロ除算の処理
                if handle_zero_division == "error":
                    raise ValueError("ゼロによる除算が発生しました")
                elif handle_zero_division == "none":
                    result_values = [None for _ in values1]
                else:  # "inf"
                    result_values = [
                        float('inf') if v > 0 else float('-inf') if v < 0 else float('nan')
                        if v is not None else None
                        for v in values1
                    ]
            else:
                # 除算処理
                result_values = [
                    v / value if v is not None else None
                    for v in values1
                ]
        except (ValueError, TypeError) as e:
            # ここで補足されたエラーがゼロ除算エラーの場合は、それを再度発生させる
            if "ゼロによる除算が発生しました" in str(e):
                raise
            # それ以外のエラーは変換エラーとして扱う
            raise ValueError(f"無効な値が指定されました: {column2_or_value}")
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列の単位を継承
        original_column = collection[column1]
        unit = original_column.unit if hasattr(original_column, "unit") else None
        # detect_column_typeを正しく呼び出す
        column = detect_column_type(None, result_column, unit, result_values)
        result.add_column(result_column, column)
    
    return result