#!/usr/bin/env python
"""
tascpy のスタブファイル生成用スクリプト

このスクリプトを実行すると、operationsモジュールのスタブファイルが
src/tascpy/typing/ ディレクトリに生成されます。
これにより、動的に生成されるメソッドに対してPylanceの自動補完が機能するようになります。
"""

import sys
import os
import logging
from pathlib import Path

# ロギングの設定
logging.basicConfig(level=logging.INFO)

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    try:
        print("tascpy スタブファイルの生成を開始します...")

        # スタブ生成を実行
        try:
            # 先にレジストリをインポートして初期化
            from src.tascpy.operations.registry import OperationRegistry

            # ドメインを先に検出
            OperationRegistry.discover_domains()

            # スタブ生成を実行
            from src.tascpy.operations.stub_generator import generate_stubs

            generate_stubs()
        except ImportError as ie:
            print(f"インポートエラー: {ie}")
            # tascpyが通常のパッケージとしてインストールされている場合
            try:
                from tascpy.operations.registry import OperationRegistry

                OperationRegistry.discover_domains()

                from tascpy.operations.stub_generator import generate_stubs

                generate_stubs()
            except ImportError:
                raise ImportError("tascpyパッケージをインポートできませんでした")

        print("スタブファイルの生成が完了しました。")
        print("VS Code / Pylance で自動補完が機能するようになりました。")
        return 0
    except Exception as e:
        print(f"エラー: スタブファイルの生成に失敗しました: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
