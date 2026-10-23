# tascpy

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green)](https://github.com/toruinaba/tascpy)

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
collection = tascpy.io.load("data.csv", format_name="csv", auto_detect_types=True)

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

### 荷重-変位ドメインの分析

```python
# 荷重-変位ドメインへ変換し、剛性と降伏点を計算
ld = (
    collection.ops
    .as_load_displacement(load_column="Force", displacement_column="Displacement")
    .remove_consecutive_duplicates_across()
    .calculate_stiffness(range_start=0.1, range_end=0.5)
    .find_yield_point(method="offset", offset_value=0.002)  # 0.2%オフセット法
    .end()
)

print(f"初期剛性: {ld.results['stiffness'].value:.2f}")
yield_pt = ld.results["yield_point"]
print(f"降伏荷重: {yield_pt.y:.2f} kN")
print(f"降伏変位: {yield_pt.x:.2f} mm")
```

`collection.ops` が返す操作オブジェクトは通常のクラスなので、IDE の自動補完と型チェックがそのまま効きます。ドメインに変換すると、そのドメイン固有の操作（`find_yield_point` など）も補完されます。

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

## 動作環境

- Python 3.11 以上
- 依存ライブラリ:
  - numpy
  - matplotlib
  - japanize-matplotlib（日本語フォントサポート用）

## プロジェクト構造

```
tascpy/
├── src/
│   └── tascpy/
│       ├── core/             # 基本データ構造（ColumnCollection, Column, Step）
│       ├── domains/          # ドメイン特化コレクション（荷重-変位・座標・ひずみ）
│       ├── analytics/
│       │   ├── functional/   # 純粋な計算関数
│       │   └── ops/          # メソッドチェーンの操作クラス（collection.ops）
│       ├── visualization/    # 可視化
│       └── io/               # データ入出力
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
