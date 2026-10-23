# tascpy 開発者ガイド

このガイドは、tascpy を拡張したり、機能を追加したりする開発者向けの情報をまとめたものです。

## アーキテクチャ概要

```text
src/tascpy/
├── core/                   # 基本データ構造
│   ├── collection.py       # ColumnCollection（.ops / .plot / .io プロパティ）
│   ├── column.py           # Column, NumberColumn, StringColumn, InvalidColumn
│   ├── step.py             # Step（行インデックス）
│   ├── row.py
│   └── result.py           # AnalysisResult（ScalarResult, PointResult, XYSeriesResult）
├── domains/                # ドメイン特化コレクション
│   ├── factory.py          # DomainCollectionFactory
│   ├── converters.py       # ドメイン変換の前処理
│   ├── load_displacement.py
│   ├── coordinate.py
│   └── strain.py
├── analytics/
│   ├── functional/         # 純粋な計算関数（NumPy 配列 -> 配列・値）
│   │   ├── core/           # math, filters, select, stats, combine
│   │   ├── load_displacement/
│   │   ├── coordinate/
│   │   └── strain/
│   └── ops/                # メソッドチェーンの操作クラス
│       ├── core.py         # CoreOps
│       ├── load_displacement.py  # LoadDisplacementOps
│       ├── coordinate.py   # CoordinateOps
│       ├── strain.py       # StrainOps
│       └── list.py         # OpsList
├── visualization/          # 可視化（functional 描画関数 + plotters）
├── io/                     # ファイル入出力
└── utils/
```

### 主要クラスの関係

- **ColumnCollection**: 基本データコンテナ。`ops` / `plot` / `io` プロパティを持ちます
- **ドメインコレクション**（`LoadDisplacementCollection` など）: `ColumnCollection` のサブクラス。`ops` / `plot` が対応するドメインのクラスを返します
- **CoreOps とそのサブクラス**: メソッドチェーンの操作。各操作は functional の関数を呼び、新しいコレクションを持つ操作オブジェクトを返します
- **DomainCollectionFactory**: ドメイン名からコレクションを生成します（`as_domain` で使用）

### 依存関係

```text
ops ──> functional
ops ──> core, domains
domains ──> core
visualization, io ──> core
```

`core` から `ops` / `visualization` / `io` へは、各プロパティ内で遅延インポートしています。functional はコレクションに依存しません。

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
```

## 新しい操作の追加

functional に純粋関数を書き、対応する Ops クラスにメソッドを追加します。手順、内部ヘルパー、新しいドメインの追加方法は [操作の追加方法](developer_guide_operations.md) を参照してください。

## テスト

functional のテストと ops のテストを分けて書きます。[テスト戦略](developer_guide_testing.md) を参照してください。

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
