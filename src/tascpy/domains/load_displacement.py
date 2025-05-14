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
    """荷重と変形のデータセットを扱うための特化コレクションクラス"""

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
            load_column: 荷重データを含むカラム名
            displacement_column: 変形データを含むカラム名
        """
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
    def ops(self):
        """操作プロキシクラスを返す"""
        from ..operations.proxy import CollectionOperations

        if TYPE_CHECKING:
            from ..typing.load_displacement import (
                LoadDisplacementCollectionOperations,
            )

            return LoadDisplacementCollectionOperations(self, domain="load_displacement")  # type: ignore
        else:
            return CollectionOperations(self, domain=self.domain)

    @property
    def load_column(self) -> str:
        """荷重データを含むカラム名を返す

        Returns:
            str: 荷重カラム名
        """
        return self.metadata.get("load_displacement_domain", {}).get(
            "load_column", "load"
        )

    @property
    def displacement_column(self) -> str:
        """変形データを含むカラム名を返す

        Returns:
            str: 変形カラム名
        """
        return self.metadata.get("load_displacement_domain", {}).get(
            "displacement_column", "displacement"
        )

    def clone(self) -> "LoadDisplacementCollection":
        """コレクションの複製を作成

        Returns:
            LoadDisplacementCollection: 複製されたコレクション
        """
        ld_info = self.metadata.get("load_displacement_domain", {})

        return LoadDisplacementCollection(
            step=self.step.clone() if self.step else None,
            columns={name: column.clone() for name, column in self.columns.items()},
            metadata=self.metadata.copy(),
            load_column=ld_info.get("load_column", "load"),
            displacement_column=ld_info.get("displacement_column", "displacement"),
        )

    def keys(self) -> list[str]:
        """利用可能なキーのリストを返す

        通常のカラム名に加えて、メタデータのトップレベルキーも含める
        ただし、カラム名と衝突するメタデータのキーは優先度が低くなる

        Returns:
            list[str]: カラム名とアクセス可能なメタデータキーのリスト
        """
        # 基本のキーセット
        key_set = set(self.columns.keys())

        # 特殊キーを追加
        key_set.add("step")
        key_set.add("load")
        key_set.add("displacement")
        key_set.add("curves")

        # メタデータのトップレベルキーを追加（カラム名と衝突しないもの）
        if self.metadata:
            for meta_key in self.metadata.keys():
                if meta_key not in key_set and meta_key not in ["curves", "metadata"]:
                    key_set.add(meta_key)

        return sorted(list(key_set))


# ファクトリ関数の定義
def create_load_displacement_collection(**kwargs: Any) -> LoadDisplacementCollection:
    """荷重-変形コレクションを作成するファクトリ関数"""
    return LoadDisplacementCollection(**kwargs)


# ドメインファクトリーへの登録
DomainCollectionFactory.register(
    "load_displacement", create_load_displacement_collection
)
