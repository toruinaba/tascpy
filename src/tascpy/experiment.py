"""
Experimentクラスの定義

従来のExperimentクラスの機能をColumnCollectionクラスをベースに実装
互換性を保ちつつ、より柔軟なデータ操作を可能にする
"""

from typing import Dict, List, Any, Optional, Union, Callable, TextIO
from pathlib import Path

from .core.collection import ColumnCollection
from .core.column import Column
from .core.io_formats import get_format, FILE_FORMATS


class Experiment(ColumnCollection):
    """実験データを保持するクラス

    ColumnCollectionを継承し、従来のExperimentクラスとの互換性を提供する
    """

    @classmethod
    def from_file(
        cls, filepath: Union[str, Path], format_name: str = "standard", **kwargs
    ):
        """ファイルからExperimentを作成する

        Args:
            filepath: 読み込むファイルパス
            format_name: 使用するファイルフォーマットの名前
            **kwargs: フォーマット設定を上書きするためのキーワード引数

        Returns:
            Experiment: 読み込んだデータを含む新しいExperimentオブジェクト
        """
        # ColumnCollectionの読み込み機能を使用
        collection = super().from_file(filepath, format_name, **kwargs)

        # Experimentオブジェクトに変換して返す
        experiment = cls(
            step=collection.step,
            columns=collection.columns,
            metadata=collection.metadata,
        )

        return experiment

    # 以下、従来のExperimentクラスとの互換性のためのプロパティとメソッド

    @property
    def chs(self) -> List[str]:
        """チャンネル名のリスト"""
        return [col.ch for col in self.columns.values()]

    @property
    def names(self) -> List[str]:
        """列名のリスト"""
        return list(self.columns.keys())

    @property
    def units(self) -> List[str]:
        """単位のリスト"""
        return [col.unit for col in self.columns.values()]

    @property
    def steps(self) -> List[int]:
        """ステップ値のリスト"""
        return self.step.values

    def save(
        self, filepath: Union[str, Path], format_name: str = "standard", **kwargs
    ) -> None:
        """ファイルに保存する (従来のsaveメソッドとの互換性用)

        Args:
            filepath: 保存先ファイルパス
            format_name: ファイルフォーマット名
            **kwargs: フォーマット設定の上書き
        """
        self.to_file(filepath, format_name, **kwargs)

    def clone(self):
        """Experimentのクローンを作成"""
        # 親クラスのcloneメソッドを呼び出し
        collection_clone = super().clone()

        # Experimentオブジェクトに変換して返す
        return Experiment(
            step=collection_clone.step,
            columns=collection_clone.columns,
            metadata=collection_clone.metadata,
        )


def load_experiment(
    filepath: Union[str, Path], format_name: str = "standard", **kwargs
) -> Experiment:
    """ファイルからExperimentを読み込むユーティリティ関数

    Args:
        filepath: 読み込むファイルパス
        format_name: 使用するファイルフォーマットの名前
        **kwargs: フォーマット設定を上書きするためのキーワード引数

    Returns:
        Experiment: 読み込んだデータを含む新しいExperimentオブジェクト
    """
    return Experiment.from_file(filepath, format_name, **kwargs)
