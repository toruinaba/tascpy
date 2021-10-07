# Tascpy
## Version
0.0.2
## 
## Example
```python
import tascpy

path = "./result.txt" # タスクの計測結果テキストファイル
with tp.Reader(path) as f:
    res = tp.Experimental_data.load(f) # ファイルのロード

# 一部データの抽出
req_steps = list(range(1, 400)) # 400ステップまで
req_names = ["P", "d", "b1", "b2", "b3", "b4", "b5"] # 指定チャンネル名のみ
extracted = res.extract_data(names=req_names, steps=req_steps) # 指定データのみの新しいインスタンス

# 指定のチャンネルの値が最も近いステップの抽出
ref_load1 = 200.0
ref_load2 = 600.0
fetched_step1 = extracted.fetch_near_step("P", ref_load1)
fetched_step2 = extracted.fetch_near_step("P", ref_load2)

# matplotlibでの可視化
## Pyplot型
### "P"のチャンネルのステップ履歴プロット
res.plot_history("P")
plt.show()
### "d"チャンネル-"P"チャンネル関係のプロット
res.plot_xy("d", "P")
plt.show()

## オブジェクト指向型
fig = plt.figure(figsize=(10, 3))
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)
### "d"チャンネル-"P"チャンネル関係のプロット
extracted.plot_xy("d", "P", ax=ax1, linewidth=0.5)
### 固定X値に対するチャンネル計測値のプロット（ステップオブジェクト用）
distance = [0.0, 50.0, 100.0, 200.0, 300.0]
plot_list = ["b1", "b2", "b3", "b4", "b5"]
fetched_step1.plot_const_x(distance, plot_list, ax=ax2, marker="o", color="r")
fetched_step2.plot_const_x(distance, plot_list, ax=ax2, marker="^", color="b")
plt.show()
# 抽出データのcsvアウトプット
extracted.to_csv("./data/extracted_W-N.csv")
```
