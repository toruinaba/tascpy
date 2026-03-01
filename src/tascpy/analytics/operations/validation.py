from functools import wraps
from typing import Callable, Any, List, Union, Optional
from tascpy.core.collection import ColumnCollection

def requires_column(column_name: str):
    """指定された列が存在することを検証するデコレーター
    
    Args:
        column_name: 必須の列名
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            if column_name not in collection.columns:
                raise ValueError(f"必須列 '{column_name}' がコレクションに存在しません")
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator

def requires_columns(column_names: List[str]):
    """複数の指定された列が存在することを検証するデコレーター
    
    Args:
        column_names: 必須の列名のリスト
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            missing_columns = [col for col in column_names if col not in collection.columns]
            if missing_columns:
                raise ValueError(f"以下の必須列がコレクションに存在しません: {', '.join(missing_columns)}")
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator

def requires_metadata(key: str):
    """指定されたメタデータキーが存在することを検証するデコレーター
    
    Args:
        key: 必須のメタデータキー
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            if key not in collection.metadata:
                raise ValueError(f"メタデータに必須キー '{key}' が存在しません")
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator

def requires_domain(domain: Union[str, List[str]]):
    """コレクションが指定されたドメインであることを検証するデコレーター
    
    Args:
        domain: 必須のドメイン名（単一文字列または文字列のリスト）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            # コレクションのドメインを確認
            # collection.domain プロパティを使用するが、存在しない場合はmetadataを確認
            current_domain = getattr(collection, "domain", None)
            if not current_domain:
                current_domain = collection.metadata.get("domain")
            
            allowed_domains = [domain] if isinstance(domain, str) else domain
            
            if current_domain not in allowed_domains:
                raise ValueError(f"この操作はドメイン {allowed_domains} 専用です (現在のドメイン: {current_domain})")
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator

def requires_coordinates(columns: Optional[List[str]] = None):
    """座標情報が存在することを検証するデコレーター
    
    Args:
        columns: 座標を確認する列名のリスト（オプション）
                 指定がない場合、コレクション全体で少なくとも1つの座標が存在するか確認します。
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            # CoordinateCollectionのようなメソッドを持つか確認
            if not hasattr(collection, "get_columns_with_coordinates"):
                 raise ValueError("このコレクションは座標操作をサポートしていません")
            
            if columns:
                # 特定の列の座標を確認
                for col in columns:
                    if col not in collection.columns:
                        raise ValueError(f"列 '{col}' が見つかりません")
                    
                    coords = collection.get_column_coordinates(col)
                    # (x, y, z) のいずれかが設定されているか
                    if not any(c is not None for c in coords):
                        raise ValueError(f"列 '{col}' には座標情報がありません")
            else:
                # 少なくとも1つの列に座標があるか確認
                coords_cols = collection.get_columns_with_coordinates()
                if not coords_cols:
                    raise ValueError("有効な座標データがありません")
                    
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator
