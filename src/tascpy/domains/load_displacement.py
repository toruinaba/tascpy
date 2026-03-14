from typing import Dict, Any, Optional, TYPE_CHECKING
from ..core.collection import ColumnCollection
from ..core.step import Step
from ..core.column import Column
from .factory import DomainCollectionFactory

if TYPE_CHECKING:
    from ..typing.load_displacement import (
        LoadDisplacementCollectionOperations,
    )


class LoadDisplacementCollection(ColumnCollection):
    """荷重と変形のデータセットを扱うための特化コレクションクラス
    
    Examples:
        >>> from tascpy.domains.load_displacement import LoadDisplacementCollection
        >>> from tascpy.core.column import NumberColumn
        >>> cols = {"load": NumberColumn("load", "Load", "kN", [0.0, 10.0]), "disp": NumberColumn("disp", "Disp", "mm", [0.0, 1.0])}
        >>> col = LoadDisplacementCollection(columns=cols, load_column="load", displacement_column="disp")
        >>> col["load"].values
        [0.0, 10.0]
    """

    def __init__(
        self,
        step: Optional[Step] = None,
        columns: Optional[Dict[str, Column]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        load_column: str = "load",
        displacement_column: str = "displacement",
        **kwargs: Any,
    ):
        """初期化

        Args:
            step: ステップデータ
            columns: カラムデータ
            metadata: メタデータ
            load_column: 荷重データを含むカラム名（デフォルト: "load"）
            displacement_column: 変形データを含むカラム名（デフォルト: "displacement"）
        """
        if load_column is None:
            raise ValueError("load_column は必須です。荷重データのカラム名を指定してください。")
        if displacement_column is None:
            raise ValueError("displacement_column は必須です。変形データのカラム名を指定してください。")

        super().__init__(step=step, columns=columns, metadata=metadata)

        # 荷重と変形のカラム名をメタデータに保存
        # 操作関数がこの情報を使用する
        self.metadata.update(
            {
                "load_displacement_domain": {
                    "load_column": load_column,
                    "displacement_column": displacement_column,
                }
            }
        )

        # カラムが存在するかチェック (データがある場合のみ)
        if columns:
            if load_column not in columns:
                raise ValueError(
                    f"load_column に指定したカラム '{load_column}' が見つかりません"
                )
            if displacement_column not in columns:
                raise ValueError(
                    f"displacement_column に指定したカラム '{displacement_column}' が見つかりません"
                )

    def __getitem__(self, key: str) -> Any:
        """項目へのアクセスを提供するメソッド

        通常のカラムアクセスに加え、ドット区切りのパス形式でメタデータやカーブデータへのアクセスをサポート。
        例:
            collection["load"] -> 荷重カラム (通常のアクセス)
            collection["curves.skeleton_curve"] -> スケルトン曲線データ辞書
            collection["curves.skeleton_curve.y"] -> スケルトン曲線のy座標データ
            collection["curves.skeleton_curve.columns.y"] -> スケルトン曲線のy座標カラムオブジェクト
            collection["analysis.yield_point"] -> メタデータ内の降伏点情報（analysisキーを直接指定）
            collection["metadata.analysis.yield_point"] -> 上と同じ（metadataキーを明示）

        Args:
            key: カラム名またはドット区切りのアクセスパス

        Returns:
            Any: 取得したデータ（カラム、リスト、辞書など）

        Raises:
            KeyError: 指定されたキーまたはパスが見つからない場合
        """
        if isinstance(key, int):
            return super().__getitem__(key)

        # キーにドットが含まれる場合はパスアクセスとして処理
        if "." in key:
            path_parts = key.split(".")

            # メタデータへの直接アクセスをチェック
            # metadata キーなしでもメタデータ内の要素にアクセスできるようにする
            if path_parts[0] in self.metadata and path_parts[0] not in [
                "curves",
                "metadata",
            ]:
                current = self.metadata
                try:
                    for part in path_parts:
                        if isinstance(current, dict):
                            if part not in current:
                                raise KeyError(
                                    f"'{part}' というキーはパス '{key}' の中に存在しません"
                                )
                            current = current[part]
                        else:
                            raise KeyError(
                                f"'{part}' にアクセスしようとしましたが、現在のオブジェクトは辞書ではありません"
                            )
                    return current
                except KeyError as e:
                    raise KeyError(f"{str(e)}")

            # 以下は既存のパス処理コード
            current = self

            # パスを辿って再帰的にアクセス
            for part in path_parts:
                if isinstance(current, dict):
                    if part not in current:
                        raise KeyError(
                            f"'{part}' というキーはパス '{key}' の中に存在しません"
                        )
                    current = current[part]
                elif isinstance(current, LoadDisplacementCollection):
                    try:
                        # 次の部分がメタデータの場合
                        if part == "metadata":
                            current = current.metadata
                        # 次の部分がカーブデータの場合
                        elif part == "curves":
                            # curves キーがなくても空辞書を返す
                            current = current.metadata.get("curves", {})
                        # 次の部分が通常のカラムの場合
                        else:
                            current = current[part]  # 通常のカラムアクセス
                    except KeyError:
                        raise KeyError(
                            f"'{part}' というキーはコレクションに存在しません"
                        )
                else:
                    # リストやその他のオブジェクトにインデックスとしてアクセス試行
                    try:
                        if isinstance(current, list) and part.isdigit():
                            current = current[int(part)]
                        elif hasattr(current, part):
                            current = getattr(current, part)
                        else:
                            raise KeyError(
                                f"'{part}' というキーまたは属性が存在しません"
                            )
                    except (IndexError, AttributeError):
                        raise KeyError(
                            f"パス '{key}' の '{part}' 部分でアクセスエラーが発生しました"
                        )

            return current

        # 特殊ショートカットキーの処理
        if key == "load":
            return super().__getitem__(self.load_column)
        elif key == "displacement":
            return super().__getitem__(self.displacement_column)
        elif key == "curves":
            # curves キーがなくても空辞書を返す
            return self.metadata.get("curves", {})
        # メタデータへの直接アクセス（単一キー）
        elif key in self.metadata and key not in self.columns:
            return self.metadata[key]

        # 通常のカラムアクセス
        try:
            return super().__getitem__(key)
        except KeyError:
            # カーブデータへの直接アクセス試行
            if (
                self.metadata
                and "curves" in self.metadata
                and key in self.metadata["curves"]
            ):
                return self.metadata["curves"][key]
            # それ以外はエラー
            raise KeyError(f"'{key}' というカラムまたはカーブデータが見つかりません")

    @property
    def domain(self) -> str:
        """ドメイン識別子を返す"""
        return "load_displacement"

    @property
    def ops(self) -> "LoadDisplacementCollectionOperations":
        """操作プロキシクラスを返す"""
        from tascpy.analytics.operations.proxy import CollectionOperations

        if TYPE_CHECKING:
            from ..typing.load_displacement import (
                LoadDisplacementCollectionOperations,
            )

            return LoadDisplacementCollectionOperations(self, domain="load_displacement")  # type: ignore
        else:
            return CollectionOperations(self, domain=self.domain)
            
    @property
    def plot(self):
        """荷重-変位データの可視化プロキシクラスを返す
        
        Returns:
            LoadDisplacementPlotter: 荷重-変位用の可視化機能を提供するPlotter
        """
        if not hasattr(self, "_plotter"):
            from tascpy.visualization.plotters.load_displacement.plotter import LoadDisplacementPlotter
            
            self._plotter = LoadDisplacementPlotter(self)
        return self._plotter

    @property
    def load_column(self) -> str:
        """荷重データを含むカラム名を返す

        Returns:
            str: 荷重カラム名
        """
        return self.metadata["load_displacement_domain"]["load_column"]

    @property
    def displacement_column(self) -> str:
        """変形データを含むカラム名を返す

        Returns:
            str: 変形カラム名
        """
        return self.metadata["load_displacement_domain"]["displacement_column"]

    def clone(self) -> "LoadDisplacementCollection":
        """コレクションの複製を作成

        Returns:
            LoadDisplacementCollection: 複製されたコレクション
        """
        new_collection = LoadDisplacementCollection(
            step=self.step.clone() if self.step else None,
            columns={name: column.clone() for name, column in self.columns.items()},
            metadata=self.metadata.copy(),
            load_column=self.load_column,
            displacement_column=self.displacement_column,
        )
        new_collection._results = self._results.copy()
        return new_collection

    def keys(self) -> list[str]:
        """利用可能なキーのリストを返す

        通常のカラム名に加えて、メタデータのトップレベルキーも含める
        ただし、カラム名と衝突するメタデータのキーは優先度が低くなる

        Returns:
            list[str]: カラム名とアクセス可能なメタデータキーのリスト
        """
        key_set = set(super().keys())
        key_set.add("step")
        key_set.add("curves")
        # メタデータのトップレベルキーを追加（カラム名と衝突しないもの）
        if self.metadata:
            for meta_key in self.metadata.keys():
                if meta_key not in key_set and meta_key not in ["curves", "metadata"]:
                    key_set.add(meta_key)
        return sorted(list(key_set))

    @property
    def load_data(self):
        """荷重データ配列を取得 (NaNを保持)
        
        Returns:
            np.ndarray: 荷重データの配列
        """
        import numpy as np
        return np.array([v if v is not None else np.nan for v in self[self.load_column].values])

    @property
    def displacement_data(self):
        """変位データ配列を取得 (NaNを保持)
        
        Returns:
            np.ndarray: 変位データの配列
        """
        import numpy as np
        return np.array([v if v is not None else np.nan for v in self[self.displacement_column].values])
        
    @property
    def valid_data_mask(self):
        """NaNを含まない有効なデータのブールマスクを取得
        
        Returns:
            np.ndarray: 有効なデータのブールマスク
        """
        import numpy as np
        return ~(np.isnan(self.load_data) | np.isnan(self.displacement_data))
        
    @property
    def valid_data(self):
        """有効な(変位, 荷重)の配列の組を取得
        
        Returns:
            tuple[np.ndarray, np.ndarray]: (変位データ, 荷重データ)
        """
        mask = self.valid_data_mask
        return self.displacement_data[mask], self.load_data[mask]

    def get_ld_cycle_arrays(
        self,
        load_column: Optional[str] = None,
        displacement_column: Optional[str] = None,
        cycle_marker_column: Optional[str] = None,
    ):
        """荷重・変位・サイクルマーカーの numpy 配列を取得する。

        カラム名を省略した場合はメタデータから自動解決します。
        サイクルマーカーカラムが存在しない場合は ``KeyError`` を raise します
        （自動生成はオペレーション層の責務）。

        Args:
            load_column: 荷重カラム名（None 時はメタデータから解決）
            displacement_column: 変位カラム名（None 時はメタデータから解決）
            cycle_marker_column: サイクルマーカーカラム名（None 時は自動検出）

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray]: (loads, displacements, markers)

        Raises:
            KeyError: サイクルマーカーカラムが見つからない場合

        Examples:
            >>> loads, disps, markers = col.get_ld_cycle_arrays()
            >>> loads, disps, markers = col.get_ld_cycle_arrays(cycle_marker_column="cycle")
        """
        import numpy as np

        loads = np.array(self[load_column or self.load_column].values)
        disps = np.array(self[displacement_column or self.displacement_column].values)

        # サイクルマーカー解決: 明示指定のみ。未指定・未存在の場合は KeyError
        if cycle_marker_column is None:
            raise KeyError(
                "cycle_marker_column が指定されていません。"
                "先に `col.ops.cycle_count()` を実行してマーカー列を作成するか、"
                "cycle_marker_column を明示的に指定してください。"
            )
        if cycle_marker_column not in self.columns:
            raise KeyError(f"サイクルマーカーカラム '{cycle_marker_column}' が見つかりません")
        markers = np.array(self[cycle_marker_column].values)

        return loads, disps, markers



# ファクトリ関数の定義
def create_load_displacement_collection(**kwargs: Any) -> LoadDisplacementCollection:
    """荷重-変形コレクションを作成するファクトリ関数
    
    Examples:
        >>> from tascpy.domains.load_displacement import create_load_displacement_collection
        >>> col = create_load_displacement_collection()
        >>> type(col).__name__
        'LoadDisplacementCollection'
    """
    return LoadDisplacementCollection(**kwargs)


# ドメインファクトリーへの登録
DomainCollectionFactory.register(
    "load_displacement", create_load_displacement_collection
)
