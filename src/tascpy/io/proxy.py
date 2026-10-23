from typing import Union, Any, Optional
from pathlib import Path

class CollectionIO:
    """IO機能をColumnCollectionに提供するアクセサクラス

    `ColumnCollection.io` から利用します。
    
    >>> collection = tascpy.io.load("data.csv")
    >>> collection.io.save("out.csv")
    """
    def __init__(self, collection: Any):
        self._collection = collection

    def save(self, output_path: Union[str, Path], format_name: str = "tasc_txt", **kwargs) -> None:
        """データをファイルに保存する
        
        Args:
            output_path: 出力先ファイルパス
            format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc_txt"）
            **kwargs: フォーマット設定を上書きするためのキーワード引数。
                以下のパラメータが指定可能です：
                - encoding (str): 文字エンコーディング（例: "utf-8", "shift_jis"）
                - delimiter (str): 区切り文字
                - use_channel_name (bool): 列名ではなくチャンネル名をヘッダーに用いるか
                
        Examples:
            >>> col.io.save("processed_data.txt", format_name="tasc_txt")
        """
        from .file_io import save_collection
        save_collection(
            self._collection,
            output_path,
            format_name=format_name,
            **kwargs
        )

    def to_csv(self, path: Union[str, Path], **kwargs) -> None:
        """データをCSV形式でファイルに保存する
        
        Args:
            path: 出力先パス
            **kwargs: save メソッドに渡す引数（delimiter, encoding など）

        Examples:
            >>> col.io.to_csv("processed_data.csv")
        """
        self.save(path, format_name="csv", **kwargs)
