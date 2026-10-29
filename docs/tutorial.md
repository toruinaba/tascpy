# チュートリアル: 繰り返し載荷試験の解析

繰り返し載荷の荷重-変位データを読み込み、スケルトン曲線・剛性・降伏点・サイクルごとの履歴エネルギーを求めて保存するまでを、途中の結果を確かめながら順に進めます。

このページのコードはそのまま実行でき、表示している結果は CI で検査しています（`pytest` が doctest として実行します）。

## 1. データを用意する

実験データの代わりに、初期剛性 40 kN/mm・降伏荷重 100 kN・二次剛性 4 kN/mm のバイリニア（移動硬化）のばねを、変位の振幅を ±2 → ±4 → ±6 mm と増やしながら繰り返し載荷したデータを作ります。

```pycon
>>> import numpy as np
>>> import tascpy
>>> peaks = [2.0, -2.0, 4.0, -4.0, 6.0, -6.0]
>>> disp = np.concatenate([np.linspace(a, b, 21)[1:] for a, b in zip([0.0] + peaks, peaks + [0.0])])
>>> load, p = [], 0.0
>>> for d0, d1 in zip(np.r_[0.0, disp[:-1]], disp):
...     p = min(max(p + 40.0 * (d1 - d0), 4.0 * d1 - 90.0), 4.0 * d1 + 90.0)
...     load.append(p)

```

列の値と単位を渡してコレクションを作ります。

```pycon
>>> col = tascpy.ColumnCollection({"荷重": load, "変位": disp}, units={"荷重": "kN", "変位": "mm"})
>>> len(col), col.units
(140, {'荷重': 'kN', '変位': 'mm'})

```

## 2. TASC 形式で保存して読み込む

実際の解析では、計測した TASC のファイルを `tascpy.load` で読み込むところから始めます。ここでは作ったデータを一度保存し、読み込み直します。列名と単位はファイルに保存され、読み込むと元に戻ります。

```pycon
>>> col.io.save("experiment.txt")
>>> col = tascpy.load("experiment.txt")
>>> col.columns, col["荷重"].unit, col["変位"].unit
(['荷重', '変位'], 'kN', 'mm')

```

## 3. 荷重-変位ドメインに変換する

`as_domain` に変換関数 `tascpy.as_load_displacement` と、荷重列・変位列を渡します。戻り値は荷重-変位ドメインの操作オブジェクトで、`to_skeleton_curve` や `yield_point` などの操作が使えるようになります（IDE でも補完されます）。

```pycon
>>> ld = col.ops.as_domain(tascpy.as_load_displacement, load_column="荷重", displacement_column="変位")
>>> type(ld).__name__
'LoadDisplacementOps'

```

操作は戻り値によって3種類あり、名前で見分けられます。

- 列を足す・行を絞るなどの変換（`mark_cycles`、`select` など）は、同じ操作オブジェクトを返してチェーンが続きます。最後に `end()` でコレクションを取り出します。
- `to_` で始まる操作（`to_skeleton_curve`、`to_hysteresis_table` など）は、新しい表のコレクションに変わります。チェーンはその表で続きます。
- 名詞の操作（`stiffness`、`yield_point`）は値を求めて返し、チェーンはそこで終わります。

## 4. スケルトン曲線を求める

`to_skeleton_curve` はスケルトン曲線を求め、曲線そのものを新しい荷重-変位コレクションとして返します。列は荷重・変位（サイクルごとにずらした値）と、各点の元データのステップ `source_step` だけで、単位は元の列から引き継ぎます。サイクルは荷重の符号の反転から数えます。

```pycon
>>> skeleton = ld.to_skeleton_curve().end()
>>> skeleton.columns
['荷重', '変位', 'source_step']
>>> round(float(skeleton.displacement_data.max()), 1), skeleton.displacement.unit, round(float(skeleton.load_data.max()), 1), skeleton.load.unit
(6.0, 'mm', 114.0, 'kN')

```

サイクル番号を列として見たいときや、数え方を変えたいときは `mark_cycles` で列を作ります。作った列をサイクルを使う操作に使うときは、`cycle_column` で列名を渡します。

```pycon
>>> cycled = ld.mark_cycles().end()
>>> cycled.columns
['荷重', '変位', '荷重_cycle']
>>> cycled["荷重_cycle"].values[::20]
array([1., 1., 2., 2., 3., 3., 4.])
>>> same = cycled.ops.to_skeleton_curve(cycle_column="荷重_cycle").end()
>>> np.allclose(same.load_data, skeleton.load_data)
True

```

元データの他の列（サイクル番号など）が必要なときは、`source_step` で元データから行を取り出します。

```pycon
>>> rows = cycled.ops.select(steps=skeleton["source_step"].values.tolist()).end()
>>> np.allclose(rows["荷重"].values, skeleton.load_data), sorted(set(rows["荷重_cycle"].values.tolist()))
(True, [1.0, 2.0, 3.0])

```

## 5. 剛性と降伏点を求める

