# tascpy

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.5.0-green)](https://github.com/toruinaba/tascpy)

**tascpy** は、計測アプリケーション「tasc」などから出力される計測データの分析・可視化を効率的に行うための Python ライブラリです。直感的なインターフェースと強力なデータ処理機能を備え、メソッドチェーン形式で複雑な操作を簡潔に記述できます。

## 主な特徴

- **メソッドチェーンによる流れるような操作**：複数のデータ処理ステップを連続して記述できます
- **イミュータブルなデータ操作**：元のデータを変更せず、常に新しいデータセットを生成します
- **ドメイン特化機能**：荷重-変位データや座標データなど、特定の分析領域に特化した機能を提供します
- **柔軟なデータ選択**：列名、行インデックス、ステップ値などによる多彩な選択操作をサポートします
- **高度な数学的処理**：数値演算、補間、正規化など様々な数学的操作を提供します
- **直感的な可視化**：Matplotlib と連携した簡単かつ高度なデータ可視化機能があります
- **型ヒントと自動補完**：VSCode などの IDE で自動補完や型チェックを完全サポートします

## インストール方法

### pip からのインストール

```bash
pip install tascpy
```

### ソースからのインストール

```bash
git clone https://github.com/toruinaba/tascpy.git
cd tascpy
pip install -e .
```

## 使用例

### 基本的な使い方

```python
import tascpy

# ファイルからデータを読み込む（format_name: "tasc_txt" または "csv"）
collection = tascpy.load("data.csv", format_name="csv")

# メソッドチェーンでデータを処理
result = (
    collection.ops
    .select(columns=["Force", "Displacement"])                    # 必要な列を選択
    .filter_by_condition("Force", lambda x: x > 0)                # 正の荷重のみ抽出
    .add("Force", 10, result_column="AdjustedForce")              # 新しい列を作成
    .divide("AdjustedForce", "Displacement", result_column="Ratio")
    .end()                                                        # チェーンを終了して結果を取得
)

print(f"処理後のデータ: {len(result)} 行 × {len(result.columns)} 列")
print(f"最大値: {result['Ratio'].max():.2f}")
```

### 単位の確認

各列は単位（`unit`）とチャンネル名（`ch`）を持ちます。単位は記録・確認のためのもので、自動変換はしません。
演算結果の単位は演算の種類から決まり、自明でない場合は `None`（不明）になります。`unit=` で明示することもできます。

```python
collection.units                 # {"Force": "kN", "Displacement": "mm", ...}
result["AdjustedForce"].unit     # "kN"（加算は元の列の単位を引き継ぐ）
result["Ratio"].unit             # None（列どうしの除算の単位は自明でない）
collection[0]                    # <Row step=1, Force=0.0 kN, Displacement=0.0 mm, ...>

# polars の DataFrame との相互変換
df = collection.df
again = tascpy.ColumnCollection.from_frame(df, units=collection.units)

# 保存
collection.io.save("out.txt")             # TASC 形式（列名・ch・単位を保持）
collection.io.to_parquet("out.parquet")   # 単位・属性・解析結果まで保持
restored = tascpy.load_parquet("out.parquet")
```

### 荷重-変位ドメインの分析

```python
# 荷重-変位ドメインへ変換し、剛性と降伏点を計算
ld = (
    collection.ops
    .as_domain(tascpy.as_load_displacement, load_column="Force", displacement_column="Displacement")
    .remove_consecutive_duplicates_across()
    .calculate_stiffness(range_start=0.1, range_end=0.5)
    .find_yield_point(method="offset", offset_value=0.002)  # 0.2%オフセット法
    .end()
)

stiffness = ld.results["stiffness"]
print(f"初期剛性: {stiffness.value:.2f} {stiffness.unit}")      # 例: kN/mm
yield_pt = ld.results["yield_point"]
print(f"降伏荷重: {yield_pt.y:.2f} {yield_pt.y_unit}")
print(f"降伏変位: {yield_pt.x:.2f} {yield_pt.x_unit}")
```

`collection.ops` が返す操作オブジェクトは通常のクラスなので、IDE の自動補完と型チェックがそのまま効きます。`as_domain` に変換関数（`tascpy.as_load_displacement` など）を渡してドメインに変換すると、変換の引数とドメイン固有の操作（`find_yield_point` など）も補完されます。

### 可視化の例

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
collection.plot.plot(y_column="Force", x_column="Displacement", ax=ax, marker="o", alpha=0.7)

ax.set_title("荷重-変位関係")
ax.grid(True)
plt.tight_layout()
plt.show()
```

## ドキュメント

より詳細なドキュメントとサンプルについては、以下を参照してください：

- [基本サンプル集](./tests/manual/examples/basic/README.md) - 基本的な操作と使用例
- [高度なサンプル](./tests/manual/examples/advance/README.md) - 異常値分析など高度な分析テクニック
- [ドメイン特化機能](./tests/manual/examples/domains/README.md) - 荷重-変位分析や座標データ処理の例
- [開発者ガイド](./docs/developer_guide.md) - tascpy の拡張や独自ドメインの開発方法
- [コアデータモデル設計](./docs/developer_guide_design.md) - データ保持・単位・欠損の規則

## 動作環境

- Python 3.11 以上
- 依存ライブラリ:
  - numpy
  - polars
  - matplotlib
  - japanize-matplotlib（日本語フォントサポート用）

## プロジェクト構造

```
tascpy/
├── src/
│   └── tascpy/
│       ├── numeric/          # numpy 配列に直接使える解析関数
│       ├── core/             # データモデル（ColumnCollection など）と汎用の操作・入出力・描画
│       └── domains/          # ドメイン（荷重-変位・座標・ひずみ）。ドメインごとに collection / ops / plotter / draw
├── tests/                    # テストコード（tests/manual/examples にサンプル）
└── docs/                     # ドキュメント
```

## ライセンス

MIT ライセンスの下で公開されています。詳細は [LICENSE](./LICENSE) ファイルを参照してください。

## コントリビューション

バグ報告や機能リクエスト、プルリクエストなど、あらゆる形での貢献を歓迎します。詳細は [CONTRIBUTING.md](./CONTRIBUTING.md) を参照してください。

## 著者

- Toru Inaba ([@toruinaba](https://github.com/toruinaba)) - 初期開発者

## 謝辞

このライブラリの開発にあたり、ご協力いただいたすべての方々に感謝します。

このプロジェクトは GitHub Copilot を全面的に活用して開発されています。AI アシスタントによるコード生成とリファクタリングが、開発効率の向上と品質の維持に大きく貢献しています。
