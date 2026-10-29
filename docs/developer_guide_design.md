# コアデータモデル設計

v0.2 でコアのデータ保持を polars に移行しました。このページは、コアの設計方針と、各層が守るべき約束をまとめたものです。

## 責任分担

| 層 | 責任 |
|---|---|
| polars | 表の保持、欠損 (null)、dtype、行の抽出・連結 |
| `core` | 列メタデータ（単位・チャンネル・属性）、step、解析結果の保持、不変条件 |
| `core.ops` / `domains.*.ops` | 公開 API（メソッドチェーン）と単位の伝播（汎用 / ドメイン固有） |
| `numeric` | 数値計算としてのドメイン知識（numpy のみに依存し、単体でも使える公開 API） |
| `domains.*.collection` | 荷重-変位・座標・ひずみの意味づけ（設定の保持と、設定を読む問い合わせ） |
| `core.io` | TASC などファイル形式の解釈 |
| `core.plot` / `domains.*.plotter` | 描画（汎用 / ドメイン固有） |

## ColumnCollection

```python
coll.df        # pl.DataFrame（インデックス列 + データ列）
coll.meta      # {列名: ColumnMeta}（データ列のみ、列順どおり）
coll.metadata  # コレクション全体のメタデータ
coll.results   # {名前: AnalysisResult}
```

- **不変 (immutable)**。属性への代入や、列・メタデータを直接書き換える API はありません。変更はすべて `with_*` などのメソッドで行い、新しいコレクションが返ります。
- **インデックス列**: `step` は必須、`date` と `time` は任意です。この3つは予約名で、データ列には使えません。`coll.columns` にはデータ列だけが入ります。
- step を省略した場合は `0..n-1` になります。

### 読み取り

| API | 戻り値 |
|---|---|
| `coll["CH1"]` | `Column`（データ列の読み取り専用ビュー） |
| `coll[i]` | `Row` |
| `coll[a:b]` | `ColumnCollection` |
| `coll.by_ch("CH01")` | `Column`（チャンネル名で検索） |
| `coll.step` / `coll.date` / `coll.time` | `np.ndarray`（`date` と `time` は存在しなければ `None`） |
| `coll.columns` | データ列名のリスト |
| `coll.units` | `{列名: 単位}` |
| `coll.results["stiffness"]` | 解析結果 |

`coll[...]` は列名だけを受け付けます。チャンネル名や解析結果を暗黙に探すことはしません。

### 書き込み（新しいコレクションを返す）

| API | 内容 |
|---|---|
| `with_column(name, values, unit=, ch=, attrs=)` | 列を追加・上書きする。上書き時は、指定しなかったメタを引き継ぐ |
| `with_meta(name, unit=, ch=, attrs=)` | 列メタを変更する |
| `with_metadata(**items)` / `with_result(result)` | コレクションのメタデータ・解析結果を追加する |
| `select(names)` / `drop(*names)` / `rename(mapping)` | 列の選択・削除・改名（メタも追従する） |
| `take(rows)` / `head(n)` / `tail(n)` | 行の抽出（インデックス配列またはブールマスク） |

### 入口と出口

```python
ColumnCollection({"P": [...], "d": [...]}, step=[...], units={"P": "kN", "d": "mm"})
ColumnCollection.from_frame(df, step="time", units={"P": "kN"})
coll.df  # polars をそのまま使いたい場合の出口
```

## Column と Row

- `Column` は `name`、`meta`、`series`（`pl.Series`）を束ねた読み取り専用のビューです。`Column(name, values, unit=..., ch=...)` で単体でも作れます（`XYSeriesResult` などで使用）。
- `col.values` は `np.ndarray` を返します。数値列は float64 で、欠損は NaN になります。それ以外の列は object 配列で、欠損は `None` です。
- `col[i]` はスカラー（Python の値、欠損は `None`）を返します。集約メソッド（`max` / `min` / `mean` など）も Python スカラーまたは `None` を返します。
- `Row` は1行分の値です。`row["CH1"]`、`row.step`、`row.unit("CH1")`、`row.units` を持ちます。値は素のスカラーで、単位を値に包むことはしません。

## dtype と欠損の規則

- データ列の数値は常に **Float64** に統一します（int も float にします）。step は元の dtype のままにします。
- 内部の欠損は **null** に統一します。入力に含まれる NaN は null に変換し、ops の計算結果に出た NaN も null として格納します。
- 文字列・真偽値・日時はそのままの dtype で保持します。数値と文字列が混在する列は文字列列になります。
- io で欠損とみなすトークン: `none`、`null`、`nan`、`na`、空文字、`*` で始まる値。

## ファイル入出力

| 方法 | 形式 | 保持される情報 |
|---|---|---|
| `tascpy.load` / `coll.io.save` | TASC 系テキスト（4行ヘッダー、`tasc_txt` は Shift-JIS） | 列名・ch・単位・step・date/time |
| `tascpy.load_parquet` / `coll.io.to_parquet` | Parquet | 上記に加えて単位の None と "" の区別、attrs、メタデータ、解析結果、ドメイン設定 |
| `coll.io.to_csv` | 一般的な CSV（1行ヘッダー、UTF-8） | 列名と値のみ |

