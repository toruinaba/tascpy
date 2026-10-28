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

`as_domain` に変換関数 `tascpy.as_load_displacement` と、荷重列・変位列を渡します。戻り値は荷重-変位ドメインの操作オブジェクトで、`cycle_count` や `skeleton_curve` などの操作が使えるようになります（IDE でも補完されます）。

```pycon
>>> ld = col.ops.as_domain(tascpy.as_load_displacement, "荷重", "変位")
>>> type(ld).__name__
'LoadDisplacementOps'

```

## 4. サイクルを数えてスケルトン曲線を求める

`cycle_count` は荷重の符号の反転からサイクル番号の列を追加します。操作はつなげて書き、最後に `end()` でコレクションを取り出します。

```pycon
>>> cycled = ld.cycle_count().end()
>>> cycled.columns
['荷重', '変位', '荷重_cycle']
>>> cycled["荷重_cycle"].values[::20]
array([1., 1., 2., 2., 3., 3., 4.])

```

`skeleton_curve` はそのサイクル番号を使ってスケルトン曲線を求め、曲線そのものを新しい荷重-変位コレクションとして返します。列は荷重・変位（サイクルごとにずらした値）と、各点の元データのステップ `source_step` だけで、単位は元の列から引き継ぎます。

```pycon
>>> skeleton = cycled.ops.skeleton_curve().end()
>>> skeleton.columns
['荷重', '変位', 'source_step']
>>> round(float(skeleton.displacement_data.max()), 1), skeleton.displacement.unit, round(float(skeleton.load_data.max()), 1), skeleton.load.unit
(6.0, 'mm', 114.0, 'kN')

```

元データの他の列（サイクル番号など）が必要なときは、`source_step` で元データから行を取り出します。

```pycon
>>> rows = cycled.ops.select(steps=skeleton["source_step"].values.tolist()).end()
>>> np.allclose(rows["荷重"].values, skeleton.load_data), sorted(set(rows["荷重_cycle"].values.tolist()))
(True, [1.0, 2.0, 3.0])

```

## 5. 剛性と降伏点を求める

剛性と降伏点は単調な曲線を前提にした計算なので、繰り返し載荷のデータではスケルトン曲線から求めます。スケルトン曲線も荷重-変位コレクションなので、そのまま操作をつなげられます。

```pycon
>>> analyzed = (skeleton.ops.calculate_stiffness(range_start=0.1, range_end=0.5)
...             .find_yield_point(method="offset", offset_value=0.5, range_start=0.1, range_end=0.5).end())
>>> stiffness, point = analyzed.results["stiffness"], analyzed.results["yield_point"]
>>> round(stiffness.value, 1), stiffness.unit
(40.0, 'kN/mm')
>>> point.metadata["is_valid"], round(point.x, 2), round(point.y, 1)
(True, 3.06, 102.2)

```

初期剛性 40 kN/mm の直線を変位方向に 0.5 mm ずらした直線と、スケルトン曲線の交点が降伏点です。

繰り返し載荷の生データに `calculate_stiffness` や `find_yield_point` をそのまま使うと、範囲に入る除荷途中の点も計算に含まれ、エラーにならずに誤った値になります。初期剛性だけが必要なら、荷重が初めて下がる手前までの最初の載荷区間を抜き出して使えます。

```pycon
>>> round(ld.calculate_stiffness(range_start=0.1, range_end=0.5).end().results["stiffness"].value, 1)  # 生データのまま（誤り）
1.5
>>> first_loading = col.head(int(np.argmax(np.diff(col["荷重"].values) < 0)) + 1)
>>> len(first_loading), first_loading["荷重"].max()
(20, 80.0)
>>> first = first_loading.ops.as_domain(tascpy.as_load_displacement, "荷重", "変位")
>>> round(first.calculate_stiffness(range_start=0.1, range_end=0.5).end().results["stiffness"].value, 1)
40.0

```

最初の載荷区間（±2 mm）はまだ弾性範囲なので、降伏点はこの区間からは求まりません。降伏点は上のようにスケルトン曲線から求めます。

## 6. サイクルごとに集計する

`analyze_hysteresis` はサイクルごとの履歴エネルギー（ループの面積）と、荷重・変位の最大・最小を表にして返します。表のステップはサイクル番号です。

```pycon
>>> table = cycled.ops.analyze_hysteresis().end()
>>> table.step.tolist()
[1, 2, 3, 4]
>>> table["energy"].values.round(1), table["energy"].unit
(array([   0. ,  407. , 1103.8,   35.6]), 'kN*mm')
>>> table["max_load"].values
array([ 80., 106., 114.,  90.])

```

1 サイクル目（±2 mm）は弾性範囲なのでエネルギーは 0 です。4 サイクル目は最後に 0 mm へ戻る途中までの部分です。

## 7. 描画する

`plot` のメソッドは matplotlib の Axes を返します（表示は呼び出し側で行います。Jupyter では自動で表示されます）。元データとスケルトン曲線は、同じ Axes にそれぞれのコレクションから描画して重ねます。

```pycon
>>> ax = cycled.plot.plot_load_displacement(color="gray", label="元データ")
>>> ax = skeleton.plot.plot_load_displacement(ax=ax, color="red", label="スケルトン曲線")
>>> ax.get_xlabel(), ax.get_ylabel(), len(ax.lines)
('変位 [mm]', '荷重 [kN]', 2)
>>> ax = analyzed.plot.plot_yield_point()  # スケルトン曲線と降伏点

```

## 8. 保存する

Parquet 形式で保存すると、列の単位に加えて、解析結果とドメインの設定（荷重列・変位列）も復元できます。

```pycon
>>> analyzed.io.to_parquet("skeleton.parquet")
>>> restored = tascpy.load_parquet("skeleton.parquet")
>>> type(restored).__name__, restored.load_column, list(restored.results)
('LoadDisplacementCollection', '荷重', ['stiffness', 'yield_point'])

```

## 9. numpy の配列だけで計算する

`tascpy.numeric` の関数は、tascpy のコレクションを使わずに numpy の配列に直接使えます。サイクル番号を省略すると、荷重の符号の反転から数えます（`cycle_count` と同じ規則です）。結果は 4・5 で求めたものと一致します。

```pycon
>>> from tascpy.numeric.curve import compute_yield_point
>>> from tascpy.numeric.hysteresis import compute_skeleton_curve
>>> d_ske, p_ske = compute_skeleton_curve(disp, np.array(load))
>>> np.allclose(d_ske, skeleton.displacement_data), np.allclose(p_ske, skeleton.load_data)
(True, True)
>>> round(compute_yield_point(d_ske, p_ske, offset_value=0.5, range_start=0.1, range_end=0.5).x, 2)
3.06

```
