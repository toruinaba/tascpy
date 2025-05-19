# tascpy 開発者ガイド

このガイドは、tascpy ライブラリを拡張したり、カスタム機能を追加したりする開発者向けの情報を提供します。

## アーキテクチャ概要

tascpy のアーキテクチャは以下の主要コンポーネントで構成されています：

```
tascpy/
├── core/               # 基本データ構造とコア機能
│   ├── collection.py   # ColumnCollection クラス
│   ├── column.py       # 列の基本クラス
│   ├── indices.py      # インデックス管理
├── domains/            # ドメイン特化コレクション
│   ├── factory.py      # ドメインファクトリ
│   ├── converters.py   # ドメイン間変換
│   ├── coordinate/     # 座標ドメイン
│   ├── load_displacement/ # 荷重-変位ドメイン
├── operations/         # データ処理操作
│   ├── registry.py     # 操作の登録システム
│   ├── core/           # コアドメイン操作
│   ├── load_displacement/ # 荷重-変位ドメイン操作
```

### 主要クラスの関係

- **ColumnCollection**: 基本データコンテナ
- **DomainCollectionFactory**: ドメイン特化コレクションの作成を担当
- **CollectionOperations**: メソッドチェーンを実現するための操作ハブ
- **OperationRegistry**: 操作関数を登録・管理

## 開発環境のセットアップ

### 前提条件

- Python 3.8以上
- pipenv または venv による仮想環境

### 開発用インストール

```bash
# リポジトリのクローン
git clone https://github.com/toruinaba/tascpy.git
cd tascpy

# 開発モードでインストール
pip install -e .

# 開発用パッケージのインストール
pip install -r requirements-dev.txt
```

### 開発ツール

- **black**: コード整形
- **isort**: インポート順序の最適化
- **flake8**: リンター
- **mypy**: 静的型チェック
- **pytest**: テストランナー

## 新しい操作の追加

新しいデータ処理操作を追加するには、以下の手順に従います：

### 1. 操作関数の実装

```python
# src/tascpy/operations/core/custom_ops.py
from typing import Optional, Union, Dict, Any

from tascpy.core.collection import ColumnCollection
from tascpy.operations.registry import operation

@operation  # デコレータを使用して操作を登録
def custom_function(
    collection: ColumnCollection,
    column: str,
    parameter: float,
    result_column: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """カスタム操作の説明
    
    Args:
        collection: 対象のコレクション
        column: 処理対象の列名
        parameter: 処理パラメータ
        result_column: 結果を格納する列名（省略時は上書き）
        in_place: True の場合は元のコレクションを変更
        
    Returns:
        処理後のコレクション
    """
    # 操作の実装
    result_col_name = result_column or column
    # 元のコレクションのコピーを作成（in_place=False の場合）
    if not in_place:
        result_collection = collection.copy()
    else:
        result_collection = collection
    
    # データの処理
    values = collection[column].values
    processed_values = [value * parameter for value in values]
    
    # 結果をセット
    result_collection.set_column_values(result_col_name, processed_values)
    
    return result_collection
```

### 2. 操作の登録

操作関数に `@operation` デコレータを付けると、自動的に `OperationRegistry` に登録されます。特定のドメインに特化した操作の場合は、ドメイン名を指定します：

```python
# 荷重-変位ドメイン特化の操作
@operation(domain="load_displacement")
def custom_ld_operation(
    collection: LoadDisplacementCollection,
    # パラメータ...
) -> LoadDisplacementCollection:
    # 実装...
```

### 3. テストの作成

新しい操作に対するテストを作成します：

```python
# tests/unit/operations/core/test_custom_ops.py
import pytest
from tascpy.core.collection import ColumnCollection

class TestCustomOperations:
    """カスタム操作のテスト"""
    
    def setup_method(self):
        """テスト用のデータを準備"""
        self.collection = ColumnCollection.from_dict({
            "A": [1.0, 2.0, 3.0],
            "B": [4.0, 5.0, 6.0]
        })
        
    def test_custom_function(self):
        """custom_function の基本機能をテスト"""
        result = self.collection.ops.custom_function("A", 2.0, result_column="A_doubled").end()
        
        # 結果の検証
        assert "A_doubled" in result.columns
        assert result["A_doubled"].values[0] == 2.0
        assert result["A_doubled"].values[1] == 4.0
        assert result["A_doubled"].values[2] == 6.0
        
        # 元のデータが変更されていないことを確認
        assert self.collection["A"].values[0] == 1.0
```

