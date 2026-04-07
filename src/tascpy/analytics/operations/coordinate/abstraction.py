import functools
from typing import Callable, Any, Optional, Tuple, List
import numpy as np

from tascpy.domains.coordinate import CoordinateCollection
from tascpy.core.column import Column


def inject_coordinate_matrix(include_z: bool = True):
    """
    CoordinateCollectionから座標行列 X と有効な列名リスト valid_columns を抽出し、
    関数の最初の引数として注入するデコレータ。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, *args, **kwargs):
            # pop 'columns' so it doesn't get passed to pure function
            columns = kwargs.pop("columns", None)
            
            # get_coordinate_matrixを使用してNxDのnumpy配列と有効なカラムリストを取得
            X, valid_columns = collection.get_coordinate_matrix(columns=columns, include_z=include_z)
            
            # 元の関数(純粋関数)には X を渡し、後続のデコレータが結果を処理できるよう、
            # (結果, X, valid_columns, collection) をタプルで返す
            result = func(X, *args, **kwargs)
            return result, X, valid_columns, collection
        return wrapper
    return decorator


def store_clustering_result(algorithm_key: str = "algorithm"):
    """
    クラスタリングアルゴリズムの実行結果 (labels) を CoordinateCollection に追加するデコレータ。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # アルゴリズム名は kwargs から取得するか、デフォルト値（"kmeans"など）
            algorithm = kwargs.pop(algorithm_key, "kmeans")
            
            # kwarg "n_clusters" があれば取得。なければラベルのユニーク数とする
            n_clusters = kwargs.get("n_clusters", None)
            
            # 結果を格納するカラム名
            result_column = kwargs.pop("result_column", "cluster")

            # 前段のデコレータから4要素タプルが返されることを想定
            labels, X, valid_columns, collection = func(*args, **kwargs)
            
            if n_clusters is None:
                n_clusters = len(np.unique(labels))

            
            result = collection.clone()
            
            if "analysis" not in result.metadata:
                result.metadata["analysis"] = {}

            cluster_info = {}
            for i, col in enumerate(valid_columns):
                cluster_id = int(labels[i])
                if cluster_id not in cluster_info:
                    cluster_info[cluster_id] = []
                cluster_info[cluster_id].append(col)

            result.metadata["analysis"]["clustering"] = {
                "algorithm": algorithm,
                "n_clusters": n_clusters,
                "clusters": cluster_info,
            }

            for i, col in enumerate(valid_columns):
                cluster_id = int(labels[i])
                if not hasattr(result.columns[col], "metadata"):
                    result.columns[col].metadata = {}
                if "analysis" not in result.columns[col].metadata:
                    result.columns[col].metadata["analysis"] = {}
                result.columns[col].metadata["analysis"]["cluster"] = cluster_id

            cluster_map = {col: int(labels[i]) for i, col in enumerate(valid_columns)}
            result.columns[result_column] = Column(
                ch=None,
                name=result_column,
                unit=None,
                values=[str(cluster_map)] * len(collection.step),
                metadata={
                    "description": f"Clustering results using {algorithm}",
                    "type": "clustering",
                    "clusters": cluster_info,
                },
            )

            return result
        return wrapper
    return decorator


