"""
stub_generator.pyのテスト
"""

import os
import sys
import shutil
from pathlib import Path
import unittest
import tempfile
from typing import List

from tascpy.operations.stub_generator import generate_stubs
from tascpy.operations.registry import OperationRegistry


class TestStubGenerator(unittest.TestCase):
    """スタブ生成のテスト"""

    def setUp(self):
        """テストの準備"""
        # 一時ディレクトリをセットアップ
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        # 元のtypingディレクトリパスをバックアップ
        self.original_typing_dir = Path(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ) / "src" / "tascpy" / "typing"

    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.temp_dir.cleanup()

    def _get_operations_in_stub(self, stub_path: Path) -> List[str]:
        """スタブファイルから操作メソッド名のリストを取得"""
        operations = []
        # ファイルの存在を確認
        if not stub_path.exists():
            print(f"警告: スタブファイル {stub_path} が存在しません")
            return operations
            
        with open(stub_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    # 操作メソッド名を抽出 (def method_name(...) -> ...)
                    method_name = line.strip().split("(")[0].split()[1]
                    operations.append(method_name)
        return operations

    def test_domain_stubs_include_core_operations(self):
        """非coreドメインのスタブファイルにcoreのメソッドが含まれることを確認"""
        # 正しいtypingディレクトリのパスを取得
        typing_dir = Path(__file__).parent.parent.parent.parent / "src" / "tascpy" / "typing"
        
        # スタブを生成
        generate_stubs()
        
        # core ドメインの操作を取得
        core_ops = set(OperationRegistry.get_operations("core").keys())
        
        # スタブからcoreドメインの操作を取得
        core_stub_path = typing_dir / "core.py"
        core_stub_ops = set(self._get_operations_in_stub(core_stub_path))
        
        # load_displacement ドメインのスタブを調べる
        ld_stub_path = typing_dir / "load_displacement.py"
        ld_stub_ops = set(self._get_operations_in_stub(ld_stub_path))
        
        # coordinate ドメインのスタブを調べる
        coord_stub_path = typing_dir / "coordinate.py"
        coord_stub_ops = set(self._get_operations_in_stub(coord_stub_path))
        
        # コアメソッドでドメイン特化型スタブに存在しなければならないメソッド
        core_essential_methods = {"add", "subtract", "multiply", "divide", "filter_by_function"}
        
        # 各ドメイン特化スタブにコア操作が含まれているか確認
        for method in core_essential_methods:
            self.assertIn(method, core_stub_ops, f"coreドメインに{method}メソッドがありません")
            self.assertIn(method, ld_stub_ops, f"load_displacementドメインに{method}メソッドがありません")
            self.assertIn(method, coord_stub_ops, f"coordinateドメインに{method}メソッドがありません")
        
        # 各ドメイン特化スタブにcoreのメソッドが含まれるか確認（コアのメソッドと同名のドメインメソッドを除く）
        ld_domain_ops = OperationRegistry.get_operations("load_displacement")
        for method in core_ops:
            if method not in ld_domain_ops:
                self.assertIn(method, ld_stub_ops, f"load_displacementドメインの型に{method}コアメソッドがありません")

        coord_domain_ops = OperationRegistry.get_operations("coordinate")
        for method in core_ops:
            if method not in coord_domain_ops:
                self.assertIn(method, coord_stub_ops, f"coordinateドメインの型に{method}コアメソッドがありません")


if __name__ == "__main__":
    unittest.main()
