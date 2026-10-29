# tascpy 開発者ガイド

このガイドは、tascpy を拡張したり、機能を追加したりする開発者向けの情報をまとめたものです。

## アーキテクチャ概要

```text
src/tascpy/
├── core/                   # データモデルと、ドメインに依存しない操作・入出力・描画
│   ├── collection.py       # ColumnCollection（polars DataFrame + 列メタ、.ops / .plot / .io）
│   ├── column.py           # Column（読み取り専用ビュー）, ColumnMeta
│   ├── row.py
│   ├── result.py           # AnalysisResult（ScalarResult, PointResult, XYSeriesResult）
│   ├── ops.py              # CoreOps
│   ├── ops_list.py         # OpsList
│   ├── io/                 # ファイル入出力（TASC 系テキスト・Parquet・CSV）
│   └── plot/               # CorePlotter、描画関数、Plotly、日本語フォント
├── domains/                # ドメイン。ドメインごとに縦割りのパッケージ
│   ├── load_displacement/  # collection.py（設定）, ops.py（操作）, plotter.py / draw.py（描画）
│   ├── coordinate/         # collection.py, ops.py（描画は CorePlotter）
│   └── strain/             # collection.py, ops.py, plotter.py / draw.py（座標ドメインを拡張）
├── numeric/                # 純粋な計算関数（NumPy 配列 -> 配列・値）。単体でも使える公開 API
│   ├── math.py, stats.py, combine.py  # 汎用
│   ├── curve.py            # x-y 曲線（傾き・剛性・降伏点・ピーク・面積）
│   ├── hysteresis.py       # 繰り返し載荷（サイクル・エネルギー・スケルトン曲線・累積曲線）
│   ├── rosette.py          # ロゼット解析
│   └── spatial.py          # 距離・近傍・クラスタリング・空間補間
```

データ保持・単位・欠損の規則は [コアデータモデル設計](developer_guide_design.md) にまとめています。

### 主要クラスの関係

- **ColumnCollection**: 不変なデータコンテナ。データは polars の DataFrame、単位などは列ごとの `ColumnMeta` として持ちます。`ops` / `plot` / `io` プロパティを持ちます
- **ドメインコレクション**（`LoadDisplacementCollection` など）: `ColumnCollection` のサブクラス。ドメイン固有の設定を属性として持ち、`ops` / `plot` が対応するドメインのクラスを返します。`domain` を定義したサブクラスは定義時にレジストリに登録され、`load_parquet` での復元に使われます
- **CoreOps とそのサブクラス**: メソッドチェーンの操作。各操作は numeric の関数を呼び、新しいコレクションを持つ操作オブジェクトを返します

### 依存関係

```text
domains ──> core ──> numeric
strain ──> coordinate（ドメイン間で許可しているのはこれだけ）
```

`core.plot` は `coll.plot` のプロパティ内で遅延インポートしており、`import tascpy` だけでは matplotlib を読み込みません。トップレベルの `tascpy.ColumnCollection` なども初回アクセス時に import します（`import tascpy.numeric` で polars を読み込まないため）。トップレベルは組み立て役で、公開名に初めてアクセスしたときに `tascpy.domains` を import して組み込みドメインを登録します。core は domains を（遅延インポートも含めて）一切参照せず、ドメインへの変換は `CoreOps.as_domain`、Parquet からの復元はドメインのレジストリを通します。numeric はコレクションにも polars にも依存せず、numpy だけで単体利用できます。これらの境界は import-linter の契約（`pyproject.toml` の `[tool.importlinter]`）で検査します。

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
def stiffness(self, *, range_start: float = 0.2, range_end: float = 0.8) -> ScalarResult:
    """最大荷重に対する比率で指定した範囲の剛性を求めます

    Args:
        range_start: 範囲の開始比率
        range_end: 範囲の終了比率

    Examples:
        >>> col.ops.stiffness(range_start=0.1, range_end=0.4).value
    """
```

## コーディング規約

- PEP 8 に準拠し、行の長さは 88 文字を目安にする
- ドキュメントは日本語（Google スタイル）
- 公開する関数・メソッドには型ヒントを付ける

ブランチの運用とリリース手順（タグの push で PyPI に公開）は、リポジトリの `CONTRIBUTING.md` にまとめています。
