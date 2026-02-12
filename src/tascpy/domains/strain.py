from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
from ..core.step import Step
from ..core.column import Column
from .coordinate import CoordinateCollection
from .factory import DomainCollectionFactory

if TYPE_CHECKING:
    from ..typing.strain import StrainCollectionOperations

class StrainCollection(CoordinateCollection):
    """ひずみデータを扱うための特化コレクションクラス
    
    CoordinateCollectionを継承し、各ゲージの座標情報を持つことができます。
    また、3軸ロゼットゲージなどのグルーピング情報をメタデータとして管理します。
    """
    
    def __init__(
        self,
        step: Optional[Step] = None,
        columns: Optional[Dict[str, Column]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        coordinate_metadata_key: str = "coordinates",
        coordinates: Optional[Union[Dict[str, Dict[str, Optional[float]]], str]] = None,
        rosettes: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        """初期化
        
        Args:
            step: ステップデータ
            columns: カラムデータ
            metadata: メタデータ
            coordinate_metadata_key: 座標データキー
            coordinates: 座標情報
            rosettes: ロゼットゲージ定義辞書
                {
                    "rosette_name": {
                        "columns": ["ch1", "ch2", "ch3"],
                        "type": "rectangular", # "rectangular" (0/45/90) or "delta" (0/60/120)
                        "orientation": 0.0 # 基準軸からの角度(deg)
                    }
                }
            **kwargs: その他の引数
        """
        super().__init__(
            step=step, 
            columns=columns, 
            metadata=metadata, 
            coordinate_metadata_key=coordinate_metadata_key,
            coordinates=coordinates,
            **kwargs
        )
        
        # ロゼット定義をメタデータに保存
        if rosettes:
            if "rosettes" not in self.metadata:
                self.metadata["rosettes"] = {}
            self.metadata["rosettes"].update(rosettes)

    @property
    def domain(self) -> str:
        return "strain"

    @property
    def ops(self):
        """操作プロキシクラスを返す"""
        from ..operations.proxy import CollectionOperations
        
        # 型ヒント用 (実際の実装はまだないのでCollectionOperationsを返すか、将来的にStrainCollectionOperationsを作成)
        # return StrainCollectionOperations(self, domain="strain")
        return CollectionOperations(self, domain=self.domain)
    
    def get_rosette_info(self, rosette_name: str) -> Dict[str, Any]:
        """指定されたロゼットの情報を取得"""
        rosettes = self.metadata.get("rosettes", {})
        if rosette_name not in rosettes:
            raise KeyError(f"ロゼット '{rosette_name}' は定義されていません")
        return rosettes[rosette_name]

    def get_defined_rosettes(self) -> List[str]:
        """定義されているロゼット名のリストを取得"""
        return list(self.metadata.get("rosettes", {}).keys())
    
    def add_rosette(
        self, 
        name: str, 
        columns: List[str], 
        rosette_type: str = "rectangular", 
        orientation: float = 0.0
    ) -> "StrainCollection":
        """ロゼット定義を追加
        
        Args:
            name: ロゼット名
            columns: ゲージカラム名のリスト (3つ)
            rosette_type: "rectangular" (0/45/90) or "delta" (0/60/120)
            orientation: 第1ゲージの角度 (deg)
        """
        if len(columns) != 3:
            raise ValueError("ロゼットゲージには3つのカラムが必要です")
            
        for col in columns:
            if col not in self.columns:
                raise ValueError(f"カラム '{col}' がコレクションに存在しません")
        
        if "rosettes" not in self.metadata:
            self.metadata["rosettes"] = {}
            
        self.metadata["rosettes"][name] = {
            "columns": columns,
            "type": rosette_type,
            "orientation": orientation
        }
        return self

    def clone(self) -> "StrainCollection":
        """コレクションの複製を作成"""
        # 親クラスのcloneロジックを再利用したいが、戻り値の型が異なるため
        # メタデータを手動で構築して新しいインスタンスを作成する
        
        # CoordinateCollection.clone()の実装を参考に、StrainCollection用に再実装
        
        coordinate_info = self.metadata.get("coordinate_domain", {})
        
        # 列のクローンを作成
        cloned_columns = {}
        for name, column in self.columns.items():
            cloned_column = column.clone()
            
            # 座標メタデータのコピー (CoordinateCollectionと同じロジック)
            coord_key = self.coordinate_metadata_key
            if (
                hasattr(column, "metadata") 
                and column.metadata 
                and coord_key in column.metadata
            ):
                if coord_key not in cloned_column.metadata:
                    cloned_column.metadata[coord_key] = {}
                    
                coords = column.metadata[coord_key]
                cloned_column.metadata[coord_key] = {
                    "x": coords.get("x"),
                    "y": coords.get("y"),
                    "z": coords.get("z"),
                }
            cloned_columns[name] = cloned_column
            
        import copy
        new_metadata = copy.deepcopy(self.metadata)
        
        # 結果オブジェクトのコピー（ColumnCollectionのロジック）
        # _resultsへのアクセスが必要だが、親クラスのprivate変数
        # ColumnCollection.clone()では _results = self._results.copy() している
        
        new_instance = StrainCollection(
            step=self.step.clone() if self.step else None,
            columns=cloned_columns,
            metadata=new_metadata,
            coordinate_metadata_key=coordinate_info.get("coordinate_metadata_key", "coordinates"),
            rosettes=None # メタデータに含まれているのでNoneでよい
        )
        
        # 結果オブジェクトのコピー
        if hasattr(self, "_results"):
             new_instance._results = self._results.copy()
             
        return new_instance

# ドメインファクトリーへの登録
def create_strain_collection(**kwargs: Any) -> StrainCollection:
    return StrainCollection(**kwargs)

DomainCollectionFactory.register("strain", create_strain_collection)