- テキスト形式の保存では、名前行に列名、チャンネル行に ch を書くため、保存→読み込みで列名と ch が保たれます。
- テキスト形式では、単位の None と "" はどちらも空欄になります。文字列値の `none` や `*` で始まる値は、読み込み時に欠損になります。
- 保存は全体をエンコードしてから一時ファイル経由で置き換えます。エンコーディングで表せない文字があればエラーになり、既存ファイルは変更されません。
- ops が合成する単位や列名には、Shift-JIS で表せる文字だけを使います（例: `kN*mm`）。
- 読み込み時、名前が空欄の列はチャンネル名で補います。列名の重複や予約名（step / date / time）には `_2` などの接尾辞を付け、警告を出します。

## 単位の方針

- **単位は記録して確認するためのものです。自動変換はしません。**
- `None` は「不明」、`""` は「単位なし（無次元）が明示されている」を意味します。わからない単位を推測で付けることはしません。
- ops では、明示的に指定された `unit=` が常に優先されます。指定がない場合は次の規則に従います。

| 演算 | 結果の単位 |
|---|---|
| add / subtract、行方向の平均・合計、平滑化（移動平均・ガウシアン）、abs / round、switch / blend / conditional_select | 最初の列オペランドの単位 |
| 列 × スカラー、列 ÷ スカラー | その列の単位 |
| 列 × 列、列 ÷ 列、pow / sqrt / log、calculate、custom_combine | `None` |
| normalize、外れ値フラグ、サイクル番号、ピーク／バレーのマーカー | `""` |
| diff / integrate | `"y/x"` / `"y*x"`（表記を合成するだけ。Shift-JIS で保存できる文字に限る） |
| 行の抽出・分割・連結 | 元の単位を保持 |

## numeric の約束

numeric は、TASC 以外のデータにも単体で使えるように、numpy だけに依存する純粋関数として保ちます。

- 入力: 1次元の配列風データ（list / ndarray）。内部で `np.asarray(..., dtype=float)` に変換します。
- 欠損: NaN で表します（`None` は入力として受け付けますが、出力には使いません）。
- 戻り値: `np.ndarray`、スカラー、tuple、または dataclass。
- 単位・列名・コレクションは扱いません。
- import するのは numpy（と標準ライブラリ）だけです。tascpy の他のサブパッケージや polars・matplotlib に依存しません（import-linter の契約で検査）。
- モジュールは tascpy のドメインではなく解析の対象で分けます（`curve` / `hysteresis` / `rosette` / `spatial` と、汎用の `math` / `stats` / `combine`）。
- 引数は常に (x, y) の順に並べます。汎用の x-y 曲線（`curve`）は `x, y`、荷重-変位に固有の処理（`hysteresis`）は `displacement, load` と名付けます。1次元の系列は `values` です。
- 解析結果を返す関数は `compute_` で始めます（`compute_skeleton_curve` など）。広く通じる操作の名前（`interpolate`、`moving_average`、`euclidean_distance`、`kmeans`）はそのまま使います。
- numpy の関数をそのまま呼ぶだけのラッパーや、ops のためだけの部品は公開しません（`_` 付きにするか、ops の側に置きます）。

表を操作する処理（行の抽出・検索・分割・重複除去など）は ops の側で polars を使って実装し、numeric には置きません。

## 可視化

- 描画関数とプロッター（`coll.plot`）は Axes（`iplot` は Plotly Figure）を返すだけで、`plt.show()` は呼びません。表示は呼び出し側で行います（Jupyter では自動で表示されます）。
- 軸ラベルは列名と単位から "列名 [単位]" で作ります。X 軸の列を省略すると step を使います。
- matplotlib は描画を使うまで読み込みません（`import tascpy` やデータの読み込み・演算だけなら不要です）。`tascpy.core.plot` を初めて import したときに変更する設定は、日本語フォント（japanize-matplotlib 同梱の IPAex ゴシック）の font.family と axes.unicode_minus だけです。

## ドメイン

- ドメインのコレクションは `ColumnCollection` のサブクラスです。ドメイン固有の設定（荷重-変位の `load_column` / `displacement_column`、ひずみの `rosettes`）は属性として持ち、`with_*` で操作しても引き継がれます。
- 変換は `ops.as_domain(as_load_displacement, ...)`、`ops.as_domain(as_coordinate, ...)`、`ops.as_domain(as_strain, ...)` で行います。設定が不正な場合（列が存在しない場合など）はその時点でエラーになります。
- コレクションが持つのは設定と、設定を読むだけの問い合わせ（`get_column_coordinates`、`calculate_distance` など）です。新しい列や結果を作る処理は ops に置きます（`nearest_neighbors`、`clusters` は `CoordinateOps`）。
- 座標は列ごとの値なので、`ColumnMeta.attrs["coordinates"]`（`{"x", "y", "z"}`）に持ちます。こうしておけば、列の改名や選択に自動で追従します。
