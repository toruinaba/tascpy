# 例で使うデータ

API リファレンスの docstring の例（`Examples`）は、次の `col` / `ld` / `coord` / `strain` / `cyclic` を前提にしています。

- `col`: 荷重・変位と、3 つのひずみゲージ（CH1〜CH3、直交ロゼット R1）を 6 ステップ分記録したデータ（単調載荷）
- `ld` / `coord` / `strain`: `col` を荷重-変位・座標・ひずみの各ドメインに変換したもの
- `cyclic`: 繰り返し載荷の荷重-変位データ（初期剛性 40 kN/mm・降伏荷重 100 kN・二次剛性 4 kN/mm のバイリニアのばねを、変位 ±2 mm のあと +4 mm まで載荷）

```python
import numpy as np
import tascpy
from tascpy.domains import as_coordinate, as_load_displacement, as_strain

col = tascpy.ColumnCollection(
    {
        "荷重": [0.0, 40.0, 80.0, 100.0, 110.0, 115.0],
        "変位": [0.0, 1.0, 2.0, 3.0, 5.0, 8.0],
        "CH1": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0],
        "CH2": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0],
        "CH3": [0.0, -30.0, -60.0, -90.0, -120.0, -150.0],
        "状態": ["正常", "正常", "異常", "正常", "正常", "正常"],
    },
    step=[1, 2, 3, 4, 5, 6],
    units={"荷重": "kN", "変位": "mm", "CH1": "ue", "CH2": "ue", "CH3": "ue"},
)

coordinates = {"CH1": {"x": 0.0, "y": 0.0}, "CH2": {"x": 10.0, "y": 0.0}, "CH3": {"x": 0.0, "y": 10.0}}
rosettes = {"R1": {"columns": ["CH1", "CH2", "CH3"], "type": "rectangular", "orientation": 0.0}}

ld = col.ops.as_domain(as_load_displacement, "荷重", "変位").end()
coord = col.ops.as_domain(as_coordinate, coordinates=coordinates).end()
strain = col.ops.as_domain(as_strain, rosettes=rosettes, coordinates=coordinates).end()

cyclic_disp = np.concatenate([np.linspace(0.0, 2.0, 5), np.linspace(2.0, -2.0, 9)[1:],
                              np.linspace(-2.0, 4.0, 13)[1:], np.linspace(4.0, 0.0, 9)[1:]])
cyclic_load, p = [], 0.0
for d0, d1 in zip(np.r_[0.0, cyclic_disp[:-1]], cyclic_disp):
    p = min(max(p + 40.0 * (d1 - d0), 4.0 * d1 - 90.0), 4.0 * d1 + 90.0)
    cyclic_load.append(p)
cyclic = (tascpy.ColumnCollection({"荷重": cyclic_load, "変位": cyclic_disp}, units={"荷重": "kN", "変位": "mm"})
          .ops.as_domain(as_load_displacement, "荷重", "変位").end())
```

ファイルを読み書きする例は、このデータを保存した `data.txt` がある作業ディレクトリで実行する前提です。
