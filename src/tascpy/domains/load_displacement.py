from typing import Dict, Any, Optional
from ..core.collection import ColumnCollection
from ..core.indices import Indices
from ..core.column import Column
from .factory import DomainCollectionFactory


class LoadDisplacementCollection(ColumnCollection):
    """荷重と変形のデータセットを扱うための特化コレクションクラス"""

    def __init__(
        self,
        step: Optional[Indices] = None,
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
        if columns and (
            load_column not in columns or displacement_column not in columns
        ):
            raise ValueError(
                f"カラム '{load_column}' または '{displacement_column}' が見つかりません"
            )

    @property
    def domain(self) -> str:
        """このコレクションのドメイン名を返す

        Returns:
            str: ドメイン名
        """
        return "load_displacement"

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


# ファクトリ関数の定義
def create_load_displacement_collection(**kwargs: Any) -> LoadDisplacementCollection:
    """荷重-変形コレクションを作成するファクトリ関数"""
    return LoadDisplacementCollection(**kwargs)


# ドメインファクトリーへの登録
DomainCollectionFactory.register(
    "load_displacement", create_load_displacement_collection
)
