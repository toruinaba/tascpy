from typing import Union, TextIO, List, Any, Optional, TYPE_CHECKING
from pathlib import Path
from .formats import get_format
from ..core.step import Step
from ..core.column import Column, detect_column_type

if TYPE_CHECKING:
    from ..core.collection import ColumnCollection

def load_collection(
    filepath_or_stream: Union[str, Path, TextIO],
    format_name: str = "tasc_txt",
    auto_detect_types: bool = False,
    collection_cls: Optional[Any] = None,
    **kwargs
) -> "ColumnCollection":
    """ファイルまたはストリームからColumnCollectionを作成する

    Args:
        filepath_or_stream: 読み込むファイルパスまたはストリーム
        format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc_txt"）
        auto_detect_types: カラム型を自動判定するかどうか
        collection_cls: 使用するColumnCollectionクラス（依存循環を防ぐため引数で受け取る）
        **kwargs: フォーマット設定を上書きするためのキーワード引数。
            以下のパラメータが使用可能です：
            - encoding (str): 文字エンコーディング（例: "utf-8", "shift_jis"）
            - delimiter (str): 区切り文字
            - ch_row (int): チャンネル文字の行位置 (0-indexed)
            - name_row (int): 名前文字の行位置 (0-indexed)
            - unit_row (int): 単位文字の行位置 (0-indexed)
            - data_start_row (int): データ開始行 (0-indexed)
            - data_start_col (int): データ開始列 (0-indexed)
            - step_col (int): ステップ列のインデックス (0-indexed)
            - selected_columns (list[str]): 読み込むカラム/チャンネル名のリスト。指定した列のみ読み込みます。

    Returns:
        ColumnCollection: 読み込んだデータを含む新しいColumnCollectionオブジェクト
    """
    # 循環インポートを避けるため、ここでインポートするか引数で受け取る
    if collection_cls is None:
        from ..core.collection import ColumnCollection
        collection_cls = ColumnCollection

    if isinstance(filepath_or_stream, (str, Path)):
        return _load_from_file(filepath_or_stream, format_name, auto_detect_types, collection_cls, **kwargs)
    else:
        return _load_from_stream(filepath_or_stream, format_name, auto_detect_types, collection_cls, **kwargs)

def _load_from_file(
    filepath: Union[str, Path],
    format_name: str,
    auto_detect_types: bool,
    collection_cls: Any,
    **kwargs
) -> "ColumnCollection":
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
        collection = _load_from_stream(f, format_name, auto_detect_types, collection_cls, **kwargs)
        
        # ファイルソース情報を追加
        collection.metadata["source"] = str(filepath)
        
        return collection

def _load_from_stream(
    file_stream: TextIO,
    format_name: str,
    auto_detect_types: bool,
    collection_cls: Any,
    **kwargs
) -> "ColumnCollection":
    # フォーマット設定を取得して上書き
    format_config = get_format(format_name).copy()
    format_config.update(
        {k: v for k, v in kwargs.items() if k != "selected_columns"}
    )

    # 特定の列だけを選択する場合の処理
    selected_columns = kwargs.get("selected_columns", None)

    # ファイル内容を行単位で読み込み
    all_lines = file_stream.readlines()
    rows = [line.rstrip('\r\n') for line in all_lines]

    # フォーマット設定から行と列のインデックスを取得
    delimiter = format_config["delimiter"]
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
        chs = _extract_row_values(rows[ch_row], delimiter, data_start_col)
    else:
        chs = []

    # 名前行が指定されていなければチャンネル行を使用
    if name_row is not None and name_row < len(rows):
        if name_row == ch_row:
            names = chs.copy()
        else:
            names = _extract_row_values(
                rows[name_row], delimiter, data_start_col, strip_quotes=True
            )
    else:
        names = chs.copy()

    # 単位を取得
    units = []
    if unit_row is not None and unit_row < len(rows):
        units = _extract_row_values(
            rows[unit_row], delimiter, data_start_col, strip_quotes=True
        )
    else:
        units = [""] * len(chs)

    # データ行がなければ空のコレクションを返す
    if data_start_row >= len(rows):
        return collection_cls([], {}, {"format": format_name})

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
        return collection_cls([], {}, {"format": format_name})

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
                value = _convert_value(cols[col_idx])
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
    collection = collection_cls(steps, columns, metadata)
    
    # 自動型の再判定（念のため）
    if auto_detect_types:
        collection.auto_detect_column_types()
        
    return collection

def save_collection(
    collection: "ColumnCollection",
    output_path: Union[str, Path],
    format_name: str = "tasc_txt",
    **kwargs
) -> None:
    """ColumnCollectionをファイルに出力する

    Args:
        collection: 出力するColumnCollection
        output_path: 出力先ファイルパス
        format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc_txt"）
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
    for name, column in collection.columns.items():
        ch = column.ch if hasattr(column, "ch") and column.ch else name
        ch_values.append(ch)
    ch_line = delimiter.join(ch_values)

    # 名称行を作成 - use_channel_name設定に基づいて処理
    name_values = ["NAME", "DATE", "TIME"]
    for name, column in collection.columns.items():
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
    for column in collection.columns.values():
        unit = column.unit if hasattr(column, "unit") and column.unit else ""
        unit_values.append(unit)
    unit_line = delimiter.join(unit_values)

    # データ行を作成
    data_lines = []
    for i, step_value in enumerate(collection.step.values):
        # 日付と時間の取得
        date = (
            collection.metadata.get("date", [""] * len(collection.step))[i]
            if "date" in collection.metadata
            else ""
        )
        time = (
            collection.metadata.get("time", [""] * len(collection.step))[i]
            if "time" in collection.metadata
            else ""
        )

        # 行の組み立て
        row_values = [str(step_value), date, time]
        for name in collection.columns:
            value = collection.columns[name].values[i]
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

def _extract_row_values(
    row: str, delimiter: str, start_col: int, strip_quotes: bool = False
) -> List[str]:
    """行から値を抽出する"""
    values = row.split(delimiter)[start_col:]
    if strip_quotes:
        values = [v.strip('"').strip("'") for v in values]
    return values

def _convert_value(value_str: str) -> Any:
    """文字列値を適切な型に変換する"""
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
