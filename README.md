# Tascpy
## Version
0.0.1
## Example
```python
import tascpy

path = "./result.txt" # タスクの計測結果テキストファイル
with tascpy.Reader(path) as f:
    res = tascpy.Results(f)

data = res["CH0"].data # CH0のデータ(noneはNone, *******はFalse)
data = res["P"].data # タスクの計測名がPのデータ(形式は↑と同様)
pmax = res["P"].max # Pのデータ内のMax.
maxstep = res["P"].maxstep # PデータMax時のステップ(dataのインデックスではない)
ch = res["P"].ch # Pのチャンネル名
unit = res["P"].unit # Pの単位
```