剛性と降伏点は単調な曲線を前提にした計算なので、繰り返し載荷のデータではスケルトン曲線から求めます。`stiffness` と `yield_point` は単位付きの結果を返します。

```pycon
>>> stiffness = skeleton.ops.stiffness(range_start=0.1, range_end=0.5)
>>> round(stiffness.value, 1), stiffness.unit
(40.0, 'kN/mm')
>>> point = skeleton.ops.yield_point(method="offset", offset_value=0.5, range_start=0.1, range_end=0.5)
>>> point.metadata["is_valid"], round(point.x, 2), point.x_unit, round(point.y, 1), point.y_unit
(True, 3.06, 'mm', 102.2, 'kN')

```

初期剛性 40 kN/mm の直線を変位方向に 0.5 mm ずらした直線と、スケルトン曲線の交点が降伏点です。チェーンの最後に書くこともできます。

```pycon
>>> round(ld.to_skeleton_curve().yield_point(offset_value=0.5, range_start=0.1, range_end=0.5).x, 2)
3.06

```

繰り返し載荷の生データに `stiffness` や `yield_point` をそのまま使うと、範囲に入る除荷途中の点も計算に含まれ、エラーにならずに誤った値になります。初期剛性だけが必要なら、荷重が初めて下がる手前までの最初の載荷区間を抜き出して使うこともできます。

```pycon
>>> round(ld.stiffness(range_start=0.1, range_end=0.5).value, 1)  # 生データのまま（誤り）
1.5
>>> first_loading = col.head(int(np.argmax(np.diff(col["荷重"].values) < 0)) + 1)
>>> len(first_loading), first_loading["荷重"].max()
(20, 80.0)
>>> first = first_loading.ops.as_domain(tascpy.as_load_displacement, load_column="荷重", displacement_column="変位")
>>> round(first.stiffness(range_start=0.1, range_end=0.5).value, 1)
40.0

```

最初の載荷区間（±2 mm）はまだ弾性範囲なので、降伏点はこの区間からは求まりません。降伏点は上のようにスケルトン曲線から求めます。

## 6. サイクルごとに集計する

`to_hysteresis_table` はサイクルごとの履歴エネルギー（ループの面積）と、荷重・変位の最大・最小を表にして返します。表のステップはサイクル番号です。

```pycon
>>> table = ld.to_hysteresis_table().end()
>>> table.step.tolist()
[1, 2, 3, 4]
>>> table["energy"].values.round(1), table["energy"].unit
(array([   0. ,  407. , 1103.8,   35.6]), 'kN*mm')
>>> table["max_load"].values
array([ 80., 106., 114.,  90.])

```

1 サイクル目（±2 mm）は弾性範囲なのでエネルギーは 0 です。4 サイクル目は最後に 0 mm へ戻る途中までの部分です。

## 7. 描画する

`plot` のメソッドは matplotlib の Axes を返します（表示は呼び出し側で行います。Jupyter では自動で表示されます）。元データとスケルトン曲線は、同じ Axes にそれぞれのコレクションから描画して重ねます。降伏点は `yield_point` の結果を渡して描画します。

```pycon
>>> ax = col.plot.plot(x_column="変位", y_column="荷重", color="gray", label="元データ")
>>> ax = skeleton.plot.plot_load_displacement(ax=ax, color="red", label="スケルトン曲線")
>>> ax.get_xlabel(), ax.get_ylabel(), len(ax.lines)
('変位 [mm]', '荷重 [kN]', 2)
>>> ax = skeleton.plot.plot_yield_point(point)  # スケルトン曲線と降伏点

```

## 8. 保存する

Parquet 形式で保存すると、列の単位とドメインの設定（荷重列・変位列）を復元できます。解析結果も一緒に保存したいときは、`with_result` でコレクションに付けてから保存します。

```pycon
>>> skeleton.with_result(stiffness).with_result(point).io.to_parquet("skeleton.parquet")
>>> restored = tascpy.load_parquet("skeleton.parquet")
>>> type(restored).__name__, restored.load_column, list(restored.results)
('LoadDisplacementCollection', '荷重', ['stiffness', 'yield_point'])

```

## 9. numpy の配列だけで計算する

`tascpy.numeric` の関数は、tascpy のコレクションを使わずに numpy の配列に直接使えます。サイクル番号を省略すると、荷重の符号の反転から数えます（`to_skeleton_curve` と同じ規則です）。結果は 4・5 で求めたものと一致します。

```pycon
>>> from tascpy.numeric.curve import compute_yield_point
>>> from tascpy.numeric.hysteresis import compute_skeleton_curve
>>> d_ske, p_ske = compute_skeleton_curve(disp, np.array(load))
>>> np.allclose(d_ske, skeleton.displacement_data), np.allclose(p_ske, skeleton.load_data)
(True, True)
>>> round(compute_yield_point(d_ske, p_ske, offset_value=0.5, range_start=0.1, range_end=0.5).x, 2)
3.06

```
