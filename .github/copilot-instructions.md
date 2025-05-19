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
├── examples/           # サンプルコード
├── scripts/            # スクリプト
├── docs/               # ドキュメント
├── venv/               # 仮想環境
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

## メソッドチェーン

### 基本原則
- `CollectionOperations` クラスを使用してメソッドチェーンを実現
- 操作メソッドは元のコレクションを変更せず、新しいコレクションを返す
- `.end()` メソッドでチェーンを終了し最終的な `ColumnCollection` オブジェクトを取得

### 実装パターン
- コレクションから `.ops` プロパティでアクセスし操作を開始
- 各操作メソッドは `CollectionOperations` のインスタンスを返しチェーン継続を可能に
- `in_place=True` オプションを持つメソッドは元のオブジェクトを変更可能

### 主な操作カテゴリ
- 数学演算: `add`, `subtract`, `multiply`, `divide`, `evaluate` など
- 変換操作: `sin`, `cos`, `exp`, `log`, `abs_values` など
- 選択操作: `select`, `select_step`, `select_columns` など
- フィルタリング: `filter_by_function`, `search_by_condition` など
- 微分積分: `diff`, `integrate` など
- 可視化: `plot` など

### 使用例
```python
# 複数の操作をチェーンで実行
result = (
    collection.ops
    .select_step(steps=[3, 4, 5])  # 特定のステップを選択
    .select_columns(["Force1", "Displacement1"])  # 特定の列を選択
    .multiply("Force1", 2, result_column="DoubleForce")  # 計算処理
    .evaluate("DoubleForce / Displacement1", result_column="Stiffness")  # 式の評価
    .end()  # チェーンを終了して結果を取得
)

# 統計処理のチェーン例
result = (
    ops
    .moving_average(column="raw_data", window_size=5, result_column="ma5")
    .moving_average(column="raw_data", window_size=21, result_column="ma21")
    .detect_outliers(column="raw_data", window_size=15, threshold=0.3)
    .end()
)
```

このパターンにより、データ分析の各ステップを明確に表現しながら、効率的に複数の操作を連結できます。

## ドメイン拡張とオペレーションの実装パターン

### ドメイン特化コレクションの実装
- ドメイン特化クラスは `DomainCollectionFactory` に登録して使用
- 実装時は `factory.py` の `DomainCollectionFactory.register()` メソッドを使用
- ドメイン間変換は `converters.py` の `register_domain_converter` デコレータを使用

```python
# ドメイン特化コレクションの実装例
class LoadDisplacementCollection(ColumnCollection):
    """荷重変位データ向けコレクション"""
    
    def __init__(
        self, 
        step: Optional[Indices] = None, 
        columns: Optional[Dict[str, Column]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        load_column: Optional[str] = None,
        displacement_column: Optional[str] = None
    ):
        """初期化
        
        Args:
            step: インデックスオブジェクト
            columns: カラムの辞書
            metadata: メタデータ辞書
            load_column: 荷重のカラム名
            displacement_column: 変位のカラム名
        """
        super().__init__(step=step, columns=columns, metadata=metadata)
        
        # メタデータに追加情報を設定
        if not self.metadata:
            self.metadata = {}
        self.metadata["domain"] = "load_displacement"
        
        # 荷重と変位のカラムを設定
        self._load_column = load_column
        self._displacement_column = displacement_column

# ドメイン特化コレクションファクトリの登録
def create_load_displacement_collection(**kwargs: Any) -> LoadDisplacementCollection:
    """荷重変位コレクションを作成するファクトリ関数"""
    return LoadDisplacementCollection(**kwargs)

# ファクトリへの登録
DomainCollectionFactory.register("load_displacement", create_load_displacement_collection)
```

### ドメイン間の変換
- `converters.py` の `register_domain_converter` デコレータを使用して変換関数を登録
- 変換関数は元のコレクションと更新された kwargs を返す

```python
@register_domain_converter(source_domain="core", target_domain="load_displacement")
def prepare_for_load_displacement(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """一般コレクションから荷重-変位コレクションへの変換準備を行う"""
    # 変換ロジックを実装
    # ...
    return collection, modified_kwargs
```

