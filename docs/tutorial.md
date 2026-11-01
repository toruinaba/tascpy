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

`end_as` に変換関数 `tascpy.as_load_displacement` と、荷重列・変位列を渡します。チェーンはここで終わり、荷重-変位ドメインのコレクションが返ります。その `ops` では `to_skeleton_curve` や `yield_point` などの操作が使えるようになります（IDE でも補完されます）。

```pycon
>>> ld = col.ops.end_as(tascpy.as_load_displacement, load_column="荷重", displacement_column="変位")
>>> type(ld).__name__, type(ld.ops).__name__
('LoadDisplacementCollection', 'LoadDisplacementOps')

```

操作は戻り値によって次のように分かれ、名前で見分けられます（ほかに、汎用のコレクションに戻す `as_core`、ドメインのコレクションに変換してチェーンを終える `end_as`、分割する `split_*` があります）。

- 列を足す・行を絞るなどの変換（`mark_cycles`、`select` など）は、同じ操作オブジェクトを返してチェーンが続きます。最後に `end()` でコレクションを取り出します。
- `to_` で始まる操作（`to_skeleton_curve`、`to_hysteresis_table` など）は、新しい表のコレクションに変わります。チェーンはその表で続きます。
- 名詞の操作（`stiffness`、`yield_point`）は値を求めて返し、チェーンはそこで終わります。

## 4. スケルトン曲線を求める

`to_skeleton_curve` はスケルトン曲線を求め、曲線そのものを新しい荷重-変位コレクションとして返します。列は荷重・変位（サイクルごとにずらした値）と、各点の元データのステップ `source_step` だけで、単位は元の列から引き継ぎます。サイクルは荷重の符号の反転から数えます。

```pycon
>>> skeleton = ld.ops.to_skeleton_curve().end()
>>> skeleton.columns
['荷重', '変位', 'source_step']
>>> round(float(skeleton.displacement_data.max()), 1), skeleton.displacement.unit, round(float(skeleton.load_data.max()), 1), skeleton.load.unit
(6.0, 'mm', 114.0, 'kN')

```

負側のスケルトン曲線は `side="negative"` で求めます（荷重・変位とも負の値です）。`to_cumulative_curve` も同じく `side=` を受け取ります。

```pycon
>>> negative = ld.ops.to_skeleton_curve(side="negative").end()
>>> round(float(negative.displacement_data.min()), 1), round(float(negative.load_data.min()), 1)
(-7.4, -114.0)

```

サイクル番号を列として見たいときや、数え方を変えたいときは `mark_cycles` で列を作ります。作った列をサイクルを使う操作に使うときは、`cycle_column` で列名を渡します。

```pycon
>>> cycled = ld.ops.mark_cycles(result_column="荷重_cycle").end()
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
>>> round(ld.ops.to_skeleton_curve().yield_point(offset_value=0.5, range_start=0.1, range_end=0.5).x, 2)
3.06

```

繰り返し載荷の生データに `stiffness` や `yield_point` をそのまま使うと、範囲に入る除荷途中の点も計算に含まれ、エラーにならずに誤った値になります。初期剛性だけが必要なら、荷重が初めて下がる手前までの最初の載荷区間を抜き出して使うこともできます。

```pycon
>>> round(ld.ops.stiffness(range_start=0.1, range_end=0.5).value, 1)  # 生データのまま（誤り）
1.5
>>> first_loading = col.head(int(np.argmax(np.diff(col["荷重"].values) < 0)) + 1)
>>> len(first_loading), first_loading["荷重"].max()
(20, 80.0)
>>> first = first_loading.ops.end_as(tascpy.as_load_displacement, load_column="荷重", displacement_column="変位")
>>> round(first.ops.stiffness(range_start=0.1, range_end=0.5).value, 1)
40.0

```

最初の載荷区間（±2 mm）はまだ弾性範囲なので、降伏点はこの区間からは求まりません。降伏点は上のようにスケルトン曲線から求めます。

## 6. サイクルごとに集計する

`to_hysteresis_table` はサイクルごとの履歴エネルギー（ループの面積）と、荷重・変位の最大・最小を表にして返します。表のステップはサイクル番号です。

```pycon
>>> table = ld.ops.to_hysteresis_table().end()
>>> table.step.tolist()
[1, 2, 3, 4]
>>> table["energy"].values.round(1), table["energy"].unit
(array([   0. ,  407. , 1103.8,   35.6]), 'kN*mm')
>>> table["max_load"].values
array([ 80., 106., 114.,  90.])

```

1 サイクル目（±2 mm）は弾性範囲なのでエネルギーは 0 です。4 サイクル目は最後に 0 mm へ戻る途中までの部分です。

サイクルごとに好きな値を集めるときは、`split_by_cycles` でサイクルごとに分け、`collect` で各サイクルの値を求めます。`collect` の結果はそのままリストとして使え、`to_table(name=...)` で 1 サイクル 1 行の表（ステップはサイクル番号）にできます。ステップが同じ表は `join` で横に並べられます。

```pycon
>>> cycles = ld.ops.split_by_cycles()
>>> peak = cycles.collect(lambda o: o.end()["荷重"].max())
>>> peak, peak.keys
([80.0, 106.0, 114.0, 90.0], [1, 2, 3, 4])
>>> per_cycle = peak.to_table(name="peak").join(ld.ops.to_stiffness_table()).end()
>>> per_cycle.columns, per_cycle["stiffness"].unit
(['peak', 'stiffness'], 'kN/mm')

```

データの行そのものを選ぶ `nearest_row` を集めると、元の列名・単位のままの表になります（元の行のステップは `source_step`）。表は荷重-変位のまま引き継がれます。

```pycon
>>> peaks = cycles.collect(lambda o: o.nearest_row("荷重", o.end()["荷重"].max())).to_table()
>>> type(peaks).__name__, peaks.end()["変位"].values, peaks.end()["source_step"].values
('LoadDisplacementOps', array([2., 4., 6., 0.]), array([ 19.,  59.,  99., 139.]))

```

### 反転点ごとに分けて再降伏点を見る

`split_by_cycles` は荷重が 0 をまたぐ位置で切るため、ピークからの除荷と逆方向の再降伏が別のサイクルに分かれます。除荷からの再降伏点（バウシンガー効果による降伏点の推移）を見るときは、`split_by_reversals` で正側・負側のピーク（反転点）から次のピークまでの半サイクルに分けます。反転は、直前の反転点からの片振幅に対して `ratio`（既定 5%）以上戻った時点で確定します。隣り合う区間は境界のピークを共有します。

```pycon
>>> halves = ld.ops.split_by_reversals()
>>> halves.keys, [c["変位"].values[[0, -1]].tolist() for c in halves.end()]
([1, 2, 3, 4, 5, 6, 7], [[0.1, 2.0], [2.0, -2.0], [-2.0, 4.0], [4.0, -4.0], [-4.0, 6.0], [6.0, -6.0], [-6.0, 0.0]])

```

各区間を `shift_origin` で始点（ピーク）が原点になるよう平行移動すると、`yield_point` と `stiffness` がそのまま使え、剛性も区間ごとの除荷剛性から求まります。移動量は metadata の `origin_load` / `origin_displacement` に記録されるので、足し戻すと元の座標の降伏荷重になります。

```pycon
>>> shifted = halves.map(lambda o: o.shift_origin())
>>> points = shifted.collect(lambda o: o.yield_point(offset_value=0.5, range_start=0.1, range_end=0.5,
...                                                  fail_silently=True))
>>> origin = shifted.collect(lambda o: o.end().metadata["origin_load"])
>>> reyield = points.to_table(name="yield").join(origin.to_table(name="origin_load")).end()
>>> reyield["yield_y"].values.round(1)
array([   nan,    nan,  182.2, -202.2,  202.2, -202.2,  202.2])
>>> (reyield["yield_y"].values + reyield["origin_load"].values).round(1)
array([   nan,    nan,  102.2,  -96.2,   96.2,  -88.2,   88.2])

```

±2 mm の区間は弾性範囲で折り返すので降伏点は求まりません（欠損）。移動硬化のばねなので、反転後の降伏荷重は経験した最大荷重が大きいほど低くなります。

