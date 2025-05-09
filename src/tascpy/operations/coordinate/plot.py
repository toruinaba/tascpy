"""座標ドメインの可視化関数

このモジュールには、座標情報を持つデータを可視化するための関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple, Union, Callable
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

# 日本語フォントサポート
try:
    import japanize_matplotlib
    import matplotlib as mpl
    # マイナス記号を正しく表示するための設定
    mpl.rcParams["axes.unicode_minus"] = False
except ImportError:
    print(
        "警告: japanize_matplotlib をインポートできません。日本語が正しく表示されない可能性があります。"
    )

from ...operations.registry import operation
from ...domains.coordinate import CoordinateCollection
from ...core.collection import ColumnCollection


@operation(domain="coordinate")
def plot_spatial_values(
    collection: CoordinateCollection,
    value_column: str,
    ax: Optional[plt.Axes] = None,
    plot_type: str = "scatter",
    color_map: Union[str, plt.cm.ScalarMappable] = "viridis",
    size_column: Optional[str] = None,
    size_scale: float = 50.0,
    show_colorbar: bool = True,
    step_index: Optional[int] = None,
    **kwargs
) -> CoordinateCollection:
    """座標空間上に値の分布をプロットする

    Args:
        collection: 座標コレクション
        value_column: 値を表示する列名
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        plot_type: プロットの種類 ('scatter', 'line', 'text', 'contour', 'surface')
        color_map: カラーマップ名またはカラーマップオブジェクト
        size_column: マーカーサイズを決定する列名（Noneの場合は一定サイズ）
        size_scale: マーカーサイズのスケールファクター
        show_colorbar: カラーバーを表示するかどうか
        step_index: 使用するステップのインデックス（Noneの場合は最初のステップを使用）
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # プロットタイプの検証
    valid_plot_types = ["scatter", "line", "text", "contour", "surface"]
    if plot_type not in valid_plot_types:
        raise ValueError(f"無効なプロットタイプ: {plot_type}。有効な値は {valid_plot_types} です")

    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")

    # 値列の存在チェック
    if value_column not in collection.columns:
        raise ValueError(f"列 '{value_column}' は存在しません")

    # 使用するステップのインデックスを決定
    if step_index is None:
        step_index = 0  # デフォルトは最初のステップ
    elif step_index < 0 or (len(collection.step) > 0 and step_index >= len(collection.step)):
        raise ValueError(f"無効なstep_index: {step_index}。0から{len(collection.step)-1}の範囲内である必要があります")

    # 値データを取得
    values = collection[value_column].values
    if step_index < len(values):
        step_value = values[step_index]
    else:
        step_value = values[-1] if values else None  # データが足りない場合は最後の値を使用

    # 座標データを収集
    points = []
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
        # 該当ステップの値を取得
        col_values = collection[col].values
        if step_index < len(col_values):
            col_value = col_values[step_index]
        else:
            col_value = col_values[-1] if col_values else None  # データが足りない場合は最後の値を使用
        points.append((col, x, y, z, col_value))
    
    if not points:
        raise ValueError("有効な座標情報を持つ列がありません")

    # サイズ情報の取得
    if size_column is not None:
        if size_column not in collection.columns:
            raise ValueError(f"サイズ列 '{size_column}' は存在しません")
        size_values = collection[size_column].values
        if step_index < len(size_values):
            sizes = [size_values[step_index] * size_scale]
        else:
            sizes = [size_values[-1] * size_scale if size_values else size_scale]  # データが足りない場合は最後の値を使用
    else:
        sizes = [size_scale] * len(points)

    # 3D描画が必要かどうか判断
    is_3d = all(p[3] is not None for p in points) and plot_type == "surface"

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        if is_3d:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
        else:
            fig, ax = plt.subplots()

    # カラーマップの設定
    if isinstance(color_map, str):
        color_map = plt.get_cmap(color_map)
    
    # 値の正規化
    point_values = [p[4] for p in points if p[4] is not None]
    if not point_values:
        raise ValueError("有効な値データがありません")
    norm = Normalize(vmin=min(point_values), vmax=max(point_values))

    # プロット
    if plot_type == "scatter":
        scatter = ax.scatter(
            [p[1] for p in points],  # x座標
            [p[2] for p in points],  # y座標
            c=[p[4] for p in points],  # 特定ステップのデータ値
            s=sizes,
            cmap=color_map,
            norm=norm,
            **kwargs
        )
        
        # カラーバー
        if show_colorbar:
            plt.colorbar(scatter, ax=ax, label=value_column)

    elif plot_type == "line":
        # x座標でソート
        points.sort(key=lambda p: p[1])
        line = ax.plot(
            [p[1] for p in points],  # x座標
            [p[2] for p in points],  # y座標
            **kwargs
        )

    elif plot_type == "text":
        for i, p in enumerate(points):
            ax.text(
                p[1], p[2],  # x, y座標
                f"{p[4]:.2f}" if p[4] is not None else "N/A",  # 表示テキスト
                fontsize=kwargs.get("fontsize", 8),
                ha="center", va="center"
            )

    elif plot_type == "contour" or plot_type == "surface":
        # コンター図やサーフェスプロットには格子状のデータが必要
        from scipy.interpolate import griddata
        
        # 格子を作成
        xi = np.linspace(min(p[1] for p in points), max(p[1] for p in points), 100)
        yi = np.linspace(min(p[2] for p in points), max(p[2] for p in points), 100)
        X, Y = np.meshgrid(xi, yi)
        
        # 値を補間
        Z = griddata(
            (np.array([p[1] for p in points]), np.array([p[2] for p in points])),
            np.array([p[4] for p in points]),  # 特定ステップのデータ値
            (X, Y),
            method="cubic",
            fill_value=np.nan
        )
        
        if plot_type == "contour":
            contour = ax.contourf(X, Y, Z, cmap=color_map, **kwargs)
            if show_colorbar:
                plt.colorbar(contour, ax=ax, label=value_column)
        else:  # surface
            if is_3d:
                # 3D surface plot
                surf = ax.plot_surface(X, Y, Z, cmap=color_map, **kwargs)
                if show_colorbar:
                    plt.colorbar(surf, ax=ax, label=value_column)
            else:
                # 2D surface as pcolormesh
                mesh = ax.pcolormesh(X, Y, Z, cmap=color_map, **kwargs)
                if show_colorbar:
                    plt.colorbar(mesh, ax=ax, label=value_column)

    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    if is_3d:
        ax.set_zlabel("Z座標 [m]")
    
    # タイトル設定
    step_info = f" (Step {step_index})" if step_index is not None else ""
    ax.set_title(f"{value_column}の空間分布 ({plot_type}){step_info}")
    
    return collection


