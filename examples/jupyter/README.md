# tascpy Jupyter Notebook サンプル

このディレクトリには、tascpy ライブラリを Jupyter Notebook で使用するためのサンプルノートブックが含まれています。Jupyter Notebook は対話的にコードを実行し、結果を可視化するための優れた環境を提供します。

## Jupyter Notebook での tascpy 活用

### 基本的な設定

Jupyter Notebook で tascpy を使用する際の推奨設定：

```python
# Jupyter Notebook での設定
%matplotlib inline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib  # 日本語フォントのサポート

# tascpyのインポート
import tascpy
from tascpy.core.collection import ColumnCollection
```

### スタブファイルとコード補完

Jupyter での自動補完を有効にするには、最初のセルでスタブファイルを生成します：

```python
# スタブファイルの生成（初回実行時に必要）
from tascpy.operations.stub_generator import generate_stubs
generate_stubs()
```

### インタラクティブな可視化

Jupyter Notebook での対話的なプロット表示には、`ipywidgets` を活用できます：

```python
from ipywidgets import interact, FloatSlider, IntSlider

# データの読み込み
collection = ColumnCollection.from_file("../data/sample.csv", format_name="csv")

# インタラクティブなプロット
def plot_with_threshold(threshold):
    result = (
        collection.ops
        .filter_by_value("Value", lambda x: x > threshold)
        .plot(x_column="Time", y_column="Value")
        .end()
    )
    plt.title(f"しきい値: {threshold}以上のデータ")
    plt.grid(True)
    
# スライダーでしきい値を調整可能に
interact(
    plot_with_threshold, 
    threshold=FloatSlider(min=0, max=100, step=5, value=50)
)
```

## サンプルノートブック一覧

現在このディレクトリには以下のサンプルノートブックが含まれています：

1. **interactive_data_analysis.ipynb** - インタラクティブなデータ分析の例
   - スライダーを使った動的なデータフィルタリング
   - ドロップダウンメニューによる列選択
   - チェックボックスでの表示オプション切り替え

2. **domain_specific_notebook.ipynb** - ドメイン特化分析のノートブック
   - 荷重-変位データの高度な分析
   - 降伏点の対話的な検出
   - 結果のエクスポートとレポート生成

## Jupyter での tascpy 活用ヒント

1. **メソッドチェーンの分割**: 長いメソッドチェーンは複数行に分けて可読性を向上させます
   ```python
   result = (
       collection.ops
       .select(columns=["Force", "Displacement"])
       .filter_by_value("Force", lambda x: x > 0)
       # 改行で見やすく
       .add("Force", 10, result_column="AdjustedForce")
       .end()
   )
   ```

2. **中間結果の表示**: メソッドチェーンの途中結果を確認するには、一時的に `.end()` を挿入します
   ```python
   # 中間結果の確認
   intermediate = collection.ops.select(columns=["Force"]).end()
   display(intermediate.head())  # Jupyterの display 関数で表示
   
   # 続けて処理
   final_result = intermediate.ops.add("Force", 10).end()
   ```

3. **コードセルの分割**: 処理ステップごとにセルを分けることで、部分的な実行と結果確認が容易になります

4. **エラー処理**: try-except ブロックを使って、エラーが発生した場合に詳細情報を表示します
   ```python
   try:
       result = collection.ops.some_operation().end()
   except Exception as e:
       print(f"エラーが発生しました: {e}")
       # エラー発生時のデータ状態を確認
       print(f"現在のデータ形状: {len(collection)} 行 × {len(collection.columns)} 列")
   ```

## 注意事項

- Jupyter Notebook で大量のデータを処理する場合は、メモリ使用量に注意してください
- プロット数が多い場合は、`plt.close('all')` で不要なプロットをクリアすると良いでしょう
- 複雑な処理フローは、外部の Python モジュールとして実装し、Notebook からインポートすることも検討してください
