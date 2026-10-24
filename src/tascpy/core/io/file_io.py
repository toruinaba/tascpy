"""TASC 系テキスト形式の読み込み・保存

テキスト形式では単位の None（不明）と ""（無次元）を区別できず、どちらも空欄になります。
また文字列値の "none" や "*" で始まる値は読み込み時に欠損として扱われます。
単位・属性・解析結果まで含めて保存したい場合は Parquet（`save_parquet`）を使ってください。
"""

import csv
import io
import os
import tempfile
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, TextIO, Union

import polars as pl

from ..collection import INDEX_COLUMNS, ColumnCollection
from ..column import Column
from .formats import get_format

MISSING_TOKENS = ("none", "null", "", "nan", "na")


def load_collection(
    filepath_or_stream: Union[str, Path, TextIO],
    format_name: str = "tasc_txt",
    selected_columns: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> ColumnCollection:
    """ファイルまたはストリームから ColumnCollection を作成する

    ヘッダーのチャンネル行・名前行・単位行を列メタ（ch / 列名 / unit）に、
    日付・時刻列をインデックス列 date / time に読み込みます。

    - 単位が空欄の列の単位は None（不明）
    - 名前が空欄の列はチャンネル名、それもなければ "column{列番号}" を列名にする
    - 列名の重複や予約名（step / date / time）は "_2" などの接尾辞を付けて警告する
    - 欠損表記（none / null / nan / na / 空欄）と "*" で始まる値は欠損
    - step は整数・小数・日時・文字列のいずれかとして読み込む（空欄は欠損）

    Args:
        filepath_or_stream: 読み込むファイルパスまたはストリーム
        format_name: ファイルフォーマット名（デフォルト: "tasc_txt"）
        selected_columns: 読み込む列名またはチャンネル名（省略時は全列）
        **kwargs: フォーマット設定の上書き（encoding, delimiter, ch_row, name_row, unit_row,
            data_start_row, data_start_col, step_col, date_col, time_col）

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        KeyError: selected_columns にヘッダーにない名前が含まれる場合

    Examples:
        >>> from tascpy.core.io.file_io import load_collection
        >>> loaded = load_collection("data.txt", format_name="tasc_txt")
        >>> loaded.columns, loaded["荷重"].unit
        (['荷重', '変位', 'CH1', 'CH2', 'CH3', '状態'], 'kN')
    """
    config = {**get_format(format_name), **kwargs}
    if not isinstance(filepath_or_stream, (str, Path)):
        return _parse(filepath_or_stream.read(), config, format_name, selected_columns,
                      source=getattr(filepath_or_stream, "name", None))
    path = Path(filepath_or_stream)
    if not path.exists():
        raise FileNotFoundError(f"ファイル '{path}' が見つかりません")
    text = path.read_text(encoding=config["encoding"])
    return _parse(text, config, format_name, selected_columns, source=str(path))


def load_from_stream(stream: TextIO, format_name: str = "tasc_txt",
                     selected_columns: Optional[Sequence[str]] = None, **kwargs: Any) -> ColumnCollection:
    """ストリームから ColumnCollection を作成する（引数は load_collection と同じ）"""
    return load_collection(stream, format_name, selected_columns, **kwargs)


def _header_row(lines: List[str], index: Optional[int], delimiter: str, start: int) -> List[str]:
    if index is None or index >= len(lines):
        return []
    fields = next(csv.reader([lines[index]], delimiter=delimiter), [])
    return [f.strip() for f in fields[start:]]


def _unique_names(names: List[str]) -> List[str]:
    taken: set[str] = set(INDEX_COLUMNS)
    result = []
    for name in names:
        unique, n = name, 1
        while unique in taken:
            n += 1
            unique = f"{name}_{n}"
        if unique != name:
            warnings.warn(f"列名 '{name}' が重複しているか予約名のため '{unique}' に変更しました", stacklevel=4)
        taken.add(unique)
        result.append(unique)
    return result


def _cleaned(name: str) -> pl.Expr:
    value = pl.col(name).str.strip_chars()
    missing = value.is_null() | value.str.to_lowercase().is_in(MISSING_TOKENS) | value.str.starts_with("*")
    return pl.when(missing).then(None).otherwise(value).alias(name)


def _typed_values(series: pl.Series) -> pl.Series:
    """文字列の Series を数値・真偽値・文字列のいずれかに変換する"""
    present = series.drop_nulls()
    numbers = series.cast(pl.Float64, strict=False)
    if numbers.null_count() == series.null_count():
        return numbers
    if present.str.to_lowercase().is_in(["true", "false"]).all():
        return series.str.to_lowercase() == "true"
    return series


def _typed_step(series: pl.Series) -> pl.Series:
    """step を整数・小数・日時・文字列のいずれかに変換する"""
    for dtype in (pl.Int64, pl.Float64):
        converted = series.cast(dtype, strict=False)
        if converted.null_count() == series.null_count():
            return converted
    try:
        dates = series.str.to_datetime(strict=False)
    except pl.exceptions.ComputeError:
        return series
    return dates if dates.null_count() == series.null_count() else series


def _parse(text: str, config: Dict[str, Any], format_name: str,
           selected_columns: Optional[Sequence[str]], source: Optional[str]) -> ColumnCollection:
    lines = text.splitlines()
    delimiter = config["delimiter"]
    start = config["data_start_col"]
    metadata = {"format": format_name, "source": source}

    chs = _header_row(lines, config["ch_row"], delimiter, start)
    names = _header_row(lines, config["name_row"], delimiter, start)
    units = _header_row(lines, config["unit_row"], delimiter, start)
    width = max(len(chs), len(names), len(units))
    chs, names, units = ([*row, *[""] * (width - len(row))] for row in (chs, names, units))
    names = _unique_names([name or ch or f"column{start + i}" for i, (name, ch) in enumerate(zip(names, chs))])

    picked = list(range(width))
    if selected_columns is not None:
        unknown = [s for s in selected_columns if s not in names and s not in chs]
        if unknown:
            raise KeyError(f"指定された列が見つかりません: {unknown}")
        picked = [i for i in picked if names[i] in selected_columns or chs[i] in selected_columns]

    body = [line for line in lines[config["data_start_row"]:] if line.strip()]
    index_cols = {"step": config["step_col"], "date": config["date_col"], "time": config["time_col"]}
    n_fields = max([start + width] + [c + 1 for c in index_cols.values() if c is not None])
    raw = pl.read_csv(
        "\n".join(body).encode("utf-8"), separator=delimiter, has_header=False,
        schema={f"f{i}": pl.String for i in range(n_fields)}, missing_columns="insert", extra_columns="ignore",
        truncate_ragged_lines=True,
    ) if body else pl.DataFrame(schema={f"f{i}": pl.String for i in range(n_fields)})
    raw = raw.select(_cleaned(c) for c in raw.columns)

    columns = {
        names[i]: Column(names[i], _typed_values(raw[f"f{start + i}"]), unit=units[i] or None, ch=chs[i] or None)
        for i in picked
    }
    index = {key: raw[f"f{col}"] for key, col in index_cols.items() if col is not None}
    step = _typed_step(index["step"]) if "step" in index else None
    date, time = (index[k] if k in index and index[k].null_count() < len(raw) else None for k in ("date", "time"))
    return ColumnCollection(columns, step=step, date=date, time=time, metadata=metadata)


def save_collection(
    collection: ColumnCollection,
    output_path: Union[str, Path],
    format_name: str = "tasc_txt",
    *,
    encoding: Optional[str] = None,
    delimiter: Optional[str] = None,
) -> None:
    """ColumnCollection をテキスト形式で保存する

    標準レイアウト（1行目 "DATA"、チャンネル行・名前行・単位行の後にデータ行）で書き出します。
    名前行には列名、チャンネル行には ch（未設定なら空欄）を書くため、保存→読み込みで列名と ch が保たれます。
    書き込みは全体をエンコードしてから一時ファイル経由で行うため、失敗しても既存ファイルは変更されません。

    Args:
        collection: 保存するコレクション
        output_path: 出力先ファイルパス
        format_name: ファイルフォーマット名（デフォルト: "tasc_txt"）
        encoding: エンコーディングの上書き（tasc_txt / tasc_csv の既定は shift_jis）
        delimiter: 区切り文字の上書き

    Raises:
        ValueError: 列名・単位などに、指定エンコーディングで表せない文字がある場合
    """
    config = get_format(format_name)
    encoding_: str = encoding or config["encoding"]
    delimiter_: str = delimiter or config["delimiter"]

    names = collection.columns
    meta = collection.meta
    header = io.StringIO()
    writer = csv.writer(header, delimiter=delimiter_, lineterminator="\n")
    writer.writerows([
        ["DATA"],
        ["CH", "DATE", "TIME", *[meta[n].ch or "" for n in names]],
        ["NAME", "DATE", "TIME", *names],
        ["UNIT", "", "", *[meta[n].unit or "" for n in names]],
    ])

    df = collection.df
    blank = pl.lit("")
    body = df.select(
        pl.col("step").cast(pl.String),
        pl.col("date").cast(pl.String).fill_null("") if "date" in df.columns else blank.alias("date"),
        pl.col("time").cast(pl.String).fill_null("") if "time" in df.columns else blank.alias("time"),
        *[pl.col(n).cast(pl.String).str.to_lowercase() if df[n].dtype == pl.Boolean else pl.col(n)
          for n in names],
    ).write_csv(separator=delimiter_, include_header=False, null_value="none", line_terminator="\n")

    try:
        data = (header.getvalue() + body).encode(encoding_)
    except UnicodeEncodeError as e:
        raise ValueError(
            f"{encoding_} で表せない文字 {e.object[e.start:e.end]!r} が含まれています。"
            f"encoding='utf-8' を指定するか、列名・単位を変更してください"
        ) from e
    _write_atomic(Path(output_path), data)


def _default_mode() -> int:
    umask = os.umask(0)
    os.umask(umask)
    return 0o666 & ~umask


def _write_atomic(path: Path, data: bytes) -> None:
    """一時ファイルに書いてから置き換える（失敗時は既存ファイルを変更しない、権限は既存ファイルに合わせる）"""
    mode = path.stat().st_mode & 0o777 if path.exists() else _default_mode()
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise
