# Numeric モジュール

`tascpy.numeric` の API リファレンスです。numpy の配列を受け取って配列・値を返す解析関数で、tascpy のコレクションを使わずに単体で使えます。

```python
import numpy as np
from tascpy.numeric.hysteresis import compute_cumulative_curve, compute_skeleton_curve

disp = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0])
load = np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0])

# サイクル番号（markers）は省略すると荷重の符号反転から数える
d_ske, p_ske = compute_skeleton_curve(disp, load)
d_cum, p_cum = compute_cumulative_curve(disp, load)
```

引数は常に (x, y) の順です。汎用の x-y 曲線（`curve`）は `x, y`、繰り返し載荷（`hysteresis`）は `displacement, load` と書きます。

## Math
::: tascpy.numeric.math

## Stats
::: tascpy.numeric.stats

## Combine
::: tascpy.numeric.combine

## Curve
::: tascpy.numeric.curve

## Hysteresis
::: tascpy.numeric.hysteresis

## Rosette
::: tascpy.numeric.rosette

## Spatial
::: tascpy.numeric.spatial
