import math
from typing import Union, Optional, List, Dict, Any
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation


# 三角関数
@operation(domain="core")
def sin(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    degrees: bool = False
) -> ColumnCollection:
    """指定した列の各値にsin関数を適用

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"sin({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        degrees: Trueの場合、入力をdegreeとして扱う（デフォルトはFalse、ラジアン）

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"sin({column})"
    
    # sin関数適用
    result_values = []
    for value in values:
        if value is None:
            result_values.append(None)
        else:
            try:
                # 度からラジアンに変換
                if degrees:
                    value = math.radians(value)
                result_values.append(math.sin(value))
            except (ValueError, TypeError):
                result_values.append(None)
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


@operation(domain="core")
def cos(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    degrees: bool = False
) -> ColumnCollection:
    """指定した列の各値にcos関数を適用

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"cos({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        degrees: Trueの場合、入力をdegreeとして扱う（デフォルトはFalse、ラジアン）

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"cos({column})"
    
    # cos関数適用
    result_values = []
    for value in values:
        if value is None:
            result_values.append(None)
        else:
            try:
                # 度からラジアンに変換
                if degrees:
                    value = math.radians(value)
                result_values.append(math.cos(value))
            except (ValueError, TypeError):
                result_values.append(None)
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


@operation(domain="core")
def tan(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    degrees: bool = False
) -> ColumnCollection:
    """指定した列の各値にtan関数を適用

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"tan({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        degrees: Trueの場合、入力をdegreeとして扱う（デフォルトはFalse、ラジアン）

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"tan({column})"
    
    # tan関数適用
    result_values = []
    for value in values:
        if value is None:
            result_values.append(None)
        else:
            try:
                # 度からラジアンに変換
                if degrees:
                    value = math.radians(value)
                result_values.append(math.tan(value))
            except (ValueError, TypeError):
                result_values.append(None)
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


# 指数関数/対数関数
@operation(domain="core")
def exp(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """指定した列の各値に指数関数(e^x)を適用

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"exp({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"exp({column})"
    
    # 指数関数適用
    result_values = [
        math.exp(value) if value is not None else None
        for value in values
    ]
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


@operation(domain="core")
def log(
    collection: ColumnCollection,
    column: str,
    base: float = math.e,
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """指定した列の各値に対数関数を適用

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        base: 対数の底（デフォルトはe）
        result_column: 結果を格納する列名（デフォルトはNone、"log({column})"または"log{base}({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 0以下の値に対して対数を適用しようとした場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        if base == math.e:
            result_column = f"log({column})"
        elif base == 10:
            result_column = f"log10({column})"
        else:
            result_column = f"log{base}({column})"
    
    # 対数関数適用
    result_values = []
    for value in values:
        if value is None:
            result_values.append(None)
        else:
            try:
                if value <= 0:
                    result_values.append(None)
                else:
                    if base == math.e:
                        result_values.append(math.log(value))
                    else:
                        result_values.append(math.log(value, base))
            except (ValueError, TypeError):
                result_values.append(None)
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


@operation(domain="core")
def sqrt(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """指定した列の各値の平方根を計算

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"sqrt({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 負の値に対して平方根を適用しようとした場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"sqrt({column})"
    
    # 平方根計算
    result_values = []
    for value in values:
        if value is None:
            result_values.append(None)
        else:
            try:
                if value < 0:
                    result_values.append(None)  # 負の値の平方根は実数では定義されない
                else:
                    result_values.append(math.sqrt(value))
            except (ValueError, TypeError):
                result_values.append(None)
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


@operation(domain="core")
def pow(
    collection: ColumnCollection,
    column: str,
    exponent: float,
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """指定した列の各値を指定した指数でべき乗

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        exponent: べき指数
        result_column: 結果を格納する列名（デフォルトはNone、"{column}^{exponent}"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"{column}^{exponent}"
    
    # べき乗計算
    result_values = []
    for value in values:
        if value is None:
            result_values.append(None)
        else:
            try:
                result_values.append(math.pow(value, exponent))
            except (ValueError, TypeError):
                result_values.append(None)
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


# その他の変換関数
@operation(domain="core")
def abs_values(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """指定した列の各値の絶対値を計算

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"abs({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"abs({column})"
    
    # 絶対値計算
    result_values = [
        # Pythonの組み込みabs関数を明示的に呼び出す
        __builtins__['abs'](value) if value is not None else None
        for value in values
    ]
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result

# 組み込みabs関数との競合を避けるためのエイリアス
# オペレーション名として登録するために必要
abs = abs_values


@operation(domain="core")
def round_values(
    collection: ColumnCollection,
    column: str,
    decimals: int = 0,
    result_column: Optional[str] = None,
    in_place: bool = False
) -> ColumnCollection:
    """指定した列の各値を指定した小数点以下の桁数に丸める

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        decimals: 丸める小数点以下の桁数（デフォルトは0、整数）
        result_column: 結果を格納する列名（デフォルトはNone、"round({column}, {decimals})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
    """
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得
    values = collection[column].values
    
    # 結果の列名を決定
    if result_column is None:
        result_column = f"round({column}, {decimals})"
    
    # 丸め処理
    result_values = [
        round(value, decimals) if value is not None else None
        for value in values
    ]
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result


@operation(domain="core")
def normalize(
    collection: ColumnCollection,
    column: str,
    result_column: Optional[str] = None,
    in_place: bool = False,
    method: str = "minmax"
) -> ColumnCollection:
    """指定した列の値を正規化

    Args:
        collection: ColumnCollectionオブジェクト
        column: 処理対象の列名
        result_column: 結果を格納する列名（デフォルトはNone、"norm_{method}({column})"が使用される）
        in_place: Trueの場合は元のオブジェクトを変更、Falseの場合は新しいオブジェクトを作成
        method: 正規化方法
            "minmax": [0, 1]の範囲に正規化
            "zscore": 平均0、標準偏差1に正規化

    Returns:
        ColumnCollection: 結果の列を含むColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        ValueError: 不正なmethod値が指定された場合、または値が一定で正規化できない場合
    """
    # methodの検証
    valid_methods = ["minmax", "zscore"]
    if method not in valid_methods:
        raise ValueError(f"methodは{valid_methods}のいずれかを指定してください")
    
    # 列の存在チェック
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    
    # 結果を格納するオブジェクトを準備
    result = collection if in_place else collection.clone()
    
    # 列の値を取得（Noneを除く）
    values = [v for v in collection[column].values if v is not None]
    
    # 空の列またはすべてNoneの場合
    if not values:
        if result_column is None:
            result_column = f"norm_{method}({column})"
        
        # すべてNoneの結果を返す
        null_values = [None] * len(collection[column].values)
        if result_column in result.columns:
            result.columns[result_column].values = null_values
        else:
            # 元の列から単位などの情報を継承
            source_column = collection[column]
            column_type = detect_column_type(
                getattr(source_column, 'ch', None),
                result_column,
                getattr(source_column, 'unit', None),
                null_values
            )
            result.add_column(result_column, column_type)
        return result
    
    # 正規化処理
    if method == "minmax":
        min_val = min(values)
        max_val = max(values)
        
        # 最大値と最小値が等しい場合（定数値）
        if max_val == min_val:
            # すべて0.5に設定
            result_values = [0.5 if v is not None else None for v in collection[column].values]
        else:
            # Min-Max正規化
            result_values = [
                (v - min_val) / (max_val - min_val) if v is not None else None
                for v in collection[column].values
            ]
        
        # 結果列名
        if result_column is None:
            result_column = f"norm_minmax({column})"
    
    elif method == "zscore":
        # 平均と標準偏差を計算
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # 分散がほぼ0の場合（ほとんど定数）
        if variance < 1e-10:
            result_values = [0.0 if v is not None else None for v in collection[column].values]
        else:
            std_dev = math.sqrt(variance)
            # Z-score正規化
            result_values = [
                (v - mean) / std_dev if v is not None else None
                for v in collection[column].values
            ]
        
        # 結果列名
        if result_column is None:
            result_column = f"norm_zscore({column})"
    
    # 結果を新しい列として追加（既存の列名の場合は上書き）
    if result_column in result.columns:
        result.columns[result_column].values = result_values
    else:
        # 新しい列を追加
        # 元の列から単位などの情報を継承
        source_column = collection[column]
        column_type = detect_column_type(
            getattr(source_column, 'ch', None),
            result_column,
            getattr(source_column, 'unit', None),
            result_values
        )
        result.add_column(result_column, column_type)
    
    return result