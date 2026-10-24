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
import tascpy

# 基本サンプルデータの読み込み（ヘッダーのチャンネル・名前・単位行が列メタになる）
basic_data = tascpy.load("./sample.csv", format_name="csv")
print(basic_data.units)  # {'Force1': 'kN', ...}

# 荷重-変位サンプルデータの読み込み
ld_data = tascpy.load("./load_displacement_sample.csv", format_name="csv")
```

### サンプルデータの生成

```python
# 荷重-変位サンプルデータ生成スクリプトの実行
exec(open("./create_load_displacement_sample.py").read())

# または直接実行
# python create_load_displacement_sample.py
```

## 独自データの使い方

`tascpy.load` は TASC 形式（タブ区切り / CSV）のヘッダー構成を前提にしています。独自のデータを使用する場合は、以下の点に注意してください：

1. **サポートされる形式** (`format_name`):
   - `"tasc_txt"` / `"tasc_csv"`: TASC 出力（Shift-JIS）
   - `"standard"` / `"csv"`: 同じ構成の UTF-8 ファイル
   - 独自形式は `tascpy.core.io.register_format` で登録できます

2. **列の型と欠損値**:
   - 数値の列は自動的に Float64 になります
   - `none` / `null` / `nan` / 空欄 / `*` で始まる値は欠損として読み込まれます
   - 単位行が空欄の列の単位は `None`（不明）になります

3. **ヘッダー行の位置**:
   - チャンネル行・名前行・単位行・データ開始行・データ開始列などはキーワード引数で上書きできます
   - 日付・時刻の列はインデックス列 `date` / `time` として読み込まれます

```python
# 独自データの読み込み例
custom_data = tascpy.load(
    "./your_data.csv",
    format_name="csv",
    encoding="shift_jis",  # 文字コードの指定
    unit_row=3,  # 単位行の位置 (0 始まり)
    data_start_row=4,  # データ開始行
    selected_columns=["Force1", "Displacement1"],  # 読み込む列（列名またはチャンネル名）
)
```

## 注意事項

- テストデータはデモンストレーション目的で提供されており、実際の実験結果とは異なります
- 大きなデータファイルを扱う場合は、メモリ使用量に注意してください
- 実際のプロジェクトでは、データファイルをバージョン管理から除外することが一般的です（.gitignore に追加）
