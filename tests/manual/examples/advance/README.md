# tascpy 高度なサンプル集

このディレクトリには、tascpy ライブラリの高度な使用例を示すサンプルスクリプトが含まれています。これらのサンプルは基本的な操作を理解した後に取り組むことで、より実践的なデータ分析シナリオにおける tascpy の活用方法を学ぶことができます。

## サンプルファイル一覧

1. **[01_outlier_analysis_visualization.py](./01_outlier_analysis_visualization.py)** - 異常値の検出・除去・可視化
   - 異常値を含む模擬データの生成
   - 移動平均を使った異常値検出
   - 異常値の視覚的強調表示
   - 異なるパラメータによる異常値除去の効果比較
   - エッジ処理方法の比較
   - 前処理後データのトレンド分析
   
   ```python
   # 異常値の可視化（欠損除去はチェーン、描画はコレクションの plot で行う）
   clean = filtered_collection.ops.filter_out_none(columns=["data"]).end()
   clean.plot.visualize_outliers(
       column="data",
       window_size=15,
       threshold=0.3,  # しきい値
       plot_type="line",
       highlight_color="red",
       outlier_marker="o",
       ax=ax1,
       normal_alpha=0.7,
   )
   
   # 異常値と判定された行を除外する
   cleaned = (
       filtered_collection.ops
       .filter_out_none(columns=["data"])
       .remove_outliers("data", window_size=15, threshold=0.5)
       .end()
   )
   ```

## 可視化結果

このサンプルでは、異常値の分析と除去に関する以下の視覚化結果が `examples/advance/imgs` ディレクトリに保存されます：

1. **outlier_visualization_comparison.png** - 異なるしきい値での異常値検出の比較
2. **outlier_removal_effect.png** - 異常値除去前後のデータの比較
3. **edge_handling_outlier_comparison.png** - 異なるエッジ処理方法の効果比較
4. **cleaned_data_trend.png** - クリーニング後のデータトレンド分析

![異常値の可視化比較](./imgs/outlier_visualization_comparison.png)

## 異常値処理の主要機能

tascpy では以下の異常値処理機能が提供されています：

### 1. 異常値の検出と可視化

```python
# 異常値の検出とフラグ付け（0: 正常, 1: 異常値 の列を追加）
flagged_collection = (
    collection.ops
    .detect_outliers("data", window_size=15, threshold=0.5, result_column="outlier_flag")
    .end()
)

# 検出した異常値の視覚化
collection.plot.visualize_outliers(
    column="data",
    window_size=15,
    threshold=0.5,
    plot_type="line",
    highlight_color="red",
    outlier_marker="o",
)
```

### 2. 異常値の除去

```python
# 異常値と判定された行を除外する
cleaned_collection = (
    collection.ops
    .remove_outliers("data", window_size=15, threshold=0.5, edge_handling="symmetric")
    .end()
)
```

### 3. エッジ処理方法


```python
# データ端の窓の取り方を指定する（"asymmetric": 端では片側の窓、"symmetric": 対称な窓）
result_asym = collection.ops.remove_outliers("data", window_size=15, threshold=0.5, edge_handling="asymmetric").end()
result_sym = collection.ops.remove_outliers("data", window_size=15, threshold=0.5, edge_handling="symmetric").end()
```

## 実践的なワークフロー例

異常値処理を含む実践的なデータ分析ワークフロー：

```python
# 実践的な異常値処理ワークフロー
result = (
    collection.ops
    .filter_out_none(columns=["raw_data"])  # 欠損値を除去
    .remove_outliers("raw_data", window_size=21, threshold=0.7)  # 異常値の行を除外
    .moving_average("raw_data", window_size=5, result_column="smoothed_data")  # スムージング
    .end()
)

# 可視化による確認
fig, ax = plt.subplots(figsize=(10, 6))
collection.plot.plot(y_column="raw_data", ax=ax, color="gray", linestyle=":", label="生データ")
result.plot.plot(y_column="raw_data", ax=ax, color="blue", label="異常値除去後")
result.plot.plot(y_column="smoothed_data", ax=ax, color="red", linestyle="--", linewidth=2, label="スムージング後")
ax.legend()
```

## パラメータ選択のガイドライン

### 移動ウィンドウサイズの選択

- **小さなウィンドウサイズ** (3-7): 局所的な異常値に敏感、短期的な変動も異常と見なされる可能性
- **中間のウィンドウサイズ** (11-21): 多くの場合の良いバランス
- **大きなウィンドウサイズ** (31以上): 長期的なトレンドからの逸脱を検出、短期的な変動は無視

### しきい値の選択

- **小さなしきい値** (0.1-0.3): 厳格な異常値検出、正常なデータも異常と判定される可能性
- **中間のしきい値** (0.5-0.7): 多くの場合の良いバランス
- **大きなしきい値** (1.0以上): 緩やかな異常値検出、極端な外れ値のみ検出

適切なパラメータはデータの特性や分析の目的によって異なります。複数のパラメータ組み合わせを試し、視覚的に確認することをお勧めします。
