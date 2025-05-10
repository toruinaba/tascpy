# GitHub Copilot Instructions for tascpy

## プロジェクトの目的と概要

tascpy は、tasc という計測アプリケーションから出力される計測データ（CSV、TXTファイルなど）を
速やかに分析、可視化するためのライブラリです。データの効率的な解析と視覚化を可能にします。

## コーディング規約

### 基本スタイル
- PEP 8 スタイルガイドに準拠
- 行の最大長は 88 文字（Black 準拠）
- インデントは 4 スペース

### 命名規則
- クラス名: パスカルケース (`DomainCollectionFactory`)
- 関数/メソッド/変数名: スネークケース (`create_column_collection`, `result_column`)
- プライベートメンバー: アンダースコア接頭辞 (`_factories`)
- 定数: 大文字のスネークケース (`MAX_VALUE`)
- ファイル名: スネークケース (`factory.py`, `collection.py`)
- 変数名は英語のみ使用（日本語不可）

### 型ヒント
- 全ての関数とメソッドには型ヒントを付ける
- 複雑な型は `typing` モジュールを活用
- 戻り値の型も必ず指定

```python
from typing import Dict, Callable, Optional, Any

def function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    ...
```

## ドキュメント規約

### docstring スタイル
- Google スタイルを採用
- docstring は日本語で記述
- 敬語は「です・ます」調を使用

```python
def function(param: str) -> int:
    """機能の簡潔な説明
    
    詳細な説明を書きます。複数行になる場合もあります。
    
    Args:
        param: パラメータの説明
        
    Returns:
        int: 戻り値の説明
        
    Raises:
        ValueError: エラーが発生する条件
    """
    ...
```

### 文書スタイル
- 読者に対して「〜してください」のような丁寧な言葉遣い
- 英数字は半角、日本語は全角
- 英数字と日本語の間に半角スペースを入れる
- 句読点は「、」「。」を使用
- 専門用語は初出時に英語併記
- 数字は算用数字を使用（「3つ」）
- 単位は数字と半角スペースを空けて記述（「10 MB」）
- ドキュメント中のオブジェクト名やクラス名は、コード内で使用されている名称をそのまま使用

## プロジェクト構造

```
tascpy/
├── src/
│   └── tascpy/
│       ├── core/         # 基本データ構造
│       ├── domains/      # ドメイン特化コレクション
│       ├── operations/   # データ処理操作
│       └── plugins/      # プラグイン
├── tests/
│   ├── unit/            # 単体テスト
│   └── func/            # 機能テスト
└── examples/           # サンプルコード
```

## テスト戦略

### テストフレームワークと構成
- Pytest を使用
- `tests/unit` に単体テスト
- `tests/func` に機能テスト
- ドメイン別、機能別のサブディレクトリ構造
- 単体テストのカバレッジ目標は 80% 以上
- 機能テストには特に目標値を設定しない

### テストコード命名規則と実装
- テストクラス名は `Test` で始まる（例: `TestLoadDisplacementAnalysis`）
- クラスには日本語の docstring でテスト内容を説明
- テストメソッド名は `test_` で始まる
- メソッドにも日本語の docstring でテスト内容を説明
- `setup_method` を使用してテストフィクスチャを初期化
- 明確なエラーメッセージを含む assert ステートメント

```python
class TestExample:
    """○○機能のテスト"""
    
    def setup_method(self, method):
        """テスト環境の準備"""
        self.data = ...
        
    def test_basic_functionality(self):
        """基本機能のテスト"""
        result = some_function(self.data)
        assert result == expected, f"期待値: {expected}, 実際: {result}"
```

## ドメイン定義
現在、tascpy では以下のドメインが実装されています：

1. **core**: 基本的な `ColumnCollection` に対する操作
   - 基本的なデータ構造と汎用操作を提供

2. **load_displacement**: 荷重変位およびそれに類するデータの操作に特化したドメイン
   - `LoadDisplacementCollection` クラスを実装
   - `operations/load_displacement` 以下に特化した操作を提供

3. **coordinate**: 座標値を保持し、座標を用いたデータ変換および可視化に特化したドメイン
   - `CoordinateCollection` クラスを実装
   - `operations/coordinate` 以下に特化した操作を提供

## プログラミングパターン
- ファクトリパターンを活用したドメイン特化コレクションの生成
  - `DomainCollectionFactory` で各ドメイン向けコレクションを作成
- コンポジションを重視した設計
- イミュータブルなデータ操作を推奨

## 重要な注意事項
- `tests/data` および `sandbox` ディレクトリは読み込み禁止
- 国際化対応は不要（日本語UIで問題なし）
