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
    from ..operations.stubs.core import CoreCollectionOperations

T = TypeVar("T")


class ColumnCollection:
    """複数のcollumnと一つのstepを保持するクラス"""

    domain = "core"

    def __init__(self, step, columns, metadata=None, auto_detect_types=False):
        """
        Args:
            step: Stepオブジェクトまたはステップ値のリスト
            columns: {名前: Column}の辞書または{名前: 値リスト}の辞書
            metadata: メタデータの辞書
            auto_detect_types: カラム型を自動判定するかどうか
        """
        # ステップの初期化
        if isinstance(step, Step):
            self.step = step
        else:
            self.step = Step(values=step if step is not None else [])

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

    def __getitem__(self, key):
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
            metadata=self.metadata.copy(),
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
            from ..operations.stubs.core import CoreCollectionOperations

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

    def describe(self) -> Dict[str, Dict[str, Any]]:
        """データの概要を取得
        Returns:
            辞書: 各列の統計情報を含む辞書
        """
        stats = {}
        for name, column in self.columns.items():
            # columnが数値の場合は統計情報を計算
            if isinstance(column.values, (list, tuple)):
                stats[name] = {
                    "count": len(column.values),
                    "mean": sum(column.values) / len(column.values),
                    "min": min(column.values),
                    "max": max(column.values),
                }
            else:
                stats[name] = {"count": len(column.values)}
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
        format_name: str = "tasc",
        auto_detect_types=False,
        **kwargs,
    ) -> "ColumnCollection":
        """ファイルからColumnCollectionを作成する

        Args:
            filepath: 読み込むファイルパス
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc"）
            auto_detect_types: カラム型を自動判定するかどうか
            **kwargs: フォーマット設定を上書きするためのキーワード引数

        Returns:
            ColumnCollection: 読み込んだデータを含む新しいColumnCollectionオブジェクト

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            KeyError: 指定されたフォーマット名が登録されていない場合
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"ファイル '{filepath}' が見つかりません")

        # フォーマット設定を取得して上書き
        format_config = get_format(format_name).copy()
        format_config.update(kwargs)

        # エンコーディングを取得（デフォルトはUTF-8）
        encoding = format_config.get("encoding", "utf-8")

        with open(filepath, "r", encoding=encoding) as f:
            collection = cls.from_stream(f, format_name, **kwargs)

            # 自動判定が有効な場合は各カラムの型を判定
            if auto_detect_types:
                collection.auto_detect_column_types()

            return collection

    @classmethod
    def from_stream(
        cls,
        file_stream: TextIO,
        format_name: str = "tasc",
        auto_detect_types=False,
        **kwargs,
    ) -> "ColumnCollection":
        """テキストストリームからColumnCollectionを作成する

        Args:
            file_stream: 読み込むテキストストリーム
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc"）
            auto_detect_types: カラム型を自動判定するかどうか
            **kwargs: フォーマット設定を上書きするためのキーワード引数
                selected_columns: 読み込む列名またはチャンネル名のリスト。指定された列のみ読み込む

        Returns:
            ColumnCollection: 読み込んだデータを含む新しいColumnCollectionオブジェクト

        Raises:
            KeyError: 指定されたフォーマット名が登録されていない場合
        """
        # フォーマット設定を取得して上書き
        format_config = get_format(format_name).copy()
        format_config.update(
            {k: v for k, v in kwargs.items() if k != "selected_columns"}
        )

        # 特定の列だけを選択する場合の処理
        selected_columns = kwargs.get("selected_columns", None)

        # ファイル内容を行単位で読み込み
        all_lines = file_stream.readlines()
        rows = [line.rstrip() for line in all_lines]

        # フォーマット設定から行と列のインデックスを取得
        delimiter = format_config["delimiter"]
        title_row = format_config.get("title_row", None)
        ch_row = format_config["ch_row"]
        name_row = format_config["name_row"]
        unit_row = format_config["unit_row"]
        data_start_row = format_config["data_start_row"]
        step_col = format_config["step_col"]
        date_col = format_config["date_col"]
        time_col = format_config["time_col"]
        data_start_col = format_config["data_start_col"]

        # チャンネル、名前、単位を抽出
        if ch_row < len(rows):
            chs = cls._extract_row_values(rows[ch_row], delimiter, data_start_col)
        else:
            chs = []

        # 名前行が指定されていなければチャンネル行を使用
        if name_row is not None and name_row < len(rows):
            if name_row == ch_row:
                names = chs.copy()
            else:
                names = cls._extract_row_values(
                    rows[name_row], delimiter, data_start_col, strip_quotes=True
                )
        else:
            names = chs.copy()

        # 単位を取得
        units = []
        if unit_row is not None and unit_row < len(rows):
            units = cls._extract_row_values(
                rows[unit_row], delimiter, data_start_col, strip_quotes=True
            )
        else:
            units = [""] * len(chs)

        # データ行がなければエラーを回避
        if data_start_row >= len(rows):
            return cls([], {}, {"format": format_name})

        # データ行のみを対象とする
        data_rows = rows[data_start_row:]

        # ステップ、日付、時間データを抽出
        steps = []
        dates = []
        times = []

        # データ行を処理
        for row_idx, row in enumerate(data_rows):
            cols = row.split(delimiter)

            # ステップデータを抽出
            if len(cols) > step_col:
                try:
                    step_val = cols[step_col].strip()
                    if step_val.lower() in ("none", "null", ""):
                        steps.append(row_idx + 1)  # Noneの場合は行番号を使用
                    else:
                        steps.append(int(step_val))
                except (ValueError, IndexError):
                    steps.append(row_idx + 1)  # 変換に失敗した場合も行番号を使用
            else:
                steps.append(row_idx + 1)  # 列がない場合も行番号を使用

            # 日付データを抽出
            if date_col is not None and len(cols) > date_col:
                date_val = cols[date_col].strip()
                dates.append(date_val)
            else:
                dates.append("")

            # 時間データを抽出
            if time_col is not None and len(cols) > time_col:
                time_val = cols[time_col].strip()
                times.append(time_val)
            else:
                times.append("")

        # データが取得できたか確認
        if not steps:
            return cls([], {}, {"format": format_name})

        # 各列のデータを抽出
        columns = {}
        for i, (ch, name, unit) in enumerate(zip(chs, names, units)):
            # 特定の列だけを読み込む場合の処理
            if selected_columns is not None:
                # 列名もチャンネル名も選択リストにない場合はスキップ
                if name not in selected_columns and ch not in selected_columns:
                    continue  # 指定されていない列はスキップ

            col_idx = data_start_col + i
            values = []

            for row in data_rows:
                cols = row.split(delimiter)
                if col_idx < len(cols):
                    value = cls._convert_value(cols[col_idx])
                    values.append(value)
                else:
                    values.append(None)

            # 自動判定が有効な場合は適切なカラム型を選択
            if auto_detect_types:
                columns[name] = detect_column_type(ch, name, unit, values)
            else:
                columns[name] = Column(ch, name, unit, values)

        # メタデータを作成
        metadata = {
            "format": format_name,
            "source": getattr(file_stream, "name", None),
        }

        # 日付と時間のメタデータを追加
        # 空文字列のみの場合は追加しない
        if any(date for date in dates if date):
            metadata["date"] = dates
        if any(time for time in times if time):
            metadata["time"] = times

        # ColumnCollectionを作成して返す
        return cls(steps, columns, metadata)

    @staticmethod
    def _extract_row_values(
        row: str, delimiter: str, start_col: int, strip_quotes: bool = False
    ) -> List[str]:
        """行から値を抽出する

        Args:
            row: 処理する行
            delimiter: 区切り文字
            start_col: 抽出開始列インデックス
            strip_quotes: 引用符を削除するかどうか

        Returns:
            抽出された値のリスト
        """
        values = row.split(delimiter)[start_col:]
        if strip_quotes:
            values = [v.strip('"').strip("'") for v in values]
        return values

    @staticmethod
    def _convert_value(value_str: str) -> Any:
        """文字列値を適切な型に変換する

        Args:
            value_str: 変換する文字列値

        Returns:
            変換された値
        """
        value_str = value_str.strip()

        # None判定（大文字小文字を区別しない）
        if value_str.lower() in ("none", "null", "", "nan", "*******"):
            return None

        # ブール値判定
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # 数値判定
        try:
            # 整数判定
            if value_str.isdigit():
                return int(value_str)
            # 浮動小数点数判定
            return float(value_str)
        except ValueError:
            # その他は文字列として扱う
            return value_str

    def to_file(
        self, output_path: Union[str, Path], format_name: str = "tasc", **kwargs
    ) -> None:
        """ColumnCollectionをファイルに出力する

        Args:
            output_path: 出力先ファイルパス
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc"）
            **kwargs: フォーマット設定を上書きするためのキーワード引数

        Raises:
            KeyError: 指定されたフォーマット名が登録されていない場合
        """
        # フォーマット設定を取得して上書き
        format_config = get_format(format_name).copy()
        format_config.update(kwargs)

        if isinstance(output_path, str):
            output_path = Path(output_path)

        delimiter = format_config["delimiter"]
        # エンコーディングを取得（デフォルトはUTF-8）
        encoding = format_config.get("encoding", "utf-8")
        # チャンネル名を使用するかどうかを取得
        use_channel_name = format_config.get("use_channel_name", False)

        # ヘッダー行を作成
        title_line = "DATA"

        # チャンネル行を作成
        ch_values = ["CH", "DATE", "TIME"]
        for name, column in self.columns.items():
            ch = column.ch if hasattr(column, "ch") and column.ch else name
            ch_values.append(ch)
        ch_line = delimiter.join(ch_values)

        # 名称行を作成 - use_channel_name設定に基づいて処理
        name_values = ["NAME", "DATE", "TIME"]
        for name, column in self.columns.items():
            if use_channel_name:
                # チャンネル名を使用
                display_name = (
                    column.ch if hasattr(column, "ch") and column.ch else name
                )
            else:
                # 列名を使用
                display_name = name
            name_values.append(display_name)
        name_line = delimiter.join(name_values)

        # 単位行を作成
        unit_values = ["UNIT", "", ""]
        for column in self.columns.values():
            unit = column.unit if hasattr(column, "unit") and column.unit else ""
            unit_values.append(unit)
        unit_line = delimiter.join(unit_values)

        # データ行を作成
        data_lines = []
        for i, step_value in enumerate(self.step.values):
            # 日付と時間の取得
            date = (
                self.metadata.get("date", [""] * len(self.step))[i]
                if "date" in self.metadata
                else ""
            )
            time = (
                self.metadata.get("time", [""] * len(self.step))[i]
                if "time" in self.metadata
                else ""
            )

            # 行の組み立て
            row_values = [str(step_value), date, time]
            for name in self.columns:
                value = self.columns[name].values[i]
                if value is None:
                    row_values.append("none")
                elif isinstance(value, bool):
                    row_values.append(str(value).lower())
                else:
                    row_values.append(str(value))

            data_lines.append(delimiter.join(row_values))

        # ファイルに書き込み（指定されたエンコーディングを使用）
        with open(output_path, "w", encoding=encoding) as f:
            f.write(title_line + "\n")
            f.write(ch_line + "\n")
            f.write(name_line + "\n")
            f.write(unit_line + "\n")
            f.write("\n".join(data_lines))

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