@operation(domain="coordinate")
def plot_coordinates(
    collection: CoordinateCollection,
    ax: Optional[plt.Axes] = None,
    labels: bool = True,
    dimension: str = "2d",
    **kwargs
) -> CoordinateCollection:
    """座標情報を使って各列の位置をプロットする

    Args:
        collection: 座標コレクション
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        labels: 各点にラベルを表示するかどうか
        dimension: 描画次元 ('2d' または '3d')
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")

    # 3D描画が必要かどうか判断
    is_3d = dimension.lower() == "3d" and all(
        collection.get_column_coordinates(col)[2] is not None for col in coord_columns
    )

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        if is_3d:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
        else:
            fig, ax = plt.subplots()

    # 座標データをプロット
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
            
        if is_3d and z is not None:
            ax.scatter(x, y, z, **kwargs)
            if labels:
                ax.text(x, y, z, col, fontsize=9)
        else:
            ax.scatter(x, y, **kwargs)
            if labels:
                ax.text(x, y, col, fontsize=9)

    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    if is_3d:
        ax.set_zlabel("Z座標 [m]")
    
    # タイトル設定
    ax.set_title("座標位置プロット")
    
    return collection


@operation(domain="coordinate")
def plot_spatial_heatmap(
    collection: CoordinateCollection,
    value_column: str,
    resolution: Tuple[int, int] = (100, 100),
    interpolation_method: str = "cubic",
    ax: Optional[plt.Axes] = None,
    color_map: str = "viridis",
    show_colorbar: bool = True,
    show_points: bool = False,
    step_index: Optional[int] = None,
    **kwargs
) -> CoordinateCollection:
    """座標に基づいてヒートマップを作成

    Args:
        collection: 座標コレクション
        value_column: ヒートマップ値として使用する列名
        resolution: ヒートマップの解像度 (nx, ny)
        interpolation_method: 補間方法 ('linear', 'cubic', 'nearest')
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        color_map: カラーマップ名
        show_colorbar: カラーバーを表示するかどうか
        show_points: オリジナルのデータ点を表示するかどうか
        step_index: 使用するステップのインデックス（Noneの場合は最初のステップを使用）
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")

    # 値列の存在チェック
    if value_column not in collection.columns:
        raise ValueError(f"列 '{value_column}' は存在しません")

    # 使用するステップのインデックスを決定
    if step_index is None:
        step_index = 0  # デフォルトは最初のステップ
    elif step_index < 0 or (len(collection.step) > 0 and step_index >= len(collection.step)):
        raise ValueError(f"無効なstep_index: {step_index}。0から{len(collection.step)-1}の範囲内である必要があります")

    # データを収集
    points = []
    values = []
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
        points.append((x, y))
        
        # 特定のステップの値を使用
        col_values = collection[col].values
        if step_index < len(col_values):
            values.append(col_values[step_index])
        else:
            values.append(col_values[-1] if col_values else None)  # データが足りない場合は最後の値を使用

    if not points:
        raise ValueError("有効な座標情報を持つ列がありません")
    if None in values:
        raise ValueError("一部の列に有効な値がありません")

    # ヒートマップの解像度
    nx, ny = resolution
    
    # 補間に必要なgriddata
    try:
        from scipy.interpolate import griddata
    except ImportError:
        raise ImportError("このプロットにはSciPyが必要です。pip install scipyで導入してください。")

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots()

    # グリッドを作成
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    z = np.array(values)
    
    xi = np.linspace(np.min(x), np.max(x), nx)
    yi = np.linspace(np.min(y), np.max(y), ny)
    X, Y = np.meshgrid(xi, yi)
    
    # 値を補間
    Z = griddata((x, y), z, (X, Y), method=interpolation_method)
    
    # ヒートマップをプロット
    heatmap = ax.pcolormesh(X, Y, Z, cmap=color_map, **kwargs)
    
    # オリジナルのデータ点を表示
    if show_points:
        ax.scatter(x, y, c='black', s=10, alpha=0.5)
    
    # カラーバー
    if show_colorbar:
        plt.colorbar(heatmap, ax=ax, label=value_column)
    
    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    
    # タイトル設定
    step_info = f" (Step {step_index})" if step_index is not None else ""
    ax.set_title(f"{value_column}の空間ヒートマップ{step_info}")
    
    return collection


