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
├── src/tascpy/
│   ├── core/            # ColumnCollection（polars DataFrame + 列メタ）, Column, ColumnMeta, Row, 解析結果
│   ├── domains/         # ドメイン特化コレクション（荷重-変位・座標・ひずみ）
│   ├── analytics/
│   │   ├── functional/  # numpy だけに依存する純粋な計算関数
│   │   └── ops/         # メソッドチェーンの操作クラス（collection.ops）
│   ├── visualization/   # 可視化
│   └── io/              # ファイル入出力
├── tests/
│   ├── unit/            # 単体テスト
│   ├── func/            # 機能テスト
│   └── manual/examples/ # サンプルコード
└── docs/                # ドキュメント（設計は docs/developer_guide_design.md）
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

## データモデル

詳細は `docs/developer_guide_design.md` を参照してください。要点:

- `ColumnCollection` は不変。変更は `with_column` / `with_meta` / `with_metadata` / `select` / `take` などで新しいコレクションを返す
- 列の単位・チャンネル・属性は `ColumnMeta` に持つ。単位は記録・確認のためで自動変換はしない。不明な単位は推測せず `None`
- `step`（必須）・`date`・`time` はインデックス列で、データ列名には使えない
- 数値列は Float64、欠損は null（`.values` では NaN）

## ドメイン

1. **core**: `ColumnCollection` と `CoreOps`
2. **load_displacement**: `LoadDisplacementCollection`（`load_column` / `displacement_column` を属性に持つ）と `LoadDisplacementOps`
3. **coordinate**: `CoordinateCollection`（座標は列メタの `attrs["coordinates"]`）と `CoordinateOps`
4. **strain**: `StrainCollection`（ロゼット定義を属性に持つ）と `StrainOps`

ドメインへの変換は `ops.as_load_displacement(...)` / `ops.as_coordinate(...)` / `ops.as_strain(...)`、戻すときは `ops.as_core()`。
新しいドメインの追加方法は `docs/developer_guide_operations.md` を参照してください。

## メソッドチェーン

- `collection.ops` が操作クラス（`CoreOps` とドメインごとのサブクラス）を返す。操作は通常のメソッドとして静的に定義されており、IDE の補完と pyright の型チェックが効く
- 各操作は新しいコレクションを持つ操作オブジェクト（`Self`）を返し、`.end()` でコレクションを取り出す
- 計算は functional の純粋関数に書き、ops はコレクションからの値の取り出し・結果と単位の格納だけを行う
- 行の抽出・検索などの表操作は ops の中で polars を使って実装する
- `split_*` は `OpsList` を返す（`map` / `collect` / `filter` / `concat` / `end`）

```python
result = (
    collection.ops
    .split_by_integers([1, 1, 2, 2, 3, 3])
    .map(lambda o: o.add("Value", 10, result_column="ValuePlus10"))
    .filter(lambda c: c["Value"].mean() > 20)
    .concat()
    .end()
)
```

## サンプルコードの作成方針
- examples以下に格納されるサンプルコードについては可読性を重視し、関数を用いず平文とする
- 同じく可読性を向上させるためメソッドチェーンを活用したサンプルコードを作成


## 重要な注意事項
- `tests/data` および `sandbox` ディレクトリは読み込み禁止
- 国際化対応は不要（日本語UIで問題なし）
- 提案は日本語
