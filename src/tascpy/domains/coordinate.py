from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING, Union
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.step import Step
from tascpy.core.column import Column
from tascpy.domains.factory import DomainCollectionFactory
from tascpy.analytics.functional.coordinate.clustering import find_nearest_neighbors_logic, simple_kmeans
from tascpy.analytics.functional.coordinate.distance import compute_euclidean_distance

if TYPE_CHECKING:
    from ..typing.coordinate import CoordinateCollectionOperations


class CoordinateCollection(ColumnCollection):
    """座標値をメタデータとして保持する特化コレクションクラス

    各カラムに対して座標値(x, y, z)を関連付け、
    座標ベースの計算を可能にします。
    
    Examples:
        >>> from tascpy.domains.coordinate import CoordinateCollection
        >>> from tascpy.core.column import NumberColumn
        >>> cols = {"CH1": NumberColumn("CH1", "Strain", "ue", [100.0])}
        >>> col = CoordinateCollection(columns=cols, coordinates={"CH1": {"x": 10.0, "y": 20.0}})
        >>> col.get_column_coordinates("CH1")
        (10.0, 20.0, None)
    """

    def __init__(
        self,
        step: Optional[Step] = None,
        columns: Optional[Dict[str, Column]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        coordinate_metadata_key: str = "coordinates",
        coordinates: Optional[Union[Dict[str, Dict[str, Optional[float]]], str]] = None,
        **kwargs: Any,
    ):
        """初期化

        Args:
            step: ステップデータ
            columns: カラムデータ
            metadata: メタデータ
            coordinate_metadata_key: 座標データが格納されるメタデータのキー
            coordinates: カラム名をキーとし、座標情報 {'x': float, 'y': float, 'z': float} を値とする辞書、
                        またはJSON/CSVファイルのパス
                例: {'column1': {'x': 1.0, 'y': 2.0, 'z': 3.0}, 'column2': {'x': 4.0, 'y': 5.0}}
        """
        super().__init__(step=step, columns=columns, metadata=metadata)

        # 座標メタデータのキーをメタデータに保存
        self.metadata.update(
            {"coordinate_domain": {"coordinate_metadata_key": coordinate_metadata_key}}
        )

        # 既存の列に座標情報がない場合は初期化する
        # super().__init__ で self.columns に Column オブジェクトとして格納されているはず
        if self.columns:
            for col_name, col in self.columns.items():
                if not hasattr(col, "metadata") or not col.metadata:
                    col.metadata = {}
                if coordinate_metadata_key not in col.metadata:
                    col.metadata[coordinate_metadata_key] = {
                        "x": None,
                        "y": None,
                        "z": None,
                    }

        # 座標情報のロード
        coords_dict = {}
        if coordinates:
            from pathlib import Path
            if isinstance(coordinates, (str, Path)):
                coords_dict = self._load_coordinates_from_file(coordinates)
            else:
                coords_dict = coordinates

        # 初期化時に座標情報を設定
        if coords_dict:
            for column_name, coords in coords_dict.items():
                if column_name in self.columns:
                    self.set_column_coordinates(
                        column_name,
                        x=coords.get("x"),
                        y=coords.get("y"),
                        z=coords.get("z"),
                    )

    def _load_coordinates_from_file(self, file_path: str) -> Dict[str, Dict[str, Optional[float]]]:
        """ファイルから座標情報をロードする helper method"""
        from pathlib import Path
        import json
        import csv
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"座標ファイルが見つかりません: {file_path}")
            
        suffix = path.suffix.lower()
        result = {}
        
        if suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                result = json.load(f)
                
        elif suffix == ".csv":
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # ヘッダーチェック（大文字小文字を区別しない）
                    # 期待するカラム: column, x, y, z
                    # 実際のキーを探す
                    row_lower = {k.lower(): v for k, v in row.items() if k}
                    
                    if "column" not in row_lower:
                        continue
                        
                    col_name = row.get("column") or row_lower.get("column")
                    # rowから元のケースで値を取得するのは難しいので、row_lowerを使う
                    # ただしcol_nameは元の値が欲しい（辞書の値として入っているはず）
                    # csv.DictReaderのrowは {Header: Value}
                    
                    # 再度実装: ヘッダーのマッピングを作成
                    if reader.fieldnames:
                        header_map = {h.lower(): h for h in reader.fieldnames}
                    else:
                        continue

                    col_key = header_map.get("column")
                    if not col_key: continue
                    
                    col_name = row[col_key]
                    
                    coords = {}
                    for axis in ["x", "y", "z"]:
                        axis_key = header_map.get(axis)
                        if axis_key and row[axis_key]:
                            try:
                                coords[axis] = float(row[axis_key])
                            except ValueError:
                                coords[axis] = None
                    
                    result[col_name] = coords
        
        else:
            raise ValueError(f"サポートされていないファイル形式です: {suffix}")
            
        return result

    @property
    def domain(self) -> str:
        """ドメイン識別子を返す"""
        return "coordinate"

    @property
    def ops(self) -> "CoordinateCollectionOperations":
        """操作プロキシクラスを返す"""
        from tascpy.analytics.operations.proxy import CollectionOperations

        if TYPE_CHECKING:
            from ..typing.coordinate import CoordinateCollectionOperations

            return CoordinateCollectionOperations(self, domain="coordinate")  # type: ignore
        else:
            return CollectionOperations(self, domain=self.domain)
    @property
    def plot(self):
        """可視化プロキシクラスを返す"""
        from ..visualization.coordinate.plotter import CoordinatePlotter
        return CoordinatePlotter(self)

    @property
    def coordinate_metadata_key(self) -> str:
        """座標データが格納されるメタデータのキーを返す

        Returns:
            str: メタデータキー
        """
        return self.metadata.get("coordinate_domain", {}).get(
            "coordinate_metadata_key", "coordinates"
        )

    def clone(self) -> "CoordinateCollection":
        """コレクションの複製を作成

        Returns:
            CoordinateCollection: 複製されたコレクション
        """
        coordinate_info = self.metadata.get("coordinate_domain", {})

        # 列のクローンを作成し、その過程で座標メタデータも適切にコピー
        cloned_columns = {}
        for name, column in self.columns.items():
            cloned_column = column.clone()

            # 座標メタデータが存在する場合、深いコピーを作成
            coord_key = self.coordinate_metadata_key
            if (
                hasattr(column, "metadata")
                and column.metadata
                and coord_key in column.metadata
            ):
                if coord_key not in cloned_column.metadata:
                    cloned_column.metadata[coord_key] = {}

                # 各座標を明示的にコピー
                coords = column.metadata[coord_key]
                cloned_column.metadata[coord_key] = {
                    "x": coords.get("x"),
                    "y": coords.get("y"),
                    "z": coords.get("z"),
                }

            cloned_columns[name] = cloned_column

        # 新しいコレクションを作成
        import copy

        return CoordinateCollection(
            step=self.step.clone() if self.step else None,
            columns=cloned_columns,
            metadata=copy.deepcopy(self.metadata),
            coordinate_metadata_key=coordinate_info.get(
                "coordinate_metadata_key", "coordinates"
            ),
        )

    def set_column_coordinates(
        self,
        column_name: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ) -> "CoordinateCollection":
        """指定したカラムに座標値を設定する

        Args:
            column_name: 対象カラム名
            x: X座標値
            y: Y座標値
            z: Z座標値

        Returns:
            self: メソッドチェーン用
        """
        if column_name not in self.columns:
            raise ValueError(f"カラム '{column_name}' が見つかりません")

        if (
            not hasattr(self.columns[column_name], "metadata")
            or not self.columns[column_name].metadata
        ):
            self.columns[column_name].metadata = {}

        coord_key = self.coordinate_metadata_key
        if coord_key not in self.columns[column_name].metadata:
            self.columns[column_name].metadata[coord_key] = {}

        coords = self.columns[column_name].metadata[coord_key]

        if x is not None:
            coords["x"] = x
        if y is not None:
            coords["y"] = y
        if z is not None:
            coords["z"] = z

        return self

    def get_column_coordinates(
        self, column_name: str
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """指定したカラムの座標値を取得する

        Args:
            column_name: 対象カラム名

        Returns:
            Tuple[Optional[float], Optional[float], Optional[float]]: (x, y, z)座標
        """
        if column_name not in self.columns:
            raise ValueError(f"カラム '{column_name}' が見つかりません")

        coord_key = self.coordinate_metadata_key
        coords = (
            self.columns[column_name].metadata.get(coord_key, {})
            if hasattr(self.columns[column_name], "metadata")
            else {}
        )

        return (coords.get("x"), coords.get("y"), coords.get("z"))

    def get_columns_with_coordinates(self) -> List[str]:
        """座標が設定されているカラム名のリストを返す

        Returns:
            List[str]: 座標情報を持つカラム名のリスト
        """
        coord_key = self.coordinate_metadata_key
        result = []

        for col_name, col in self.columns.items():
            if hasattr(col, "metadata") and col.metadata:
                coords = col.metadata.get(coord_key, {})
                if any(coords.get(axis) is not None for axis in ["x", "y", "z"]):
                    result.append(col_name)

        return result

    def get_coordinate_matrix(
        self, columns: Optional[List[str]] = None, include_z: bool = False
    ) -> Tuple[np.ndarray, List[str]]:
        """指定したカラムの座標をNumPy行列として取得する

        指定された列群の座標情報(x, y, [z])を抽出して N x D の行列を生成し、
        実際に抽出に成功した列名のリストと共に返します。
        一部の座標が欠損している列はスキップされます。

        Args:
            columns: 対象カラム名のリスト。Noneの場合は全ての座標付き列が対象。
            include_z: Trueの場合は Z 座標を含める（3次元）。Falseの場合は 2D座標。

        Returns:
            Tuple[np.ndarray, List[str]]: 
                - N x D の座標行列 (Nは有効な列数、Dは2または3)
                - 有効な座標が抽出できたカラム名のリスト

        Raises:
            ValueError: 有効な座標データが1つも抽出できなかった場合
        """
        if columns is None:
            columns = self.get_columns_with_coordinates()

        coord_data = []
        valid_columns = []

        for col in columns:
            try:
                x, y, z = self.get_column_coordinates(col)
                
                # 必須のx,yがあるか確認
                if x is None or y is None:
                    continue

                if include_z:
                    if z is None:
                        continue # zが要求されたのに無い場合はスキップ
                    coord_data.append([x, y, z])
                else:
                    coord_data.append([x, y])
                
                valid_columns.append(col)
            except ValueError:
                continue

        if not coord_data:
            raise ValueError("有効な座標データが見つかりません")

        return np.array(coord_data), valid_columns


    def calculate_distance(self, column1: str, column2: str) -> float:
        """2つのカラムの座標間の距離を計算する

        Args:
            column1: 1つ目のカラム名
            column2: 2つ目のカラム名

        Returns:
            float: 2点間のユークリッド距離
        """
        x1, y1, z1 = self.get_column_coordinates(column1)
        x2, y2, z2 = self.get_column_coordinates(column2)

        # 座標値が不足している場合はエラー
        if any(c is None for c in [x1, y1, x2, y2]):
            raise ValueError("距離計算に必要な座標情報が不足しています")

        # z座標が設定されていない場合は2D距離を計算
        if z1 is None or z2 is None:
            return float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

        # 3D距離を計算
        return float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2))

    def find_nearest_neighbors(
        self,
        column: str,
        n_neighbors: int = 3,
        result_column: Optional[str] = None,
    ) -> "CoordinateCollection":
        """指定した列に最も近い座標を持つ近傍列を探します

        指定された列を基準として、座標空間上で最も近い n 個の列を探索します。
        結果はメタデータに保存され、近傍情報も新しい列として追加されます。

        Args:
            column: 基準となる列名
            n_neighbors: 取得する近傍の数 (デフォルト: 3)
            result_column: 結果列名（None の場合、自動生成）

        Returns:
            CoordinateCollection: 近傍情報を含むコレクション
        """
        if column not in self.columns:
            raise ValueError(f"指定されたカラム '{column}' が見つかりません。")

        matrix, valid_cols = self.get_coordinate_matrix(include_z=True)
        if len(valid_cols) <= 1:
            raise ValueError("十分な数の座標データがありません。")

        try:
            target_idx = valid_cols.index(column)
        except ValueError:
            raise ValueError(f"カラム '{column}' には有効な座標が設定されていません。")

        # functionalロジックを呼び出し
        distances, indices = find_nearest_neighbors_logic(matrix, target_idx, n_neighbors)

        # numpy int/float を Python ネイティブに変換
        nearest_cols = [valid_cols[i] for i in indices]
        dist_list = [float(d) for d in distances]

        # クローンして結果をメタデータとプロパティ列として保存
        new_col = self.clone()
        res_name = result_column or f"{column}_neighbors"
        
        # 列として追加 (便宜上数値を1にして、メタデータで詳細を持たせる等、要件によるがここでは元の設計を踏襲して列化)
        # 本来opsでやっていたことは、結果カラムを新しく作ること
        from tascpy.core.column import NumberColumn
        step_len = len(new_col.step.values) if new_col.step is not None else len(next(iter(new_col.columns.values())).values)
        
        # 値は1.0などをダミーで入れ、メタデータに情報を格納
        result_array = np.ones(step_len)
        new_column = NumberColumn(res_name, "Nearest Neighbors", "", result_array)
        
        metadata = {
            "operation": "find_nearest_neighbors",
            "base_column": column,
            "neighbors": nearest_cols,
            "distances": dist_list
        }
        new_column.metadata = metadata
        new_col.columns[res_name] = new_column
        
        # コレクションのメタデータにも格納
        if "coordinate_domain" not in new_col.metadata:
            new_col.metadata["coordinate_domain"] = {}
        new_col.metadata["coordinate_domain"][f"nearest_neighbors_{column}"] = metadata

        return new_col


    def spatial_clustering(
        self,
        n_clusters: int = 2,
        columns: Optional[List[str]] = None,
        result_column: str = "cluster",
        algorithm: str = "kmeans"
    ) -> "CoordinateCollection":
        """座標情報に基づいてクラスタリングを行います

        列の座標位置に基づいて、類似した位置にある列をグループ化します。
        クラスタリング結果はメタデータに保存され、各列のクラスタ情報も追加されます。

        Args:
            n_clusters: クラスタ数 (デフォルト: 2)
            columns: クラスタリング対象の列名リスト（None の場合は座標を持つ全列）
            result_column: 結果列名 (デフォルト: "cluster")
            algorithm: クラスタリングアルゴリズム (デフォルト: "kmeans")

        Returns:
            CoordinateCollection: クラスタリング結果を含むコレクション
        """
        matrix, valid_cols = self.get_coordinate_matrix(columns, include_z=True)

        if len(valid_cols) < n_clusters:
            raise ValueError(f"クラスタ数({n_clusters})が有効な座標データの数({len(valid_cols)})を上回っています。")

        # クラスタリングの実行
        if algorithm.lower() != "kmeans":
            raise NotImplementedError(f"アルゴリズム '{algorithm}' は未実装です。")
            
        labels = simple_kmeans(matrix, n_clusters)
        
        # Pythonネイティブ型に変換
        labels_list = [int(l) for l in labels]
        cluster_assignment = dict(zip(valid_cols, labels_list))

        new_col = self.clone()
        
        # 各列のメタデータにクラスタIDを付与
        for idx, col_name in enumerate(valid_cols):
            cluster_id = int(labels[idx])
            if hasattr(new_col.columns[col_name], "metadata"):
                new_col.columns[col_name].metadata["cluster_id"] = cluster_id
            
        # コレクション全体のメタデータにクラスタ情報を保存
        metadata = {
            "operation": "spatial_clustering",
            "algorithm": algorithm,
            "n_clusters": n_clusters,
            "assignments": cluster_assignment
        }
        if "coordinate_domain" not in new_col.metadata:
            new_col.metadata["coordinate_domain"] = {}
        new_col.metadata["coordinate_domain"]["clustering_result"] = metadata
        
        # クラスタIDを含むサマリー列を追加
        from tascpy.core.column import NumberColumn
        step_len = len(new_col.step.values) if new_col.step is not None else len(next(iter(new_col.columns.values())).values)
        cluster_array = np.full(step_len, np.nan) # データ行という意味では意味をなさないが仕様踏襲
        
        new_column = NumberColumn(result_column, "Cluster ID", "", cluster_array)
        new_column.metadata = metadata
        new_col.columns[result_column] = new_column

        return new_col


# ファクトリ関数の定義
def create_coordinate_collection(**kwargs: Any) -> CoordinateCollection:
    """座標コレクションを作成するファクトリ関数

    座標情報はkwargsの'coordinates'パラメータで渡される辞書として指定できます。

    Args:
        **kwargs: CoordinateCollectionコンストラクタに渡す引数
            - coordinates: カラム名をキーとし、座標情報を値とする辞書（オプション）
                例: {'column1': {'x': 1.0, 'y': 2.0, 'z': 3.0}}

    Returns:
        CoordinateCollection: 作成された座標コレクション
    """
    return CoordinateCollection(**kwargs)


# ドメインファクトリーへの登録
DomainCollectionFactory.register("coordinate", create_coordinate_collection)