@operation(domain="coordinate")
def plot_coordinate_distance(
    collection: CoordinateCollection,
    reference_column: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    plot_type: str = "matrix",
    color_map: str = "viridis",
    **kwargs
) -> CoordinateCollection:
    """座標間の距離関係を可視化

    Args:
        collection: 座標コレクション
        reference_column: 基準となる列名（Noneの場合はすべての列の組み合わせ）
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        plot_type: プロット種類 ('matrix', 'network', 'histogram')
        color_map: カラーマップ名
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")
    
    # 距離行列を計算
    distances = {}
    for i, col1 in enumerate(coord_columns):
        x1, y1, z1 = collection.get_column_coordinates(col1)
        if x1 is None or y1 is None:
            continue
            
        for j, col2 in enumerate(coord_columns[i:], start=i):
            if col1 == col2:
                distances[(col1, col2)] = 0.0
                continue
                
            try:
                dist = collection.calculate_distance(col1, col2)
                distances[(col1, col2)] = dist
                distances[(col2, col1)] = dist
            except ValueError:
                # 距離計算できない場合はスキップ
                continue
    
    if not distances:
        raise ValueError("有効な距離を計算できませんでした")
    
    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots()
    
    # プロットタイプに基づいて描画
    if plot_type == "matrix":
        # 距離行列のプロット
        cols = sorted(list({col for pair in distances.keys() for col in pair}))
        n = len(cols)
        matrix = np.zeros((n, n))
        
        # 行列を埋める
        for i, col1 in enumerate(cols):
            for j, col2 in enumerate(cols):
                if (col1, col2) in distances:
                    matrix[i, j] = distances[(col1, col2)]
        
        # ヒートマップとして表示
        im = ax.imshow(matrix, cmap=color_map, **kwargs)
        plt.colorbar(im, ax=ax, label="距離 [m]")
        
        # ラベル設定
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(cols, rotation=90)
        ax.set_yticklabels(cols)
        ax.set_title("座標間距離行列")
        
    elif plot_type == "network":
        # ネットワークプロット
        import networkx as nx
        
        G = nx.Graph()
        
        # ノードの追加
        node_positions = {}
        for col in coord_columns:
            x, y, z = collection.get_column_coordinates(col)
            if x is None or y is None:
                continue
            G.add_node(col)
            node_positions[col] = (x, y)
        
        # エッジの追加
        if reference_column:
            # 指定された列と他の列との距離
            for col in coord_columns:
                if col != reference_column and (reference_column, col) in distances:
                    G.add_edge(reference_column, col, weight=distances[(reference_column, col)])
        else:
            # すべての組み合わせ
            for (col1, col2), dist in distances.items():
                if col1 != col2:
                    G.add_edge(col1, col2, weight=dist)
        
        # ネットワークをプロット
        nx.draw(G, pos=node_positions, with_labels=True, node_color='lightblue', 
                edge_color='gray', ax=ax, **kwargs)
        
        # エッジラベル（距離）を表示
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=node_positions, edge_labels=edge_labels, ax=ax)
        
        ax.set_title("座標間距離ネットワーク")
        ax.set_xlim(min(pos[0] for pos in node_positions.values()) - 1, 
                   max(pos[0] for pos in node_positions.values()) + 1)
        ax.set_ylim(min(pos[1] for pos in node_positions.values()) - 1, 
                   max(pos[1] for pos in node_positions.values()) + 1)
        
    elif plot_type == "histogram":
        # 距離のヒストグラム
        # 自分自身との距離（0）を除く
        dist_values = [d for (c1, c2), d in distances.items() if c1 != c2]
        
        ax.hist(dist_values, bins=20, **kwargs)
        ax.set_xlabel("距離 [m]")
        ax.set_ylabel("頻度")
        ax.set_title("座標間距離の分布")
    
    return collection


@operation(domain="coordinate")
def plot_coordinate_timeseries(
    collection: CoordinateCollection,
    value_column: str,
    time_column: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    color_map: str = "viridis",
    animate: bool = False,
    **kwargs
) -> CoordinateCollection:
    """時系列データと座標情報を組み合わせて可視化

    Args:
        collection: 座標コレクション
        value_column: 値として使用する列名
        time_column: 時系列軸として使用する列名（Noneの場合はステップ）
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        color_map: カラーマップ名
        animate: アニメーションを生成するかどうか
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")

    # 値列の存在チェック
    if value_column not in collection.columns:
        raise ValueError(f"列 '{value_column}' は存在しません")
        
    # 時系列データを取得
    if time_column is None:
        time_values = collection.step.values
        time_label = "Step"
    else:
        if time_column not in collection.columns:
            raise ValueError(f"時系列列 '{time_column}' は存在しません")
        time_values = collection[time_column].values
        time_label = time_column
    
    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots()
    
    if animate:
        # アニメーション作成
        import matplotlib.animation as animation
        
        # 座標データを収集
        points = []
        for col in coord_columns:
            x, y, z = collection.get_column_coordinates(col)
            if x is None or y is None:
                continue
            values = collection[col].values
            points.append((col, x, y, values))
        
        if not points:
            raise ValueError("有効な座標情報を持つ列がありません")
        
        # アニメーション用の初期プロット
        scatter = ax.scatter(
            [p[1] for p in points],
            [p[2] for p in points],
            c=[p[3][0] for p in points],
            cmap=plt.get_cmap(color_map),
            **kwargs
        )
        
        # カラーバー
        plt.colorbar(scatter, ax=ax, label=value_column)
        
        # フレーム数
        n_frames = len(time_values)
        
        # アニメーション更新関数
        def update(frame):
            # 現在のフレームの値を設定
            scatter.set_array([p[3][frame] if frame < len(p[3]) else p[3][-1] for p in points])
            ax.set_title(f"{value_column}の時系列プロット - {time_label}: {time_values[frame]}")
            return scatter,
        
        # アニメーション作成
        ani = animation.FuncAnimation(
            fig, update, frames=n_frames, interval=200, blit=True
        )
        
        # ラベル設定
        ax.set_xlabel("X座標 [m]")
        ax.set_ylabel("Y座標 [m]")
        ax.set_title(f"{value_column}の時系列プロット")
        
    else:
        # 通常のプロット（時系列全体を線で表示）
        for col in coord_columns:
            x, y, z = collection.get_column_coordinates(col)
            if x is None or y is None:
                continue
                
            values = collection[col].values
            
            # 時間 vs 値のプロット
            ax.plot(time_values[:len(values)], values, label=col, **kwargs)
        
        # ラベル設定
        ax.set_xlabel(time_label)
        ax.set_ylabel(value_column)
        ax.set_title(f"{value_column}の時系列プロット")
        ax.legend()
        
    return collection


