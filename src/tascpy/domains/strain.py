from typing import Dict, Any, Optional, Union, TYPE_CHECKING
from ..core.step import Step
from ..core.column import Column
from .coordinate import CoordinateCollection
from .factory import DomainCollectionFactory

if TYPE_CHECKING:
    from ..typing.strain import StrainCollectionOperations


class StrainCollection(CoordinateCollection):
    """ひずみデータを扱うための特化コレクションクラス
    
    CoordinateCollectionを継承し、各ゲージの座標情報に加えて、
    ロゼットゲージ（3軸ゲージなど）のグルーピング情報を管理します。
    """

    def __init__(
        self,
        step: Optional[Step] = None,
        columns: Optional[Dict[str, Column]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        coordinate_metadata_key: str = "coordinates",
        coordinates: Optional[Union[Dict[str, Dict[str, Optional[float]]], str]] = None,
        rosette_metadata_key: str = "rosettes",
        rosettes: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        """初期化

        Args:
            step: ステップデータ
            columns: カラムデータ
            metadata: メタデータ
            coordinate_metadata_key: 座標データが格納されるメタデータのキー
            coordinates: 座標情報
            rosette_metadata_key: ロゼット情報が格納されるメタデータのキー
            rosettes: ロゼット定義辞書
                例: {
                    "rosette_A": {
                        "columns": ["ch1", "ch2", "ch3"],
                        "type": "rectangular",
                        "orientation": 0.0
                    }
                }
        """
        super().__init__(
            step=step, 
            columns=columns, 
            metadata=metadata, 
            coordinate_metadata_key=coordinate_metadata_key,
            coordinates=coordinates,
            **kwargs
        )

        # ロゼットメタデータのキーを保存
        self.metadata.update(
            {"strain_domain": {"rosette_metadata_key": rosette_metadata_key}}
        )

        # ロゼット情報の登録
        if rosettes:
            for name, info in rosettes.items():
                self.add_rosette(name, info)

    @property
    def domain(self) -> str:
        """ドメイン識別子を返す"""
        return "strain"

    @property
    def ops(self):
        """操作プロキシクラスを返す"""
        from ..operations.proxy import CollectionOperations

        if TYPE_CHECKING:
             from ..typing.strain import StrainCollectionOperations
             return StrainCollectionOperations(self, domain="strain") # type: ignore
        else:
             return CollectionOperations(self, domain=self.domain)

    @property
    def plot(self):
        """可視化プロキシクラスを返す"""
        from ..visualization.strain.plotter import StrainPlotter
        return StrainPlotter(self)

    @property
    def rosette_metadata_key(self) -> str:
        """ロゼットデータが格納されるメタデータのキーを返す"""
        return self.metadata.get("strain_domain", {}).get(
            "rosette_metadata_key", "rosettes"
        )
    
    def add_rosette(self, name: str, info: Dict[str, Any]) -> "StrainCollection":
        """ロゼット定義を追加する
        
        Args:
            name: ロゼット名
            info: ロゼット情報 (columns, type, orientationなど)
        """
        key = self.rosette_metadata_key
        if key not in self.metadata:
            self.metadata[key] = {}
            
        # バリデーション（簡易）
        if "columns" not in info:
            raise ValueError(f"ロゼット情報には 'columns' リストが必要です: {name}")
            
        columns = info["columns"]
        if len(columns) != 3:
            # 現状は3軸ロゼットを想定
            # 必要に応じて緩和
            pass

        self.metadata[key][name] = info
        return self

    def get_rosette(self, name: str) -> Optional[Dict[str, Any]]:
        """ロゼット情報を取得する"""
        key = self.rosette_metadata_key
        return self.metadata.get(key, {}).get(name)

    def get_rosettes(self) -> Dict[str, Dict[str, Any]]:
        """全てのロゼット情報を取得する"""
        key = self.rosette_metadata_key
        return self.metadata.get(key, {})

    def clone(self) -> "StrainCollection":
        """コレクションの複製を作成"""
        # CoordinateCollection.clone() をベースにするが、
        # CoordinateCollectionは自分自身のクラス(CoordinateCollection)を返してしまうため、
        # ここで再実装するか、super().clone()の結果をキャスト的に使う必要がある。
        # ただしmetadataはdeepcopyされているので、StrainCollectionとして作り直すのが確実。
        
        import copy
        
        strain_info = self.metadata.get("strain_domain", {})
        coord_info = self.metadata.get("coordinate_domain", {})
        
        cloned_columns = {}
        for name, column in self.columns.items():
            cloned_columns[name] = column.clone()
            
        return StrainCollection(
            step=self.step.clone() if self.step else None,
            columns=cloned_columns,
            metadata=copy.deepcopy(self.metadata),
            coordinate_metadata_key=coord_info.get("coordinate_metadata_key", "coordinates"),
            rosette_metadata_key=strain_info.get("rosette_metadata_key", "rosettes")
        )

# ファクトリ関数の定義
def create_strain_collection(**kwargs: Any) -> StrainCollection:
    """ひずみコレクションを作成するファクトリ関数"""
    return StrainCollection(**kwargs)

# ドメインファクトリーへの登録
DomainCollectionFactory.register("strain", create_strain_collection)