### 4. ドキュメントの更新

docstring には Google スタイルの日本語ドキュメントを記述します：

```python
## ドメイン特化コレクションの作成

新しいドメイン特化コレクションを実装するプロセスを説明します：

### 1. コレクションクラスの実装

```python
# src/tascpy/domains/custom_domain/collection.py
from typing import Optional, Dict, Any, List

from tascpy.core.collection import ColumnCollection
from tascpy.core.indices import Indices
from tascpy.core.column import Column

class CustomDomainCollection(ColumnCollection):
    """カスタムドメインのコレクション
    
    特定の分析領域に特化した機能を提供します。
    """
    
    def __init__(
        self, 
        step: Optional[Indices] = None, 
        columns: Optional[Dict[str, Column]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        special_column: Optional[str] = None
    ):
        """初期化
        
        Args:
            step: インデックスオブジェクト
            columns: カラムの辞書
            metadata: メタデータ辞書
            special_column: 特別な列の名前
        """
        super().__init__(step=step, columns=columns, metadata=metadata)
        
        # メタデータを設定
        if not self.metadata:
            self.metadata = {}
        self.metadata["domain"] = "custom_domain"
        
        # 特別な列を設定
        self._special_column = special_column
        
    @property
    def special_column(self) -> Optional[str]:
        """特別な列の名前を取得"""
        return self._special_column
    
    # ドメイン特化メソッドを追加
    def domain_specific_method(self) -> Any:
        """ドメイン特化の機能を提供"""
        if not self._special_column or self._special_column not in self.columns:
            raise ValueError("特別な列が設定されていないか、存在しません")
            
        # 実装...
        return some_result
```

### 2. ファクトリ関数の実装

```python
# src/tascpy/domains/custom_domain/factory.py
from typing import Any, Optional, Dict

from tascpy.domains.custom_domain.collection import CustomDomainCollection

def create_custom_domain_collection(**kwargs: Any) -> CustomDomainCollection:
    """カスタムドメインコレクションを作成するファクトリ関数"""
    return CustomDomainCollection(**kwargs)
```

### 3. ドメインの登録

```python
# src/tascpy/domains/custom_domain/__init__.py
from tascpy.domains.factory import DomainCollectionFactory
from tascpy.domains.custom_domain.factory import create_custom_domain_collection

# ファクトリへの登録
DomainCollectionFactory.register("custom_domain", create_custom_domain_collection)
```

### 4. ドメイン変換の実装

```python
# src/tascpy/domains/converters.py
from typing import Tuple, Dict, Any

from tascpy.core.collection import ColumnCollection
from tascpy.domains.converters import register_domain_converter

@register_domain_converter(source_domain="core", target_domain="custom_domain")
def prepare_for_custom_domain(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """一般コレクションからカスタムドメインコレクションへの変換準備を行う"""
    
    # 変換ロジックを実装
    modified_kwargs = kwargs.copy()
    
    # 特別な列を自動検出する例
    if "special_column" not in modified_kwargs:
        # 列名から特別な列を推測するロジック
        special_columns = [col for col in collection.columns if "special" in col.lower()]
        if special_columns:
            modified_kwargs["special_column"] = special_columns[0]
    
    return collection, modified_kwargs
```

### 5. ドメイン特化操作の実装

```python
# src/tascpy/operations/custom_domain/analysis.py
from typing import Optional, Any

from tascpy.domains.custom_domain.collection import CustomDomainCollection
from tascpy.operations.registry import operation

@operation(domain="custom_domain")
def special_analysis(
    collection: CustomDomainCollection,
    parameter: float,
    result_column: Optional[str] = None
) -> CustomDomainCollection:
    """カスタムドメイン特化の分析処理
    
    Args:
        collection: カスタムドメインコレクション
        parameter: 分析パラメータ
        result_column: 結果列名
        
    Returns:
        処理後のコレクション
    """
    # カスタムドメイン特有の処理
    special_column = collection.special_column
    if not special_column:
        raise ValueError("特別な列が設定されていません")
  ## テスト戦略

tascpy のテストは以下の原則に従って実装します：

### 単体テスト (Unit Tests)

- `tests/unit` ディレクトリに配置
- 個々のクラス・メソッド・関数の動作を検証
- モジュール構造を反映したディレクトリ構造
- テストクラス名は `Test` で始める
- Pytest フィクスチャを活用

```python
# tests/unit/domains/test_custom_domain.py
import pytest
from tascpy.domains.custom_domain.collection import CustomDomainCollection

class TestCustomDomainCollection:
    """カスタムドメインコレクションのテスト"""
    
    def setup_method(self):
        """テスト用データの準備"""
        self.collection = CustomDomainCollection(
            columns={
                "A": [1.0, 2.0, 3.0],
                "special_data": [10.0, 20.0, 30.0]
            },
            special_column="special_data"
        )
    
    def test_initialization(self):
        """初期化が正しく行われることを確認"""
        assert self.collection.special_column == "special_data"
        assert self.collection.metadata["domain"] == "custom_domain"
    
    def test_domain_specific_method(self):
        """ドメイン特化メソッドのテスト"""
        result = self.collection.domain_specific_method()
        # 結果の検証...
```

### 機能テスト (Functional Tests)

- `tests/func` ディレクトリに配置
- 複数のコンポーネントを組み合わせた機能をテスト
- 実際のユースケースに近いシナリオをテスト
- 実データに近いテストデータを使用

```python
# tests/func/test_custom_domain_workflow.py
import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection

class TestCustomDomainWorkflow:
    """カスタムドメインのワークフローテスト"""
    
    def setup_method(self):
        """テスト用の実データに近いデータセットを準備"""
        # 実際のユースケースに近いデータを生成
        # ...
    
    def test_complete_workflow(self):
        """データ読み込みから分析、可視化までの一連のワークフロー"""
        # 1. データ読み込み
        collection = ColumnCollection.from_dict(self.test_data)
        
        # 2. カスタムドメインへの変換
        custom_collection = collection.ops.as_domain(
            "custom_domain", 
            special_column="data_column"
        ).end()
        
        # 3. ドメイン特化操作の実行
        result = (
            custom_collection.ops
            .special_analysis(parameter=2.5, result_column="analysis_result")
            .some_other_operation()
            .end()
        )
        
        # 4. 結果の検証
        assert "analysis_result" in result.columns## スタブファイル生成システム

tascpy では、動的に登録される操作メソッドのためのスタブファイルを自動生成する仕組みがあります。このシステムを拡張する方法を説明します：

### スタブジェネレーターの仕組み

スタブ生成プロセスは以下のステップで行われます：

1. 登録された全操作の情報を `OperationRegistry` から収集
2. 各操作の型情報とドキュメントを解析
3. 各操作に対するスタブメソッドを生成
4. `typing` ディレクトリにスタブファイルを出力

### 自動生成（推奨）

最新バージョンでは、モジュールのインポート時に自動的にスタブファイルが生成されます。特別な設定は不要です。

```python
import tascpy  # このインポート時に自動的にスタブファイルが生成されます
```

環境変数 `TASCPY_GENERATE_STUBS` を "0" に設定することで、この機能を無効化できます。

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

### カスタムスタブの追加

新しいドメインに特化した操作を追加した場合：

1. スタブは自動的に生成されます
2. 必要に応じて `stub_generator.py` をカスタマイズ：

```python
# src/tascpy/operations/stub_generator.py
# カスタムドメイン用のスタブテンプレートを追加
DOMAIN_STUB_TEMPLATES = {
    # 既存のテンプレート...
    "custom_domain": """
class CustomDomainOperations({base_class}):
    \"""カスタムドメイン特化のメソッドチェーン操作\"""
    
    def __init__(self, collection: "CustomDomainCollection"):
        super().__init__(collection)
        self._collection: "CustomDomainCollection" = collection
    
{methods}
"""
}
```

## 貢献ガイドライン

tascpy プロジェクトへの貢献を検討している方向けのガイドラインです：

### コーディング規約

- PEP 8 スタイルガイドに準拠
- 行の最大長は 88 文字（Black 準拠）
- ドキュメントは日本語で記述（Google スタイル）
- すべての関数とクラスには型ヒントを付ける

### プルリクエストプロセス

1. 機能追加や修正のIssueを作成
2. フォークしてブランチを作成（`feature/機能名` または `fix/バグ名`）
3. 変更を実装
4. テストを追加し、すべてのテストが通ることを確認
5. ドキュメントを更新
6. プルリクエストを作成

### レビュープロセス

- コードレビューはすべてのプルリクエストに対して行われます
- レビュー基準：
  - 機能が仕様通りに動作するか
  - コードの品質とスタイルガイドへの準拠
  - テストの充実度
  - ドキュメントの完全性と正確性

### リリースプロセス

- セマンティックバージョニングを採用（MAJOR.MINOR.PATCH）
- 各リリースには変更履歴（CHANGELOG）を更新
- リリースブランチを作成し、テストが完了した後にマージ

## まとめ

このガイドでは、tascpy ライブラリの拡張方法や貢献方法について説明しました。より詳細な情報や質問がある場合は、GitHub Issues を通じてプロジェクトメンテナーにお問い合わせください。

コマンドラインからスタブファイルを生成する場合は、以下のコマンドを実行できます。

```bash
python scripts/generate_stubs.py
```

あるいは、Python コードから直接生成することも可能です。

```python
from tascpy.operations.stub_generator import generate_stubs
generate_stubs()
```

スタブファイルは `src/tascpy/operations/stubs/` ディレクトリに生成され、これにより VS Code / Pylance での自動補完が有効になります。

### スタブファイルの更新

自動生成モードでは、新しい操作メソッドを追加した場合や、既存のメソッドのシグネチャを変更した場合も、次回のインポート時に自動的に最新のスタブファイルが生成されます。

手動モードの場合は、上記の方法でスタブファイルを再生成する必要があります。

### スタブファイル生成の仕組み

スタブファイル生成システムは次のコンポーネントで構成されています：

1. `OperationRegistry.generate_stubs()`: スタブ生成プロセスを開始します
2. `stub_generator.py`: メインのスタブ生成ロジックを含みます
   - `format_annotation()`: 型アノテーションを適切な文字列形式に変換
   - `generate_operation_stub()`: 各操作関数からスタブメソッドを生成
   - `generate_stubs()`: 全てのドメインとその操作のスタブ生成を実行

生成されたスタブには、ドメイン固有のクラス（例：`CoreCollectionOperations`）が含まれ、各ドメインの操作メソッドが正確な型情報と共に定義されています。

#### TypeVar と型ヒント

スタブは以下の型定義を使用して、メソッドチェーンでの型情報を維持します：

```python
T = TypeVar('T', bound='CollectionOperationsBase')
```

これにより、メソッドチェーン内で適切な戻り値の型を保持し、自動補完が正しく機能します。

### スタブファイルの利用

スタブファイルは自動的に適用されるため、特別な設定は必要ありません。VS Code を使用している場合、`collection.ops.` と入力した後に自動補完が機能し、利用可能なメソッド一覧が表示されます。

### スタブファイルのトラブルシューティング

スタブファイルが正しく生成されない場合は、以下を確認してください。

1. 仮想環境（venv）内でプロジェクトが正しくインストールされているか
2. ファイルシステムの権限設定（スタブディレクトリの書き込み権限など）
3. ログ出力を有効にして詳細を確認

```python
import logging
logging.basicConfig(level=logging.DEBUG)
from tascpy.operations.stub_generator import generate_stubs
generate_stubs()
```
