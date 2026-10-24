# tascpy 開発者ガイド

このガイドは、tascpy を拡張したり、機能を追加したりする開発者向けの情報をまとめたものです。

## アーキテクチャ概要

```text
src/tascpy/
├── core/                   # 基本データ構造
│   ├── collection.py       # ColumnCollection（polars DataFrame + 列メタ、.ops / .plot / .io）
│   ├── column.py           # Column（読み取り専用ビュー）, ColumnMeta
│   ├── row.py
│   └── result.py           # AnalysisResult（ScalarResult, PointResult, XYSeriesResult）
├── domains/                # ドメイン特化コレクション
│   ├── load_displacement.py
│   ├── coordinate.py
│   └── strain.py
├── numeric/                # 純粋な計算関数（NumPy 配列 -> 配列・値）。単体でも使える公開 API
│   ├── math.py, stats.py, combine.py  # 汎用
│   ├── curve.py            # x-y 曲線（傾き・剛性・降伏点・ピーク・面積）
│   ├── hysteresis.py       # 繰り返し載荷（サイクル・エネルギー・スケルトン曲線・累積曲線）
│   ├── rosette.py          # ロゼット解析
│   └── spatial.py          # 距離・近傍・クラスタリング・空間補間
├── analytics/
│   └── ops/                # メソッドチェーンの操作クラス
│       ├── core.py         # CoreOps
│       ├── load_displacement.py  # LoadDisplacementOps
│       ├── coordinate.py   # CoordinateOps
│       ├── strain.py       # StrainOps
│       └── list.py         # OpsList
├── visualization/          # 可視化（描画関数 + plotters）
└── io/                     # ファイル入出力
```

データ保持・単位・欠損の規則は [コアデータモデル設計](developer_guide_design.md) にまとめています。

### 主要クラスの関係

- **ColumnCollection**: 不変なデータコンテナ。データは polars の DataFrame、単位などは列ごとの `ColumnMeta` として持ちます。`ops` / `plot` / `io` プロパティを持ちます
- **ドメインコレクション**（`LoadDisplacementCollection` など）: `ColumnCollection` のサブクラス。ドメイン固有の設定を属性として持ち、`ops` / `plot` が対応するドメインのクラスを返します
- **CoreOps とそのサブクラス**: メソッドチェーンの操作。各操作は numeric の関数を呼び、新しいコレクションを持つ操作オブジェクトを返します

### 依存関係

```text
ops, domains, visualization ──> numeric
ops ──> core, domains
domains ──> core
visualization, io ──> core
```

`core` から `ops` / `visualization` / `io` へは、各プロパティ内で遅延インポートしています。numeric はコレクションにも polars にも依存せず、numpy だけで単体利用できます。この境界は import-linter の契約（`pyproject.toml` の `[tool.importlinter]`）で検査します。

## 開発環境のセットアップ

前提: Python 3.11 以上

```bash
git clone https://github.com/toruinaba/tascpy.git
cd tascpy
pip install -e . -r requirements-dev.txt
```

テストと型チェック:

```bash
pytest   # 設定は pytest.ini
pyright   # 設定は pyproject.toml
lint-imports   # import の境界の検査。設定は pyproject.toml
```

## 新しい操作の追加

numeric に純粋関数を書き、対応する Ops クラスにメソッドを追加します。手順、内部ヘルパー、新しいドメインの追加方法は [操作の追加方法](developer_guide_operations.md) を参照してください。

## テスト

numeric のテストと ops のテストを分けて書きます。[テスト戦略](developer_guide_testing.md) を参照してください。

## ドキュメント

docstring は Google スタイルの日本語で記述します。API リファレンスは mkdocstrings で docstring から生成されます（`docs/api/`）。

```python
def calculate_stiffness(self, range_start: float = 0.2, range_end: float = 0.8) -> Self:
    """最大荷重に対する比率で指定した範囲の剛性を計算し、結果 "stiffness" に格納します

    Args:
        range_start: 範囲の開始比率
        range_end: 範囲の終了比率

    Examples:
        >>> col.ops.calculate_stiffness(0.1, 0.4).end().results["stiffness"].value
    """
```

## 貢献ガイドライン

### コーディング規約

- PEP 8 に準拠し、行の最大長は 88 文字（Black 準拠）
- ドキュメントは日本語（Google スタイル）
- 公開する関数・メソッドには型ヒントを付ける

### プルリクエストの流れ

1. 機能追加や修正の Issue を作成
2. ブランチを作成（`feature/機能名` または `fix/バグ名`）
3. 変更を実装し、テストを追加
4. テストと型チェックが通ることを確認
5. ドキュメントを更新し、プルリクエストを作成

### リリース

- セマンティックバージョニング（MAJOR.MINOR.PATCH）を採用
- リリースごとに変更履歴を更新
