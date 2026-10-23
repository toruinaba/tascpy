from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, TextIO, Union

from ..core.collection import ColumnCollection
from ..core.column import Column
from .formats import get_format

_MISSING_TOKENS = {"none", "null", "", "nan", "na"}


def load_collection(
    filepath_or_stream: Union[str, Path, TextIO],
    format_name: str = "tasc_txt",
    selected_columns: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> ColumnCollection:
    """ファイルまたはストリームから ColumnCollection を作成する

    ヘッダーのチャンネル行・名前行・単位行を列メタ（ch / 列名 / unit）に、
    日付・時刻列をインデックス列 date / time に読み込みます。
    単位が空欄の列の単位は None（不明）になります。

    Args:
        filepath_or_stream: 読み込むファイルパスまたはストリーム
        format_name: ファイルフォーマット名（デフォルト: "tasc_txt"）
        selected_columns: 読み込む列名またはチャンネル名（省略時は全列）
        **kwargs: フォーマット設定の上書き（encoding, delimiter, ch_row, name_row, unit_row,
            data_start_row, data_start_col, step_col, date_col, time_col）

    Examples:
        >>> col = load_collection("data.txt", format_name="tasc_txt")
    """
    config = {**get_format(format_name), **kwargs}
    if not isinstance(filepath_or_stream, (str, Path)):
        return _parse(filepath_or_stream.readlines(), config, format_name, selected_columns,
                      source=getattr(filepath_or_stream, "name", None))
    path = Path(filepath_or_stream)
    if not path.exists():
        raise FileNotFoundError(f"ファイル '{path}' が見つかりません")
    with open(path, "r", encoding=config.get("encoding", "utf-8")) as f:
        return _parse(f.readlines(), config, format_name, selected_columns, source=str(path))


def load_from_stream(stream: TextIO, format_name: str = "tasc_txt",
                     selected_columns: Optional[Sequence[str]] = None, **kwargs: Any) -> ColumnCollection:
    """ストリームから ColumnCollection を作成する（引数は load_collection と同じ）"""
    return load_collection(stream, format_name, selected_columns, **kwargs)


def _parse(lines: List[str], config: Dict[str, Any], format_name: str,
           selected_columns: Optional[Sequence[str]], source: Optional[str]) -> ColumnCollection:
    rows = [line.rstrip("\r\n") for line in lines]
    delimiter = config["delimiter"]
    start_col = config["data_start_col"]
    metadata = {"format": format_name, "source": source}

    def header(row_index: Optional[int], strip_quotes: bool = False) -> Optional[List[str]]:
        if row_index is None or row_index >= len(rows):
            return None
        values = rows[row_index].split(delimiter)[start_col:]
        return [v.strip('"').strip("'") for v in values] if strip_quotes else values

    chs = header(config["ch_row"]) or []
    names = header(config["name_row"], strip_quotes=True) or list(chs)
    units = header(config["unit_row"], strip_quotes=True) or [""] * len(chs)

    data_rows = [row.split(delimiter) for row in rows[config["data_start_row"]:]]
    if not data_rows:
        return ColumnCollection(metadata=metadata)

    def cell(cols: List[str], index: Optional[int]) -> str:
        return cols[index].strip() if index is not None and index < len(cols) else ""

    steps = [_parse_step(cell(cols, config["step_col"]), i + 1) for i, cols in enumerate(data_rows)]
    dates = [cell(cols, config["date_col"]) for cols in data_rows]
    times = [cell(cols, config["time_col"]) for cols in data_rows]

    columns = {}
    for i, (ch, name, unit) in enumerate(zip(chs, names, units)):
        if selected_columns is not None and name not in selected_columns and ch not in selected_columns:
            continue
        values = [_convert_value(cell(cols, start_col + i)) for cols in data_rows]
        columns[name] = Column(name, values, unit=unit or None, ch=ch or None)

    return ColumnCollection(
        columns, step=steps,
        date=dates if any(dates) else None,
        time=times if any(times) else None,
        metadata=metadata,
    )


def _parse_step(value: str, row_number: int) -> int:
    try:
        return int(value)
    except ValueError:
        return row_number


def _convert_value(value_str: str) -> Any:
    """文字列を値に変換する（欠損表記と "*" で始まる値は None）"""
    value_str = value_str.strip()
    lowered = value_str.lower()
    if lowered in _MISSING_TOKENS or value_str.startswith("*"):
        return None
    if lowered in ("true", "false"):
        return lowered == "true"
    try:
        return float(value_str)
    except ValueError:
        return value_str


def save_collection(
    collection: ColumnCollection,
    output_path: Union[str, Path],
    format_name: str = "tasc_txt",
    **kwargs: Any,
) -> None:
    """ColumnCollection をファイルに出力する

    Args:
        collection: 出力するコレクション
        output_path: 出力先ファイルパス
        format_name: ファイルフォーマット名（デフォルト: "tasc_txt"）
        **kwargs: フォーマット設定の上書き（delimiter, encoding, use_channel_name）
    """
    config = {**get_format(format_name), **kwargs}
    delimiter = config["delimiter"]
    use_channel_name = config.get("use_channel_name", False)

    names = collection.columns
    meta = collection.meta
    ch_line = ["CH", "DATE", "TIME"] + [meta[n].ch or n for n in names]
    name_line = ["NAME", "DATE", "TIME"] + [(meta[n].ch or n) if use_channel_name else n for n in names]
    unit_line = ["UNIT", "", ""] + [meta[n].unit or "" for n in names]

    n_rows = len(collection)
    dates = collection.date if collection.date is not None else [""] * n_rows
    times = collection.time if collection.time is not None else [""] * n_rows
    data_lines = []
    for row, date, time in zip(collection.iter_rows(), dates, times):
        values = [_format_value(row[n]) for n in names]
        data_lines.append(delimiter.join([str(row.step), date or "", time or "", *values]))

    with open(Path(output_path), "w", encoding=config.get("encoding", "utf-8")) as f:
        f.write("DATA\n")
        for line in (ch_line, name_line, unit_line):
            f.write(delimiter.join(line) + "\n")
        f.write("\n".join(data_lines))


def _format_value(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
