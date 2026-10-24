# Numeric モジュール

`tascpy.numeric` の API リファレンスです。numpy の配列を受け取って配列・値を返す解析関数で、tascpy のコレクションを使わずに単体で使えます。

```python
import numpy as np
from tascpy.numeric.hysteresis import compute_cumulative_curve, compute_cycle_markers

load = np.array([0, 10, 0, -10, 0, 15, 0])
disp = np.array([0, 1, 2, 1, 0, 1.5, 2.5])
markers = compute_cycle_markers(load)
d_cum, p_cum = compute_cumulative_curve(load, disp, markers)
```

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
