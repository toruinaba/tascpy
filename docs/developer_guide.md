## 開発者向けガイド

### スタブファイルの生成

tascpy は操作メソッドを動的に登録する仕組みを採用しています。このため、VS Code などのエディタで Pylance などの静的解析ツールを使用する際に、自動補完が正しく機能しない場合があります。

この問題を解決するために、以下の方法でスタブファイルを生成できます。

#### 1. 自動生成（推奨）

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

#### 2. 手動生成

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
