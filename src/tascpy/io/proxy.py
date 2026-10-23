from pathlib import Path
from typing import Any, Optional, Union


class CollectionIO:
    """`ColumnCollection.io` から使うファイル保存のアクセサ

    | メソッド | 形式 | 保持される情報 |
    |---|---|---|
    | `save` | TASC 系テキスト（4行ヘッダー） | 列名・ch・単位（None と "" は区別しない） |
    | `to_parquet` | Parquet | 列メタ・メタデータ・解析結果・ドメイン設定すべて |
    | `to_csv` | 一般的な CSV（1行ヘッダー） | 列名のみ |

    Examples:
        >>> col.io.save("processed.txt")
        >>> col.io.to_parquet("processed.parquet")
    """

    def __init__(self, collection: Any):
        self._collection = collection

    def save(self, output_path: Union[str, Path], format_name: str = "tasc_txt", *,
             encoding: Optional[str] = None, delimiter: Optional[str] = None) -> None:
        """TASC 系テキスト形式で保存する

        Args:
            output_path: 出力先ファイルパス
            format_name: ファイルフォーマット名（デフォルト: "tasc_txt"）
            encoding: エンコーディングの上書き（tasc_txt / tasc_csv の既定は shift_jis）
            delimiter: 区切り文字の上書き

        Examples:
            >>> col.io.save("processed_data.txt", encoding="utf-8")
        """
        from .file_io import save_collection

        save_collection(self._collection, output_path, format_name=format_name,
                        encoding=encoding, delimiter=delimiter)

    def to_parquet(self, path: Union[str, Path]) -> None:
        """列メタ・メタデータ・解析結果まで含めて Parquet 形式で保存する（`tascpy.io.load_parquet` で復元）"""
        from .parquet import save_parquet

        save_parquet(self._collection, path)

    def to_csv(self, path: Union[str, Path], separator: str = ",") -> None:
        """インデックス列とデータ列を、1行ヘッダーの一般的な CSV（UTF-8）として保存する

        単位などの列メタは保存されません。
        """
        self._collection.df.write_csv(path, separator=separator)
