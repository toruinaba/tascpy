
@operation(domain="core")
def max(collection: ColumnCollection, column: str) -> float:
    """列の最大値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 最大値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    # None/NaN処理
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanmax(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.max(valid_values))

@operation(domain="core")
def min(collection: ColumnCollection, column: str) -> float:
    """列の最小値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 最小値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanmin(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.min(valid_values))

@operation(domain="core")
def mean(collection: ColumnCollection, column: str) -> float:
    """列の平均値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 平均値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanmean(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.mean(valid_values))

@operation(domain="core")
def std(collection: ColumnCollection, column: str) -> float:
    """列の標準偏差を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 標準偏差
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nanstd(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.std(valid_values))

@operation(domain="core")
def sum(collection: ColumnCollection, column: str) -> float:
    """列の合計値を取得します
    
    Args:
        collection: 対象のコレクション
        column: 列名
        
    Returns:
        float: 合計値
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")
    values = collection[column].values
    
    if hasattr(values, "dtype") and np.issubdtype(values.dtype, np.number):
        return float(np.nansum(values))
    
    valid_values = [v for v in values if v is not None and (not isinstance(v, float) or not np.isnan(v))]
    if not valid_values:
        return float("nan")
        
    return float(np.sum(valid_values))
