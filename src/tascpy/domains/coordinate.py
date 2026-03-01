from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING, Union
import numpy as np
from ..core.collection import ColumnCollection
from ..core.step import Step
from ..core.column import Column
from .factory import DomainCollectionFactory

if TYPE_CHECKING:
    from ..typing.coordinate import CoordinateCollectionOperations


class CoordinateCollection(ColumnCollection):
    """座標値をメタデータとして保持する特化コレクションクラス

    各カラムに対して座標値(x, y, z)を関連付け、
    座標ベースの計算を可能にします。
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
    def ops(self):
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
            return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # 3D距離を計算
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


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
