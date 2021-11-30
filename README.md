# Tascpy
タスク計測データ処理用のPythonライブラリ
## Version
0.0.3
## Requirement
matplotlib
## Installation
## Example
### 結果の読み込み
計測結果のテキストファイルのロードにより結果を取り扱うExperimental_dataインスタンスを作成できます。
```python
import tascpy

path = "./result.txt" # タスクの計測結果テキストファイル
with tp.Reader(path) as f:
    res = tp.Experimental_data.load(f) # ファイルのロード
```

### 履歴グラフの描画
履歴データ及びチャンネル関係グラフをExperimental_dataインスタンスから簡単に出力できます。
```python

# matplotlibでの可視化
## Pyplot型
### "P"のチャンネルのステップ履歴プロット
res.plot_history("P")
plt.show()
### "d"チャンネル-"P"チャンネル関係のプロット
res.plot_xy("d", "P")
plt.show()
```


### 特定の領域の取り出し
親インスタンスから特定のステップ, チャンネルのみを抽出した子インスタンスを作成できます。
```python
# 一部データの抽出
req_steps = list(range(1, 400)) # 400ステップまで
req_names = ["P", "d", "b1", "b2", "b3", "b4", "b5"] # 指定チャンネル名のみ
extracted = res.extract_data(names=req_names, steps=req_steps) # 指定データのみの新しいインスタンス
```

### 特定のチャンネルの取り出し
指定チャンネルを取り出し, 最大・最小や近傍値を検索することができます。
```python
# 指定チャンネルの取り出し
p  = res["P"] # "P"チャンネルの取り出し
d = res["d"] # "d"チャンネルの取り出し
ch0 = res["CH0"] # 0チャンネルの取り出し


# チャンネルインスタンスの取り扱い
print(p.ch) # このチャンネルのチャンネル名
print(p.name) # このチャンネルの名前
print(p.unit) # このチャンネルの単位
print(p.steps) # ステップ一覧
print(p.data) # 計測データのリスト(ステップ順)

# その他演算
print(p.max) # "P"チャンネルの最大値
print(p.maxrow) # "P"チャンネルが最大となるインデックス
print(p.maxstep) # "P"チャンネルが最大となるステップ(maxrow + 1)
print(p.min) # "P"チャンネルの最小値
print(p.minrow) # "P"チャンネルが最小となるインデックス
print(p.minstep) # "P"チャンネルが最小となるステップ(minrow + 1)
print(p.absmax) # "P"チャンネルの絶対値最大
print(p.absmin) # "P"チャンネルの絶対値最小
step = p.fetch_near_step(100) # "P"チャンネルの値が100に最も近いステップの値
p.to_csv("./p_channel.csv") #  "P"チャンネルのみのcsv作成
```

### 特定のステップの取り出し
指定ステップを検索し, チャンネル名や名前を取得することができます。また指定ステップのXもしくはY固定グラフを作成することができます。
```python
# 通常のステップ取得
step = extracted.fetch_step(100) # ステップ100のインスタンスを取得

# 指定のチャンネルの値が最も近いステップの抽出
ref_load1 = 200.0
ref_load2 = 600.0
fetched_step1 = extracted.fetch_near_step("P", ref_load1) # "P"チャンネルがref_load1に一番近いステップインスタンスを取得
fetched_step2 = extracted.fetch_near_step("P", ref_load2, method=1) # "P"チャンネルがref_load2以下かつ一番近いステップインスタンスを取得
fetched_step3 = extracted.fetch_near_step("P", ref_load2, method=2) # "P"チャンネルがref_load2以上かつ一番近いステップインスタンスを取得
fetchedD_step4 = extracted.fetch_near_step("P", ref_load2, maxstep=150) # ステップ150以下のうちref_load2に一番近いステップインスタンスを取得

# ステップインスタンスの取り扱い
print(fetched_step1.chs) # チャンネル名一覧
print(fetched_step1.names) # 名前一覧

# XorY固定グラフの描画
distance = [0.0, 50.0, 100.0, 200.0, 300.0]
plot_list = ["b1", "b2", "b3", "b4", "b5"]
fetched_step1.plot_const_x(distance, plot_list, marker="o", color="r")
plt.show()
fetched_step2.plot_const_x(distance, plot_list, marker="^", color="b")
plt.show()
```

### 特定のセルの取り出し
ステップインスタンスやチャンネルインスタンスから特定のセルを取り出し, データを参照することができます。
```python
# 取り出したステップの"P"のチャンネル（セル）
cell = fetched_step1["P"]
cell = res["P"][1] # ステップではなくリストインデックスのため注意!

# セルインスタンスの取り扱い
print(cell.data) # 実際の値
print(cell.unit) # このセルの単位
print(cell.step) # このセルのステップ
print(cell.ch) # このセルのチャンネル名
print(cell.name) # このセルの名前
```

### グラフ描画とアウトプットについて
matplotlibのオブジェクト指向描画に対応します。
```python
## オブジェクト指向型
fig = plt.figure(figsize=(10, 3))
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)
### "d"チャンネル-"P"チャンネル関係のプロット
extracted.plot_xy("d", "P", ax=ax1, linewidth=0.5)
### 固定X値に対するチャンネル計測値のプロット（ステップオブジェクト用）
fetched_step1.plot_const_x(distance, plot_list, ax=ax2, marker="o", color="r")
fetched_step2.plot_const_x(distance, plot_list, ax=ax2, marker="^", color="b")
plt.show()
# 抽出データのcsvアウトプット
extracted.to_csv("./data/extracted_W-N.csv")
```
## Note
21.11.30 README更新

## Author
toruinaba