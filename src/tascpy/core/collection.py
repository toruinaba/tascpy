from typing import (
    Dict,
    List,
    Any,
    Optional,
    Union,
    TypeVar,
    Callable,
    TextIO,
    TYPE_CHECKING,
)
from pathlib import Path
from copy import deepcopy
from .step import Step
from .column import (
    Column,
    NumberColumn,
    StringColumn,
    InvalidColumn,
    detect_column_type,
)
from ..core.io_formats import get_format, FILE_FORMATS

if TYPE_CHECKING:
    from ..typing.core import CoreCollectionOperations

T = TypeVar("T")


class ColumnCollection:
    """複数のcollumnと一つのstepを保持するクラス"""

    domain: str = "core"

    def __init__(
        self,
        step: Step,
        columns: dict[str, Union[Column, NumberColumn, StringColumn, InvalidColumn]],
        metadata=None,
        auto_detect_types=False,
    ):
        """
        Args:
            step: Stepオブジェクトまたはステップ値のリスト
            columns: {名前: Column}の辞書または{名前: 値リスト}の辞書
            metadata: メタデータの辞書
            auto_detect_types: カラム型を自動判定するかどうか
        """
        # ステップの初期化
        if isinstance(step, Step):
            self.step: Step = step
        else:
            self.step: Step = Step(values=step if step is not None else [])

        # 列の初期化
        self.columns = {}
        if columns:
            for name, column in columns.items():
                if isinstance(column, Column):
                    self.columns[name] = column
                else:
                    # 自動判定が有効な場合は型を自動判定
                    if auto_detect_types:
                        self.columns[name] = detect_column_type(
                            None, name, None, column
                        )
                    else:
                        self.columns[name] = Column(None, name, None, column)
        self.metadata = metadata if metadata is not None else {}

    def __len__(self) -> int:
        return len(self.step)

    def __getitem__(self, key) -> Union["ColumnCollection", Column, Dict[str, Any]]:
        """キーに基づいてデータにアクセス
        Args:
            key: 列名、チャンネル名、またはインデックス(整数/スライス)

        Returns:
            列名/チャンネル名の場合: 指定された列
            整数インデックスの場合: 指定された行のデータを含む辞書
            スライスの場合: 指定された行範囲を含む新しいColumnCollection

        Raises:
            KeyError: 指定された列名/チャンネル名が存在しない場合
            TypeError: キーが文字列または整数/スライスでない場合
        """
        if isinstance(key, str):
            # 列名によるアクセス
            if key == "step":
                return self.step
            elif key in self.columns:
                return self.columns[key]
            else:
                # チャンネル名で検索
                for col_name, column in self.columns.items():
                    if hasattr(column, "ch") and column.ch == key:
                        return column
                # 見つからなかった場合
                raise KeyError(f"列またはチャンネル '{key}' が存在しません")
        elif isinstance(key, (int, slice)):
            # インデックスによるアクセス
            if isinstance(key, int):
                # 単一行の場合
                values = {}
                for name, column in self.columns.items():
                    values[name] = column.values[key]
                from .row import Row

                return Row(step=self.step.values[key], values=values)
            else:
                # スライスの場合は新しいColumnCollectionを返す
                new_step = Step(values=self.step.values[key])
                new_columns = {}
                for name, column in self.columns.items():
                    new_column = column.clone()
                    new_column.values = column.values[key]  # スライス
                    new_columns[name] = new_column

                return ColumnCollection(
                    step=new_step, columns=new_columns, metadata=self.metadata.copy()
                )
        else:
            raise TypeError(
                f"キーは文字列または整数/スライスである必要があります: {type(key)}"
            )

    def clone(self):
        """コレクションのクローンを作成"""
        return ColumnCollection(
            step=self.step.clone(),
            columns={name: column.clone() for name, column in self.columns.items()},
            metadata=deepcopy(self.metadata),
        )

    def add_column(
        self, name: str, column: Union[Column, List[Any]]
    ) -> "ColumnCollection":
        """列を追加
        Args:
            name: 列名
            column: Columnオブジェクトまたは値のリスト

        Returns:
            self(メソッドチェーン用)
        """
        if name in self.columns:
            raise KeyError(f"列'{name}'はすでに存在します")
        if isinstance(column, Column):
            self.columns[name] = column
        else:
            self.columns[name] = Column(None, name, None, column)
        self.harmonize_length()
        return self

    def remove_column(self, name: str) -> "ColumnCollection":
        """列を削除
        Args:
            name: 列名

        Returns:
            self(メソッドチェーン用)
        """
        if name not in self.columns:
            raise KeyError(f"列'{name}'は存在しません")
        del self.columns[name]
        return self

    def harmonize_length(self) -> None:
        """列の長さをStepに合わせる"""
        for column in self.columns.values():
            if len(column) != len(self.step):
                raise ValueError(
                    f"列'{column.name}'の長さ({len(column)})がStepの長さ({len(self.step)})と一致しません"
                )
        # step, columnsの長さを揃える（ロジック実装次第追加予定）

    @property
    def ops(self):
        """操作プロキシクラスを返す"""
        from ..operations.proxy import CollectionOperations

        if TYPE_CHECKING:
            # ColumnCollectionのドメインはcoreなので、CoreCollectionOperationsのみを返す
            from ..typing.core import CoreCollectionOperations

            return CoreCollectionOperations(self, domain="core")  # type: ignore
        else:
            return CollectionOperations(self, domain=self.domain)

    def __repr__(self) -> str:
        """文字列表現"""
        return f"ColumnCollection(step={self.step}, columns={self.columns}, metadata={self.metadata})"

    def head(self, n: int = 5) -> "ColumnCollection":
        """最初のn行を取得
        Args:
            n: 行数

        Returns:
            ColumnCollection: 最初のn行を含む新しいColumnCollection

        Raises:
            ValueError: nが負の整数または列数を超える場合
        """
        if n < 0:
            raise ValueError("nは0以上の整数である必要があります")
        if n > len(self):
            raise ValueError(f"nは{len(self)}以下である必要があります")
        return self[:n]

    def tail(self, n: int = 5) -> "ColumnCollection":
        """最後のn行を取得
        Args:
            n: 行数

        Returns:
            ColumnCollection: 最後のn行を含む新しいColumnCollection

        Raises:
            ValueError: nが負の整数または列数を超える場合
        """
        if n < 0:
            raise ValueError("nは0以上の整数である必要があります")
        if n > len(self):
            raise ValueError(f"nは{len(self)}以下である必要があります")
        return self[-n:]

    def describe(self, detail: bool = False) -> Dict[str, Dict[str, Any]]:
        """データの概要を取得

        Args:
            detail: 詳細表示するかどうか。True の場合は統計情報も含む。

        Returns:
            辞書: 各列の情報を含む辞書
        """
        stats = {}
        for name, column in self.columns.items():
            # 簡易表示の場合は列名とデータ数のみ
            if not detail:
                stats[name] = {"count": len(column.values)}
            # 詳細表示の場合は統計情報も含む
            else:
                if isinstance(column, NumberColumn):
                    stats[name] = {
                        "count": len(column.values),
                        "mean": column.mean(),
                        "min": column.min(),
                        "max": column.max(),
                        "std": column.std(),
                        "type": str(type(column).__name__),
                    }
                elif isinstance(column.values, (list, tuple)) and all(
                    isinstance(x, (int, float)) for x in column.values if x is not None
                ):
                    # 数値のリストだが NumberColumn ではない場合
                    values = [x for x in column.values if x is not None]
                    if values:
                        stats[name] = {
                            "count": len(column.values),
                            "mean": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "type": str(type(column).__name__),
                        }
                    else:
                        stats[name] = {
                            "count": len(column.values),
                            "type": str(type(column).__name__),
                        }
                else:
                    # 数値以外のデータの場合
                    stats[name] = {
                        "count": len(column.values),
                        "type": str(type(column).__name__),
                    }
        return stats

    def apply(self, func: Callable[[List[Any]], List[Any]]) -> "ColumnCollection":
        """各Columnに関数を適用
        Args:
            func: 適用する関数
        Returns:
            ColumnCollection: 新しいColumnCollection
        """
        new_columns = {}
        for name, column in self.columns.items():
            new_columns[name] = column.apply(func)
        # 適用後長さが揃っているか確認
        self.harmonize_length()
        # 新しいColumnCollectionを返す
        return ColumnCollection(
            step=self.step,
            columns=new_columns,
            metadata=self.metadata.copy(),
        )

    def auto_detect_column_types(self) -> "ColumnCollection":
        """各カラムのデータ型を自動判定し、適切な型のカラムに変換する

        Returns:
            self: メソッドチェーン用
        """
        for name, column in list(self.columns.items()):
            # 各カラムの型を自動判定
            new_column = detect_column_type(
                column.ch, column.name, column.unit, column.values, column.metadata
            )
            # 元のカラムと新しいカラムの型が異なる場合のみ置き換え
            if type(new_column) != type(column):
                self.columns[name] = new_column
        return self

    @classmethod
    def from_file(
        cls,
        filepath: Union[str, Path],
        format_name: str = "tasc_txt",
        auto_detect_types=False,
        **kwargs,
    ) -> "ColumnCollection":
        """ファイルからColumnCollectionを作成する

        Args:
            filepath: 読み込むファイルパス
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc_txt"）
            auto_detect_types: カラム型を自動判定するかどうか
            **kwargs: フォーマット設定を上書きするためのキーワード引数

        Returns:
            ColumnCollection: 読み込んだデータを含む新しいColumnCollectionオブジェクト

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            KeyError: 指定されたフォーマット名が登録されていない場合
        """
        from ..io.file_io import load_collection
        return load_collection(
            filepath, 
            format_name=format_name, 
            auto_detect_types=auto_detect_types, 
            collection_cls=cls,
            **kwargs
        )

    @classmethod
    def from_stream(
        cls,
        file_stream: TextIO,
        format_name: str = "tasc_txt",
        auto_detect_types=False,
        **kwargs,
    ) -> "ColumnCollection":
        """テキストストリームからColumnCollectionを作成する

        Args:
            file_stream: 読み込むテキストストリーム
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc_txt"）
            auto_detect_types: カラム型を自動判定するかどうか
            **kwargs: フォーマット設定を上書きするためのキーワード引数
                selected_columns: 読み込む列名またはチャンネル名のリスト。指定された列のみ読み込む

        Returns:
            ColumnCollection: 読み込んだデータを含む新しいColumnCollectionオブジェクト

        Raises:
            KeyError: 指定されたフォーマット名が登録されていない場合
        """
        from ..io.file_io import load_collection
        return load_collection(
            file_stream, 
            format_name=format_name, 
            auto_detect_types=auto_detect_types, 
            collection_cls=cls,
            **kwargs
        )

    def to_file(
        self, output_path: Union[str, Path], format_name: str = "tasc_txt", **kwargs
    ) -> None:
        """ColumnCollectionをファイルに出力する

        Args:
            output_path: 出力先ファイルパス
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc_txt"）
            **kwargs: フォーマット設定を上書きするためのキーワード引数

        Raises:
            KeyError: 指定されたフォーマット名が登録されていない場合
        """
        from ..io.file_io import save_collection
        save_collection(
            self, 
            output_path, 
            format_name=format_name, 
            **kwargs
        )

    def to_csv(self, path: Union[str, Path], **kwargs) -> None:
        """CSVファイルに保存
        
        Args:
            path: 出力先パス
            **kwargs: to_fileに渡す引数
        """
        # CSVフォーマットがサポートされているか確認し、なければ簡易実装
        try:
            self.to_file(path, format_name="csv", **kwargs)
        except (KeyError, ValueError):
            # 簡易実装
            import pandas as pd
            
            data = {}
            # Stepを追加
            data["Step"] = self.step.values
            
            # Columnを追加
            for name, col in self.columns.items():
                data[name] = col.values
                
            df = pd.DataFrame(data)
            df.to_csv(path, index=False, **kwargs)

    @property
    def steps(self) -> List[Any]:
        """step.valuesのエイリアス"""
        return self.step.values

    @property
    def date(self) -> List[str]:
        """日付リスト取得"""
        return self.metadata.get("date", [""] * len(self.step))

    @property
    def time(self) -> List[str]:
        """時間リスト取得"""
        return self.metadata.get("time", [""] * len(self.step))

    def get_date_time(self) -> tuple:
        """日付と時間のタプルを取得"""
        return self.date, self.time

    def find_nearest_step(self, value: Any) -> tuple[int, Any]:
        """指定した値に最も近いステップのインデックスと値を返す
        
        Args:
            value: 検索するステップ値
            
        Returns:
            tuple: (インデックス, ステップ値)
                   見つからない場合は (-1, None)
        """
        idx = self.step.find_nearest_index(value)
        if idx == -1:
            return -1, None
        return idx, self.step.values[idx]

    def max(self) -> Dict[str, Any]:
        """各列の最大値を取得"""
        return {name: col.max() for name, col in self.columns.items()}

    def min(self) -> Dict[str, Any]:
        """各列の最小値を取得"""
        return {name: col.min() for name, col in self.columns.items()}

    def mean(self) -> Dict[str, Optional[float]]:
        """各列の平均値を取得"""
        return {name: col.mean() for name, col in self.columns.items()}

    def ptp(self) -> Dict[str, Any]:
        """各列の最大値と最小値の差を取得"""
        return {name: col.ptp() for name, col in self.columns.items()}
    
    def first_valid_index(self) -> Dict[str, Optional[int]]:
        """各列の最初の有効なインデックスを取得"""
        return {name: col.first_valid_index for name, col in self.columns.items()}

    def first_invalid_index(self) -> Dict[str, Optional[int]]:
        """各列の最初の無効なインデックスを取得"""
        return {name: col.first_invalid_index for name, col in self.columns.items()}

    def to_numeric(self, errors: str = "raise") -> "ColumnCollection":
        """全列を数値列に変換を試みる（新しいCollectionを返す）"""
        new_columns = {}
        for name, col in self.columns.items():
            new_columns[name] = col.to_numeric(errors=errors)
        
        return ColumnCollection(
            step=self.step.clone(),
            columns=new_columns,
            metadata=deepcopy(self.metadata)
        )
