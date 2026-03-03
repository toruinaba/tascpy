from typing import Union, Any, Optional
from pathlib import Path

class CollectionIO:
    """IO機能をColumnCollectionに提供するアクセサクラス

    このクラスは ColumnCollection.register_accessor("io", CollectionIO) 
    を通じて登録され、以下のように使用されます。
    
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
            **kwargs: saveメソッドまたはpandas.DataFrame.to_csvに渡す引数。
                - delimiter, encoding 等が指定可能です。
        """
        try:
            self.save(path, format_name="csv", **kwargs)
        except (KeyError, ValueError):
            import pandas as pd
            
            data = {}
            data["Step"] = self._collection.step.values
            for name, col in self._collection.columns.items():
                data[name] = col.values
                
            df = pd.DataFrame(data)
            df.to_csv(path, index=False, **kwargs)
