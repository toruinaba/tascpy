# tascpy サンプルデータ

このディレクトリには、tascpy ライブラリのサンプルスクリプトで使用するテストデータが含まれています。これらのデータファイルは、ライブラリの機能を例示するために使用されています。

## データファイル一覧

1. **[sample.csv](./sample.csv)** - 基本的なサンプルデータ
   - 単純な時系列データを含む
   - 基本サンプル (`examples/basic/`) で使用
   - 列構成: Time, Value1, Value2, Category など

2. **[load_displacement_sample.csv](./load_displacement_sample.csv)** - 荷重-変位分析用サンプルデータ
   - 荷重と変位の関係を示すデータ
   - ドメイン特化サンプル (`examples/domains/load_displacement/`) で使用
   - 列構成: Step, Force1, Displacement1 など

## テストデータ生成スクリプト

1. **[create_load_displacement_sample.py](./create_load_displacement_sample.py)** - 荷重-変位データ生成
   - 荷重-変位関係を模擬したサンプルデータを生成
   - 初期剛性と降伏後の挙動をパラメトリックに生成可能
   - 生成したデータを CSV ファイルに保存

## データの使用方法

### サンプルデータの読み込み

```python
from tascpy.core.collection import ColumnCollection

# 基本サンプルデータの読み込み
basic_data = ColumnCollection.from_file(
    filepath="./sample.csv", 
    format_name="csv", 
    auto_detect_types=True
)

# 荷重-変位サンプルデータの読み込み
ld_data = ColumnCollection.from_file(
    filepath="./load_displacement_sample.csv", 
    format_name="csv", 
    auto_detect_types=True
)
```

### サンプルデータの生成

```python
# モジュールのインポート
import os
import numpy as np

# 荷重-変位サンプルデータ生成スクリプトの実行
exec(open("./create_load_displacement_sample.py").read())

# または直接実行
# python create_load_displacement_sample.py
```

## 独自データの使い方

tascpy は様々なデータ形式に対応しています。独自のデータを使用する場合は、以下の点に注意してください：

1. **サポートされる形式**:
   - CSV ファイル（カンマ区切り）
   - タブ区切りテキストファイル
   - Excel ファイル（xlsx）
   - 特定の形式の実験データファイル

2. **列型の自動検出**:
   - `auto_detect_types=True` オプションを使用すると、数値や文字列などの型が自動検出されます
   - 特定の列の型を明示的に指定したい場合は、`column_types` パラメータを使用できます

3. **ヘッダー行の扱い**:
   - デフォルトでは最初の行がヘッダーとして扱われます
   - ヘッダーがない場合や別の行をヘッダーとして使用する場合は、`header` パラメータで指定できます

```python
# 独自データの読み込み例
custom_data = ColumnCollection.from_file(
    filepath="./your_data.csv",
    format_name="csv",
    auto_detect_types=True,
    header=0,  # 最初の行をヘッダーとして使用
    delimiter=",",  # 区切り文字の指定
    column_types={  # 特定の列の型を明示的に指定
        "Time": "number",
        "Category": "string"
    }
)
```

## 注意事項

- テストデータはデモンストレーション目的で提供されており、実際の実験結果とは異なります
- 大きなデータファイルを扱う場合は、メモリ使用量に注意してください
- 実際のプロジェクトでは、データファイルをバージョン管理から除外することが一般的です（.gitignore に追加）