def resolve_nearest_neighbors():
    """
    近傍探索用のパラメータセットアップと距離リスト作成を行い、
    結果をフォーマットして返すデコレータ。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, column: str, *args, **kwargs):
            if column not in collection.columns:
                raise ValueError(f"列 '{column}' が見つかりません")
                
            columns_with_coords = collection.get_columns_with_coordinates()
            if column not in columns_with_coords:
                raise ValueError(f"列 '{column}' には座標情報がありません")
                
            if len(columns_with_coords) <= 1:
                raise ValueError("近傍検索には少なくとも2つの座標情報が必要です")
                
            other_columns = [c for c in columns_with_coords if c != column]
            
            distances = []
            for other_col in other_columns:
                try:
                    dist = collection.calculate_distance(column, other_col)
                    distances.append((other_col, dist))
                except ValueError:
                    continue
                    
            n_neighbors = kwargs.get("n_neighbors", 3)
            result_column = kwargs.pop("result_column", None)
            
            # 純粋関数の実行 (find_nearest_neighbors_logic)
            nearest = func(distances, n_neighbors)
            
            result = collection.clone()
            
            if "analysis" not in result.metadata:
                result.metadata["analysis"] = {}

            neighbors = [
                {"column": col, "distance": dist} for col, dist in nearest
            ]

            result.metadata["analysis"]["nearest_neighbors"] = {
                "reference_column": column,
                "neighbors": neighbors,
            }

            if result_column is None:
                result_column = f"neighbors_of_{column}"

            neighbor_str = ", ".join(
                [f"{n['column']}({n['distance']:.4f}m)" for n in neighbors]
            )
            result.columns[result_column] = Column(
                ch=None,
                name=result_column,
                unit=None,
                values=[neighbor_str] * len(collection.step),
                metadata={
                    "description": f"Nearest neighbors of {column}",
                    "type": "nearest_neighbors",
                    "reference_column": column,
                    "neighbors": neighbors,
                },
            )

            return result
        return wrapper
    return decorator

def resolve_point_interpolation():
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, x: float, y: float, *args, **kwargs):
            z = kwargs.get("z", None)
            target_columns = kwargs.get("target_columns", None)
            method = kwargs.get("method", "inverse_distance")
            power = kwargs.get("power", 2.0)
            result_prefix = kwargs.pop("result_prefix", "interp_")
            
            if target_columns is None:
                target_columns = collection.get_columns_with_coordinates()
            if not target_columns:
                raise ValueError("補間に使用できる座標付き列がありません")
            
            is_3d = z is not None
            source_data = []
            valid_targets = []
            
            for col_name in target_columns:
                values = collection[col_name].values
                if len(values) == 0:
                    continue
                if isinstance(values[0], (int, float, np.number)):
                    value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
                else:
                    value = values[0]
                    
                col_x, col_y, col_z = collection.get_column_coordinates(col_name)
                if col_x is None or col_y is None:
                    continue
                if is_3d and col_z is None:
                    continue
                    
                point = {"x": col_x, "y": col_y, "z": col_z if is_3d else None}
                source_data.append({"point": point, "value": value, "col_name": col_name})
                valid_targets.append(col_name)
            
            # Call pure function
            interp_values = func(source_data, x, y, z, method, power)
            
            result = collection.clone()
            for i, col_name in enumerate(valid_targets):
                result_col_name = f"{result_prefix}{col_name}"
                interp_value = interp_values[i]
                
                result.columns[result_col_name] = Column(
                    ch=None,
                    name=result_col_name,
                    unit=collection[col_name].unit if hasattr(collection[col_name], "unit") else None,
                    values=[interp_value] * len(collection.step),
                    metadata={
                        "description": f"Interpolated value at ({x}, {y}{', ' + str(z) if is_3d else ''})",
                        "interpolation": {
                            "method": method,
                            "power": power if method == "inverse_distance" else None,
                            "target": {"x": x, "y": y, "z": z if is_3d else None},
                        },
                    },
                )
                
            return result
        return wrapper
    return decorator

def resolve_grid_interpolation():
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, x_range: Tuple[float, float], y_range: Tuple[float, float], *args, **kwargs):
            grid_size = kwargs.get("grid_size", (10, 10))
            target_column = kwargs.get("target_column", None)
            method = kwargs.get("method", "inverse_distance")
            power = kwargs.get("power", 2.0)
            result_prefix = kwargs.pop("result_prefix", "grid_")
            
            if target_column is None:
                coord_columns = collection.get_columns_with_coordinates()
                if not coord_columns:
                    raise ValueError("補間に使用できる座標付き列がありません")
                target_column = coord_columns[0]
            if target_column not in collection.columns:
                raise ValueError(f"列 '{target_column}' が見つかりません")
                
            values = collection[target_column].values
            if len(values) == 0:
                raise ValueError(f"列 '{target_column}' に値がありません")
            
            if isinstance(values[0], (int, float, np.number)):
                value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
            else:
                value = values[0]
                
            col_x, col_y, col_z = collection.get_column_coordinates(target_column)
            if col_x is None or col_y is None:
                raise ValueError(f"列 '{target_column}' に座標情報がありません")
                
            source_point = {
                "point": {"x": col_x, "y": col_y, "z": col_z},
                "value": value,
                "col_name": target_column,
            }
            
            nx, ny = grid_size
            x_grid = np.linspace(x_range[0], x_range[1], nx)
            y_grid = np.linspace(y_range[0], y_range[1], ny)
            
            # Call pure function
            grid_values = func(source_point, x_grid, y_grid, method, power)
            
            result = collection.clone()
            if "analysis" not in result.metadata:
                result.metadata["analysis"] = {}
                
            result.metadata["analysis"]["grid_interpolation"] = {
                "x_range": x_range,
                "y_range": y_range,
                "grid_size": grid_size,
                "method": method,
                "target_column": target_column,
            }
            
            grid_str = np.array2string(grid_values, precision=4, suppress_small=True)
            result_col_name = f"{result_prefix}{target_column}_grid"
            
            result.columns[result_col_name] = Column(
                ch=None,
                name=result_col_name,
                unit=None,
                values=[grid_str] * len(collection.step),
                metadata={
                    "description": f"Grid interpolation of {target_column}",
                    "grid": {
                        "x_min": float(x_range[0]),
                        "x_max": float(x_range[1]),
                        "y_min": float(y_range[0]),
                        "y_max": float(y_range[1]),
                        "nx": nx,
                        "ny": ny,
                    },
                },
            )
            return result
        return wrapper
    return decorator

def resolve_spatial_interpolation():
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, *args, **kwargs):
            source_columns = kwargs.get("source_columns", None)
            target_columns = kwargs.get("target_columns", None)
            method = kwargs.get("method", "inverse_distance")
            power = kwargs.get("power", 2.0)
            result_prefix = kwargs.pop("result_prefix", "interp_")
            
            columns_with_coords = collection.get_columns_with_coordinates()
            if source_columns is None:
                source_columns = columns_with_coords
            if target_columns is None:
                target_columns = [c for c in columns_with_coords if c not in source_columns]
                
            if not source_columns: raise ValueError("補間元の座標付き列がありません")
            if not target_columns: raise ValueError("補間先の座標付き列がありません")
            
            source_data = []
            for col_name in source_columns:
                values = collection[col_name].values
                if len(values) == 0: continue
                if isinstance(values[0], (int, float, np.number)):
                    value = np.nanmean([v for v in values if v is not None and not np.isnan(v)])
                else:
                    value = values[0]
                col_x, col_y, col_z = collection.get_column_coordinates(col_name)
                if col_x is None or col_y is None: continue
                source_data.append({"point": {"x": col_x, "y": col_y, "z": col_z}, "value": value, "col_name": col_name})
                
            target_coords = []
            valid_targets = []
            is_3d_overall = all(d["point"]["z"] is not None for d in source_data) if source_data else False
            
            for target_col in target_columns:
                target_x, target_y, target_z = collection.get_column_coordinates(target_col)
                if target_x is None or target_y is None: continue
                is_3d_tgt = target_z is not None and is_3d_overall
                target_coords.append({"x": target_x, "y": target_y, "z": target_z if is_3d_tgt else None})
                valid_targets.append((target_col, is_3d_tgt))
                
            # Call pure function
            results = func(source_data, target_coords, is_3d_overall, method, power)
            
            result = collection.clone()
            for i, (target_col, is_3d_tgt) in enumerate(valid_targets):
                avg_interp = results[i]
                result_col_name = f"{result_prefix}{target_col}"
                result.columns[result_col_name] = Column(
                    ch=None,
                    name=result_col_name,
                    unit=None,
                    values=[avg_interp] * len(collection.step),
                    metadata={
                        "description": f"Interpolated value at {target_col} position",
                        "interpolation": {
                            "method": method,
                            "power": power if method == "inverse_distance" else None,
                            "source_columns": source_columns,
                            "target_column": target_col,
                        },
                    },
                )
            
            return result
        return wrapper
    return decorator

def resolve_extract_coordinates():
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, *args, **kwargs):
            result_prefix = kwargs.pop("result_prefix", "coord_")
            
            result = collection.clone()
            coordinate_columns = collection.get_columns_with_coordinates()
            
            for column_name in coordinate_columns:
                x, y, z = collection.get_column_coordinates(column_name)
                length = len(collection.step)
                
                # 純粋関数を呼び出して各成分の配列を取得
                extracted = func(x, y, z, length)
                
                # 結果をカラムとして展開
                for comp in ["x", "y", "z"]:
                    if comp in extracted:
                        new_col_name = f"{result_prefix}{column_name}_{comp}"
                        result.columns[new_col_name] = Column(
                            ch=None,
                            name=new_col_name,
                            unit="m",  # 単位はメートルと仮定
                            values=extracted[comp],
                            metadata={
                                "description": f"{comp.upper()} coordinate of {column_name}",
                                "type": "coordinate",
                                "component": comp,
                            },
                        )
            return result
        return wrapper
    return decorator

def resolve_distance():
    """
    指定された2つの列の座標情報を取得し、距離計算純粋関数に渡すデコレータ。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: CoordinateCollection, column1: str, column2: str, *args, **kwargs):
            if column1 not in collection.columns:
                raise ValueError(f"列 '{column1}' が見つかりません")
            if column2 not in collection.columns:
                raise ValueError(f"列 '{column2}' が見つかりません")
                
            x1, y1, z1 = collection.get_column_coordinates(column1)
            x2, y2, z2 = collection.get_column_coordinates(column2)
            
            if x1 is None or y1 is None:
                raise ValueError(f"列 '{column1}' に座標情報がありません")
            if x2 is None or y2 is None:
                raise ValueError(f"列 '{column2}' に座標情報がありません")
                
            return func(x1, y1, z1, x2, y2, z2, *args, **kwargs)
        return wrapper
    return decorator