@operation(domain="coordinate")
def plot_spatial_contour(
    collection: CoordinateCollection,
    value_column: str,
    levels: int = 10,
    resolution: Tuple[int, int] = (100, 100),
    interpolation_method: str = "cubic",
    ax: Optional[plt.Axes] = None,
    color_map: str = "viridis",
    show_colorbar: bool = True,
    filled: bool = True,
    step_index: Optional[int] = None,
    **kwargs
) -> CoordinateCollection:
    """座標データに基づく等高線プロット

    Args:
        collection: 座標コレクション
        value_column: 等高線の値として使用する列名
        levels: 等高線のレベル数
        resolution: 補間グリッドの解像度 (nx, ny)
        interpolation_method: 補間方法 ('linear', 'cubic', 'nearest')
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        color_map: カラーマップ名
        show_colorbar: カラーバーを表示するかどうか
        filled: 等高線を塗りつぶすかどうか
        step_index: 使用するステップのインデックス（Noneの場合は最初のステップを使用）
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")
    
    # 値列の存在チェック
    if value_column not in collection.columns:
        raise ValueError(f"列 '{value_column}' は存在しません")
    
    # 使用するステップのインデックスを決定
    if step_index is None:
        step_index = 0  # デフォルトは最初のステップ
    elif step_index < 0 or (len(collection.step) > 0 and step_index >= len(collection.step)):
        raise ValueError(f"無効なstep_index: {step_index}。0から{len(collection.step)-1}の範囲内である必要があります")
    
    # データを収集
    points = []
    values = []
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
        points.append((x, y))
        
        # 特定のステップの値を使用
        col_values = collection[col].values
        if step_index < len(col_values):
            values.append(col_values[step_index])
        else:
            values.append(col_values[-1] if col_values else None)  # データが足りない場合は最後の値を使用

    if not points:
        raise ValueError("有効な座標情報を持つ列がありません")
    if None in values:
        raise ValueError("一部の列に有効な値がありません")
    
    # 補間に必要なgriddata
    try:
        from scipy.interpolate import griddata
    except ImportError:
        raise ImportError("このプロットにはSciPyが必要です。pip install scipyで導入してください。")
    
    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots()
    
    # グリッドを作成
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    z = np.array(values)
    
    nx, ny = resolution
    xi = np.linspace(np.min(x), np.max(x), nx)
    yi = np.linspace(np.min(y), np.max(y), ny)
    X, Y = np.meshgrid(xi, yi)
    
    # 値を補間
    Z = griddata((x, y), z, (X, Y), method=interpolation_method)
    
    # 等高線プロット
    if filled:
        contour = ax.contourf(X, Y, Z, levels=levels, cmap=color_map, **kwargs)
    else:
        contour = ax.contour(X, Y, Z, levels=levels, cmap=color_map, **kwargs)
        ax.clabel(contour, inline=True, fontsize=8)
    
    # 散布点をプロット
    ax.scatter(x, y, c='black', s=10, alpha=0.5)
    
    # カラーバー
    if show_colorbar:
        plt.colorbar(contour, ax=ax, label=value_column)
    
    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    
    # タイトル設定
    step_info = f" (Step {step_index})" if step_index is not None else ""
    ax.set_title(f"{value_column}の等高線プロット{step_info}")
    
    return collection


@operation(domain="coordinate")
def plot_3d_surface(
    collection: CoordinateCollection,
    value_column: str,
    resolution: Tuple[int, int] = (100, 100),
    interpolation_method: str = "cubic",
    ax: Optional[plt.Axes] = None,
    color_map: str = "viridis",
    show_colorbar: bool = True,
    step_index: Optional[int] = None,
    **kwargs
) -> CoordinateCollection:
    """3D表面プロットを生成

    Args:
        collection: 座標コレクション
        value_column: 表面の高さ値として使用する列名
        resolution: 補間グリッドの解像度 (nx, ny)
        interpolation_method: 補間方法 ('linear', 'cubic', 'nearest')
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        color_map: カラーマップ名
        show_colorbar: カラーバーを表示するかどうか
        step_index: 使用するステップのインデックス（Noneの場合は最初のステップを使用）
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")
    
    # 値列の存在チェック
    if value_column not in collection.columns:
        raise ValueError(f"列 '{value_column}' は存在しません")
    
    # 使用するステップのインデックスを決定
    if step_index is None:
        step_index = 0  # デフォルトは最初のステップ
    elif step_index < 0 or (len(collection.step) > 0 and step_index >= len(collection.step)):
        raise ValueError(f"無効なstep_index: {step_index}。0から{len(collection.step)-1}の範囲内である必要があります")
    
    # データを収集
    points = []
    values = []
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
        points.append((x, y))
        
        # 特定のステップの値を使用
        col_values = collection[col].values
        if step_index < len(col_values):
            values.append(col_values[step_index])
        else:
            values.append(col_values[-1] if col_values else None)  # データが足りない場合は最後の値を使用

    if not points:
        raise ValueError("有効な座標情報を持つ列がありません")
    if None in values:
        raise ValueError("一部の列に有効な値がありません")
    
    # 補間に必要なgriddata
    try:
        from scipy.interpolate import griddata
    except ImportError:
        raise ImportError("このプロットにはSciPyが必要です。pip install scipyで導入してください。")
    
    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
    
    # グリッドを作成
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    z = np.array(values)
    
    nx, ny = resolution
    xi = np.linspace(np.min(x), np.max(x), nx)
    yi = np.linspace(np.min(y), np.max(y), ny)
    X, Y = np.meshgrid(xi, yi)
    
    # 値を補間
    Z = griddata((x, y), z, (X, Y), method=interpolation_method)
    
    # 3D表面プロット
    surf = ax.plot_surface(X, Y, Z, cmap=color_map, **kwargs)
    
    # 散布点をプロット
    ax.scatter(x, y, z, c='red', s=30, alpha=0.5)
    
    # カラーバー
    if show_colorbar:
        plt.colorbar(surf, ax=ax, label=value_column)
    
    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    ax.set_zlabel(f"{value_column}")
    
    # タイトル設定
    step_info = f" (Step {step_index})" if step_index is not None else ""
    ax.set_title(f"{value_column}の3D表面プロット{step_info}")
    
    return collection


