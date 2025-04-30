import codecs
from pathlib import Path
from typing import Union

class Reader:
    """タスク出力ファイル読み込み用クラス

    with文でタスクファイルを読み込むことを想定
    :param path: ファイルパス
    """
    def __init__(self, path: Union[Path, str]):
        if isinstance(path, str):
            self.path = Path(path)
        elif isinstance(path, Path):
            self.path = path
        else:
            raise ValueError("ファイルパスはpathlibオブジェクトまたはstrで指定してください.")

    def __enter__(self, encoding="shift-jis"):
        self.io = codecs.open(self.path, "r", encoding)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.io.close()
        if exc_type is not None:
            print(exc_type)