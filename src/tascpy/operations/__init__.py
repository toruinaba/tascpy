from .registry import operation, OperationRegistry

from .core import filters
from .core import math
from .core import search
from .core import plot
from .core import transform
from .core import interpolate
from .core import split
from .core import stats  # 統計処理機能を追加

# ドメイン特化モジュールのインポート
from . import coordinate  # 座標ドメインの操作
from . import load_displacement  # 荷重変位ドメインの操作

# スタブファイルの自動生成
import os

# 環境変数で制御可能にする（CI/CD 環境などでエラーにならないように）
if os.environ.get("TASCPY_GENERATE_STUBS", "1") == "1":
    try:
        OperationRegistry.generate_stubs()
    except Exception as e:
        import sys

        print(f"警告: スタブファイルの生成に失敗しました: {e}", file=sys.stderr)