@operation(domain="coordinate")
def plot_vector_field(
    collection: CoordinateCollection,
    u_column: str,
    v_column: str,
    w_column: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    scale: float = 1.0,
    color_map: str = "viridis",
    **kwargs
) -> CoordinateCollection:
    """ベクトル場を可視化

    Args:
        collection: 座標コレクション
        u_column: X方向のベクトル成分列名
        v_column: Y方向のベクトル成分列名
        w_column: Z方向のベクトル成分列名（3Dプロットの場合）
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        scale: ベクトルのスケールファクター
        color_map: カラーマップ名
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")
    
    # 値列の存在チェック
    if u_column not in collection.columns:
        raise ValueError(f"列 '{u_column}' は存在しません")
    if v_column not in collection.columns:
        raise ValueError(f"列 '{v_column}' は存在しません")
    
    # 3Dプロットかどうかを判定
    is_3d = w_column is not None
    if is_3d and w_column not in collection.columns:
        raise ValueError(f"列 '{w_column}' は存在しません")
    
    # データを収集
    points = []
    u_values = []
    v_values = []
    w_values = [] if is_3d else None
    
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
            
        if col in collection.columns:
            points.append((x, y, z if is_3d and z is not None else None))
            u_values.append(collection[u_column].values[0])  # 最初の値を使用
            v_values.append(collection[v_column].values[0])  # 最初の値を使用
            if is_3d:
                w_values.append(collection[w_column].values[0])  # 最初の値を使用
    
    if not points:
        raise ValueError("有効な座標情報を持つ列がありません")
    
    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        if is_3d:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
        else:
            fig, ax = plt.subplots()
    
    # ベクトル場プロット
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    u = np.array(u_values) * scale
    v = np.array(v_values) * scale
    
    if is_3d:
        z = np.array([p[2] for p in points if p[2] is not None])
        w = np.array(w_values) * scale
        
        # 3Dベクトル場
        ax.quiver(x, y, z, u, v, w, **kwargs)
    else:
        # 2Dベクトル場
        # ベクトルの大きさを計算
        magnitude = np.sqrt(u**2 + v**2)
        
        # カラーマップを使用してベクトルに色を付ける
        quiver = ax.quiver(x, y, u, v, magnitude, cmap=color_map, **kwargs)
        
        # カラーバー
        plt.colorbar(quiver, ax=ax, label="ベクトル大きさ")
    
    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    if is_3d:
        ax.set_zlabel("Z座標 [m]")
    ax.set_title("ベクトル場プロット")
    
    return collection


@operation(domain="coordinate")
def plot_spatial_cluster(
    collection: CoordinateCollection,
    n_clusters: int = 3,
    method: str = "kmeans",
    ax: Optional[plt.Axes] = None,
    dimension: str = "2d",
    **kwargs
) -> CoordinateCollection:
    """座標に基づくクラスタリング結果を可視化

    Args:
        collection: 座標コレクション
        n_clusters: クラスタ数
        method: クラスタリング手法 ('kmeans', 'hierarchical', 'dbscan')
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        dimension: 描画次元 ('2d' または '3d')
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 結果のコレクション
    """
    # 座標を持つ列のリストを取得
    coord_columns = collection.get_columns_with_coordinates()
    if not coord_columns:
        raise ValueError("座標情報を持つ列がありません")
    
    # 3D描画が必要かどうか判断
    is_3d = dimension.lower() == "3d" and all(
        collection.get_column_coordinates(col)[2] is not None for col in coord_columns
    )
    
    # データを収集
    points = []
    column_names = []
    
    for col in coord_columns:
        x, y, z = collection.get_column_coordinates(col)
        if x is None or y is None:
            continue
        
        if is_3d and z is not None:
            points.append([x, y, z])
        else:
            points.append([x, y])
        
        column_names.append(col)
    
    # クラスタリング
    if method == "kmeans":
        from sklearn.cluster import KMeans
        
        # KMeansクラスタリング
        kmeans = KMeans(n_clusters=n_clusters, **kwargs)
        labels = kmeans.fit_predict(points)
        
    elif method == "hierarchical":
        from sklearn.cluster import AgglomerativeClustering
        
        # 階層的クラスタリング
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters, **kwargs)
        labels = hierarchical.fit_predict(points)
        
    elif method == "dbscan":
        from sklearn.cluster import DBSCAN
        
        # DBSCANクラスタリング
        dbscan = DBSCAN(**kwargs)
        labels = dbscan.fit_predict(points)
        
        # ノイズポイントのラベルを-1に設定
        labels = [-1 if label == -1 else label for label in labels]
    else:
        raise ValueError(f"無効なクラスタリング手法: {method}。'kmeans', 'hierarchical', 'dbscan' のいずれかを指定してください")
    
    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        if is_3d:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
        else:
            fig, ax = plt.subplots()
    
    # クラスタリング結果をプロット
    if is_3d:
        # 3Dプロット
        scatter = ax.scatter(
            [p[0] for p in points],
            [p[1] for p in points],
            [p[2] for p in points],
            c=labels,
            cmap="viridis",
            **kwargs
        )
        ax.set_zlabel("Z座標 [m]")
    else:
        # 2Dプロット
        scatter = ax.scatter(
            [p[0] for p in points],
            [p[1] for p in points],
            c=labels,
            cmap="viridis",
            **kwargs
        )
    
    # カラーバー
    plt.colorbar(scatter, ax=ax, label="クラスタラベル")
    
    # ラベル設定
    ax.set_xlabel("X座標 [m]")
    ax.set_ylabel("Y座標 [m]")
    ax.set_title(f"{method}によるクラスタリング結果")
    
    return collection


@operation(domain="coordinate")
def plot_coordinate_axis(
    collection: CoordinateCollection,
    column_names: Union[str, List[str]],
    coordinate_axis: str = "x",  # "x", "y", "z" のいずれか
    axis_orientation: str = "coord_value",  # "coord_value" または "value_coord"
    series_name: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    plot_type: str = "line",  # "scatter", "line", "bar"
    color: Optional[str] = None,
    marker: Optional[str] = None,
    step_index: Optional[int] = None,
    show_legend: bool = True,
    **kwargs
) -> CoordinateCollection:
    """指定した座標軸に沿って列の値をプロットする

    Args:
        collection: 座標コレクション
        column_names: プロットする列名または列名のリスト
        coordinate_axis: 使用する座標軸 ("x", "y", "z")
        axis_orientation: 軸の向き、"coord_value"は座標を横軸・値を縦軸、"value_coord"はその逆
        series_name: 系列の表示名（Noneの場合はデフォルト名を使用）
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        plot_type: プロットの種類 ("scatter", "line", "bar")
        color: 系列の色（Noneの場合はデフォルト色を使用）
        marker: マーカーの種類（散布図や折れ線グラフで使用）
        step_index: 使用するステップのインデックス（Noneの場合は最初のステップを使用）
        show_legend: 凡例を表示するかどうか
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        CoordinateCollection: 元のコレクション
    """
    # 有効な座標軸のチェック
    valid_axes = ["x", "y", "z"]
    if coordinate_axis not in valid_axes:
        raise ValueError(f"無効な座標軸: {coordinate_axis}。有効な値は {valid_axes} です")
    
    # 軸の向きのチェック
    valid_orientations = ["coord_value", "value_coord"]
    if axis_orientation not in valid_orientations:
        raise ValueError(f"無効な軸の向き: {axis_orientation}。有効な値は {valid_orientations} です")
    
    # プロットタイプの検証
    valid_plot_types = ["scatter", "line", "bar"]
    if plot_type not in valid_plot_types:
        raise ValueError(f"無効なプロットタイプ: {plot_type}。有効な値は {valid_plot_types} です")

    # 文字列の場合はリストに変換
    if isinstance(column_names, str):
        column_names = [column_names]
    
    # 値列の存在チェック
    for col in column_names:
        if col not in collection.columns:
            raise ValueError(f"列 '{col}' は存在しません")

    # 使用するステップのインデックスを決定
    if step_index is None:
        step_index = 0  # デフォルトは最初のステップ
    elif step_index < 0 or (len(collection.step) > 0 and step_index >= len(collection.step)):
        raise ValueError(f"無効なstep_index: {step_index}。0から{len(collection.step)-1}の範囲内である必要があります")

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots()

    # データ収集
    coord_values = []  # 座標値
    data_values = []  # 対応するデータ値
    point_labels = []  # 各点のラベル

    # 各列から座標とデータ値を収集
    for col_name in column_names:
        # 座標値を取得
        x, y, z = collection.get_column_coordinates(col_name)
        
        # 指定された座標軸の値を選択
        coord_value = None
        if coordinate_axis == "x" and x is not None:
            coord_value = x
        elif coordinate_axis == "y" and y is not None:
            coord_value = y
        elif coordinate_axis == "z" and z is not None:
            coord_value = z
        
        if coord_value is None:
            continue
        
        # 該当ステップのデータ値を取得
        col_values = collection[col_name].values
        if step_index < len(col_values):
            data_value = col_values[step_index]
        else:
            data_value = col_values[-1] if col_values else None  # データが足りない場合は最後の値を使用
        
        if data_value is not None:
            coord_values.append(coord_value)
            data_values.append(data_value)
            point_labels.append(col_name)

    if not coord_values:
        raise ValueError("有効なデータがありません")

    # 系列名の設定
    if series_name is None:
        series_name = f"Step {step_index}"

    # 軸ラベルとデータを準備
    if axis_orientation == "coord_value":
        x_data = coord_values
        y_data = data_values
        x_label = f"{coordinate_axis.upper()}座標 [m]"
        y_label = "値"
    else:  # value_coord
        x_data = data_values
        y_data = coord_values
        x_label = "値"
        y_label = f"{coordinate_axis.upper()}座標 [m]"
    
    # プロット
    plot_kwargs = {}
    if color:
        plot_kwargs['color'] = color
    if marker:
        plot_kwargs['marker'] = marker
    plot_kwargs.update(kwargs)  # 追加の引数を統合
    
    if plot_type == "scatter":
        scatter = ax.scatter(x_data, y_data, label=series_name, **plot_kwargs)
        
    elif plot_type == "line":
        # 座標値に基づいてソート
        if axis_orientation == "coord_value":
            # X軸が座標値の場合
            sorted_indices = np.argsort(x_data)
            sorted_x = [x_data[i] for i in sorted_indices]
            sorted_y = [y_data[i] for i in sorted_indices]
            sorted_labels = [point_labels[i] for i in sorted_indices]
            
            ax.plot(sorted_x, sorted_y, label=series_name, **plot_kwargs)
            
            # データポイントにラベルを付ける場合はここでラベルを表示
            for i, (x, y, label) in enumerate(zip(sorted_x, sorted_y, sorted_labels)):
                if kwargs.get('show_point_labels', False):
                    ax.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points')
        else:
            # Y軸が座標値の場合
            sorted_indices = np.argsort(y_data)
            sorted_x = [x_data[i] for i in sorted_indices]
            sorted_y = [y_data[i] for i in sorted_indices]
            sorted_labels = [point_labels[i] for i in sorted_indices]
            
            ax.plot(sorted_x, sorted_y, label=series_name, **plot_kwargs)
            
            # データポイントにラベルを付ける場合はここでラベルを表示
            for i, (x, y, label) in enumerate(zip(sorted_x, sorted_y, sorted_labels)):
                if kwargs.get('show_point_labels', False):
                    ax.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points')
            
    elif plot_type == "bar":
        if axis_orientation == "coord_value":
            bars = ax.bar(x_data, y_data, label=series_name, **plot_kwargs)
            # データラベルを表示
            if kwargs.get('show_point_labels', False):
                for i, rect in enumerate(bars):
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width()/2., height,
                            point_labels[i], ha='center', va='bottom')
        else:
            bars = ax.barh(y_data, x_data, label=series_name, **plot_kwargs)
            # データラベルを表示
            if kwargs.get('show_point_labels', False):
                for i, rect in enumerate(bars):
                    width = rect.get_width()
                    ax.text(width, rect.get_y() + rect.get_height()/2.,
                            point_labels[i], ha='left', va='center')

    # ラベル設定
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # タイトル設定
    step_info = f" (Step {step_index})" if step_index is not None else ""
    ax.set_title(f"{coordinate_axis.upper()}座標と値の関係{step_info}")
    
    # 凡例表示（オプション）
    if show_legend:
        ax.legend()
    
    return collection