### 操作関数の実装
- 操作関数は `operations/` ディレクトリ以下に実装
- `registry.py` の `operation` デコレータを使用して登録
- ドメイン特化操作は対応するドメインで指定

```python
# operations/core/math.py の例
@operation  # デフォルトで core ドメイン
def add(
    collection: ColumnCollection,
    column1: str,
    column2: Union[str, float, int],
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """2つのカラム（または数値）を加算"""
    # 実装...
    return result_collection

# operations/load_displacement/analysis.py の例
@operation(domain="load_displacement")  # 特定ドメインを指定
def calculate_slopes(
    collection: LoadDisplacementCollection,
    range_start: Optional[float] = None,
    range_end: Optional[float] = None,
    result_column: Optional[str] = None,
) -> LoadDisplacementCollection:
    """荷重-変位カーブの傾きを計算"""
    # 実装...
    return result_collection
```

### メソッドチェーンと操作登録
- すべての操作関数は `CollectionOperations` クラスに自動登録される
- 登録された操作はメソッドチェーンで利用可能
- カスタム操作を追加する場合も同様のパターンで登録

```python
# 操作の実行例
result = (
    collection.ops
    .select_columns(["Force", "Displacement"])
    .filter_by_function("Force", lambda x: x > 0)
    .calculate_slopes(range_start=0.1, range_end=0.5)
    .end()
)
```

### コレクションリスト操作
- `CollectionListOperations` クラスを使用して複数のコレクションを一度に操作
- `split` 系のメソッドでコレクションを分割し、リスト形式で処理
- リスト操作とメソッドチェーンの組み合わせが可能

```python
# コレクションの分割と各グループへの一括操作
result = (
    collection.ops
    .split_by_integers([1, 2, 1, 2, 3, 3])  # グループごとに分割
    .map("add", "Value", 10, result_column="ValuePlus10")  # 全グループに同じ操作
    .filter(lambda col: col.columns["Value"].mean() > 20)  # 条件に合うグループのみ選択
)

# インデックスで特定のグループにアクセス
first_group = result[0]
# スライスでグループを選択
first_two_groups = result[:2]
```

## スタブファイル生成について

tascpy は操作メソッドを動的に登録する仕組みを採用しています。これにより VS Code などのエディタで静的解析ツールを使用する際に、自動補完が正しく機能しない場合があります。この問題を解決するためのスタブファイル生成機能があります。

### 自動生成（推奨）

モジュールのインポート時に自動的にスタブファイルが生成されます：

```python
import tascpy  # このインポート時に自動的にスタブファイルが生成されます
```

環境変数を使って無効化も可能です：

```python
import os
os.environ["TASCPY_GENERATE_STUBS"] = "0"
import tascpy  # スタブファイルは生成されません
```

### 手動生成

コマンドラインまたはPythonコードから手動生成も可能です：

```bash
python scripts/generate_stubs.py
```

```python
from tascpy.operations.stub_generator import generate_stubs
generate_stubs()
```

スタブファイルは `src/tascpy/typing/` ディレクトリに生成され、VS Code / Pylance での自動補完が有効になります。新しい操作メソッドの追加や変更時は、次回インポート時に自動的に最新のスタブファイルが生成されます。

### スタブファイルの仕組み

スタブ生成システムの主要コンポーネント：
- `OperationRegistry.generate_stubs()`: スタブ生成プロセスの開始
- `stub_generator.py`: メインのスタブ生成ロジック
- 型情報維持のための `TypeVar` の活用


## サンプルコードの作成方針
- examples以下に格納されるサンプルコードについては可読性を重視し、関数を用いず平文とする
- 同じく可読性を向上させるためメソッドチェーンを活用したサンプルコードを作成


## 重要な注意事項
- `tests/data` および `sandbox` ディレクトリは読み込み禁止
- 国際化対応は不要（日本語UIで問題なし）
- 提案は日本語