### 再降伏点を累積曲線の上に置く

再降伏点を繰り返しの履歴に沿って並べるには、累積曲線（`to_cumulative_curve`。正側・負側それぞれ、荷重 0 の点から荷重 0 の点までの区間を変位方向につないだ曲線）の上の位置を使います。`mark_cumulative` で各行の累積曲線の上での位置を列にしておくと、`split_by_reversals` の区間にも引き継がれます。降伏点の位置での値は `value_at` で求めます（`yield_point` の結果の metadata にある、降伏点の行の位置 `row_position` を使って前後の行を補間します）。

```pycon
>>> marked = ld.ops.mark_cumulative(result_column="累積+").mark_cumulative(side="negative", result_column="累積-")
>>> shifted = marked.split_by_reversals().map(lambda o: o.shift_origin())
>>> def on_cumulative(o, column):
...     pt = o.yield_point(offset_value=0.5, range_start=0.1, range_end=0.5, fail_silently=True)
...     return o.value_at(pt, column)
>>> positive = shifted.collect(lambda o: on_cumulative(o, "累積+")).to_table(name="累積+").end()
>>> negative = shifted.collect(lambda o: on_cumulative(o, "累積-")).to_table(name="累積-").end()
>>> positive["累積+"].values.round(2), positive["累積+"].unit
(array([ nan,  nan, 3.06,  nan, 4.26,  nan, 8.56]), 'mm')
>>> negative["累積-"].values.round(2)
array([  nan,   nan,   nan, -2.91,   nan, -5.41,   nan])

```

正側の降伏点は正側の累積曲線、負側の降伏点は負側の累積曲線の上にだけ値があります（反対側の列は欠損です）。たとえば 5 番目の半サイクル（-4 → +6 mm）の降伏点は、それまでの正側の残留変形 1.35 mm から始まる区間の上にあり、位置は 4.26 mm です。`to_cumulative_curve` の曲線と同じ座標なので、重ねて描けます。

### 再降伏点を累積塑性変形に対して並べる

累積曲線は正側・負側を別々につないだもので、荷重 0 を区切りにしています。正負の両方向の塑性履歴を1本の軸で数えたいときは、反転点で区切った半サイクルごとの塑性変形を累積する `mark_cumulative_plastic` を使います。半サイクルの区切りは `split_by_reversals` と同じで、半サイクルごとに反転点を原点とした剛性 K を求め（`yield_point` の初期剛性と同じ求め方なので、`range_start` / `range_end` は `yield_point` とそろえます）、載荷の向きへの塑性変形 Δd − ΔP/K を足していきます。値はすべての行にあり、単調に増えます。

半サイクルの先頭の行の値が「その反転に入るまでの累積塑性変形」です。

```pycon
>>> kw = {"range_start": 0.1, "range_end": 0.5}
>>> marked = ld.ops.mark_cumulative_plastic(result_column="累積塑性", **kw)
>>> shifted = marked.split_by_reversals().map(lambda o: o.shift_origin())
>>> before = shifted.collect(lambda o: float(o.end()["累積塑性"].values[0]))
>>> [round(v, 2) for v in before]
[0.0, 0.0, 0.0, 1.35, 4.05, 8.55, 14.85]

```

降伏点の位置での値を `value_at` で読むと、オフセット法の定義上、先頭の値にオフセット量（0.5 mm）を足したものになります。どちらを横軸にしても、点の並びは同じです。

```pycon
>>> def at_yield(o):
...     pt = o.yield_point(offset_value=0.5, fail_silently=True, **kw)
...     return o.value_at(pt, "累積塑性")
>>> shifted.collect(at_yield).to_table(name="累積塑性").end()["累積塑性"].values.round(2)
array([  nan,   nan,  0.5 ,  1.85,  4.55,  9.05, 15.35])

```

上で求めた再降伏荷重（102.2, −96.2, 96.2, −88.2, 88.2 kN）を、この値に対して正側・負側の系列に分けて描くと、累積塑性変形に伴う降伏点の推移になります。

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
