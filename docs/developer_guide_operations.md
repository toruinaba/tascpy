# 操作登録の詳細な仕組み (register_functional)

tascpyにおけるデータ処理機能の根幹は、純粋な計算関数（Functional層）からエラーハンドリング、欠損値処理、入力の自動展開などを分離し、メソッドチェーン（`col.ops.*`）から使いやすく提供するための**操作登録システム (`register_functional`)** にあります。

このドキュメントでは、その全容を解明し、複雑な処理をどのように登録するかを解説します。

---

## 1. 全体アーキテクチャとデータフロー

ユーザが `col.ops.my_function()` を呼び出したとき、裏側では以下のような変換パイプラインが走ります。

```mermaid
flowchart TD
    User([ユーザーからの呼び出し\n`col.ops.func("A", param=1)`]) --> Proxy[CollectionOperations Proxy\n`func(col, "A", param=1)`]
    Proxy --> RegWrap[Registry Wrapper\n動的に生成された関数]
    
    subgraph Abstraction Decorators [抽象化デコレータ層 (abstraction.py)]
        SR[store_result\n/ store_xy_result]
        FR[filter_rows\n※事前条件による行のフィルタ]
        IS[inject_step_values\n/ inject_metadata]
        IC[inject_columns\n列名の解決と配列への展開]
        HMV[handle_missing_values\nNaN等の処理]

        SR --> FR
        FR --> IS
        IS --> IC
        IC --> HMV
    end

    RegWrap --> SR
    HMV --> Func((純粋な計算関数\n functional.py\n`func(array_A, param=1)`))
    
    Func -. 計算結果を返す .-> HMV
    SR -. 結果を新しいコレクションにマージして返す .-> Proxy
```

このアーキテクチャにより、純粋な `Numpy` 計算関数を書くだけで、tascpyの柔軟な列指定、安全なエラーハンドリング、メソッドチェーンが自動的に構成されます。

---

## 2. デコレータ層の詳細解剖

登録時に指定できる各デコレータの役割と挙動を解説します。

### 2.1 `inject_columns` (列名の解決と展開)
最も重要なデコレータです。プロキシから渡された文字列（列名）を、実際の `np.ndarray` などのデータに変換します。
列が存在しない場合は、ここで自動的に `KeyError` が発生するため、純粋関数側でのエラーチェックは不要です。

*   **`num_inputs`**: 指定した数の**位置引数**を列名として解釈し、展開します。
    *   `num_inputs=1` (デフォルト): 最初の引数を列名とみなし、展開します（例: `func("列A")` -> `func(array_A)`）。
    *   **`num_inputs=-1`**: 全ての位置引数（`*args`）を列名とみなし、順に配列に展開します。純粋関数が可変長引数（`*columns`）を受け取る場合に非常に便利です（例: `average_across`）。
*   **`columns_arg`**: 文字列を指定すると、引数（kwargs）の中からその名前のリストを探し、`{"列名": 配列}` の辞書を第一引数として純粋関数に注入します。
*   **`cast_to_numpy`**: `True` なら入力のリスト等を `np.ndarray` に統一します。

### 2.2 `handle_missing_values` (欠損値・NaN処理)
純粋関数に値が渡される**直前**に実行されます。
*   **`strategy="nan"`**: 入力に含まれる `None` を `np.nan` にキャストし、配列を float 型に統一します。Numpyの算術関数に安全に渡すためによく使われます。
*   **`strategy="strict"`**: どこかに `None` や `NaN` が含まれていれば、関数自体を実行せずに全てが `NaN` の結果配列を即座に返します。

### 2.3 `filter_rows` (行の事前フィルタリング)
行数が変動する操作（`filter_by_value` や `filter_out_none` など）で使用します。`filter_rows=True` を指定すると、純粋関数が返した boolean マスクや有効インデックスに基づいて、新しい `ColumnCollection` を小さく絞り込んで返します。

### 2.4 `store_result`系 (結果の格納と命名)
純粋関数の計算結果（配列や数値）を受け取り、それを新しい列としてどう保存するかを決定します。
元のコレクション（`in_place=False`ならコピー）に結果を追加した新しいインスタンスを返します。

*   **命名規則 (`result_naming`)**: 
    *   `basic_naming("op_name")`: ユーザーが明示的な `result_column="名前"` を与えなかった場合、元の列名に基づいて名付けます。（例: `A` -> `A_op_name`）。`num_inputs=-1`などで元列が複数ある場合は、手動指定が必須になるか、操作名を単独で使います。
    *   `format_naming("{col}_{param}")`: フォーマット文字列に基づいて動的に命名します。
*   派生版として `store_xy_result` (結果をX, Yのペアとして保存する) 等があります。

---

## 3. シグネチャと型ヒントのオーバーライド

`register_functional` は動的にラッパーを生成するため、本来エディタ側（VS Code 等）からは関数の引数が `*args, **kwargs` に見えてしまいます。これを防ぐため、`OperationRegistry.generate_stubs()` を使って `.pyi` スタブファイルを自動生成し、静的型推論を可能にします。

この際、純粋関数の本来の引数と、プロキシ経由で呼ぶ際にユーザーが渡すべき引数が異なるため、`signature_override` を使用してシグネチャを改変します。

```python
signature_override={
    # 純粋関数の *columns を、ユーザー入力時は column_names の tuple として型付け
    "*columns": ("column_names", tuple),
    
    # ユーザーが指定可能な結果格納用の引数（もともとの関数には存在しない引数）
    "result_column": (str, None)
}
```
この定義に基づいてスタブが生成されるため、メソッドチェーン時にも確実なコード補完が効くようになります。

---

## 4. パターン別 実装レシピ

実際の開発で頻出するパターンの登録方法です。

### 4.1 単一カラムを入力とする関数
もっとも基本的な形です。最初の引数が自動的に配列に変換されます。

```python
from tascpy.analytics.operations.registry import register_functional
from tascpy.analytics.operations.abstraction import basic_naming

# 純粋関数: def calc_diff(array: np.ndarray, base_value: float) -> np.ndarray: ...

calc_diff = register_functional(
    functional.calc_diff,
    domain="core",
    name="calc_diff",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    store_result={"result_naming": basic_naming("diff")},
    signature_override={
        "values": ("column", str),  # スタブ上では 'column' という名前に見せる
        "result_column": (str, None)
    }
)
# 使い方: col.ops.calc_diff("A", base_value=1.5)
```

### 4.2 複数カラムを個別に入力とする関数
2つの列を受け取る関数などです。

```python
# 純粋関数: def add_two(arr1: np.ndarray, arr2: np.ndarray) -> np.ndarray: ...

add_two = register_functional(
    functional.add_two,
    domain="core",
    name="add_two",
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    store_result={"result_naming": basic_naming("sum")},
    ...
)
# 使い方: col.ops.add_two("A", "B")
```

### 4.3 辞書として複数カラムを受け取る関数
大量のカラムを一度に渡し、純粋関数側で辞書として一括処理したい場合です。（`filter_out_none`などで利用）

```python
# 純粋関数: def process_all(data_dict: Dict[str, np.ndarray]) -> np.ndarray: ...

process_all = register_functional(
    functional.process_all,
    domain="core",
    name="process_all",
    # 引数 'columns' (リスト) を探し、それを辞書に変換して注入
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    ...
)
# 使い方: col.ops.process_all(columns=["A", "B", "C"])
```

### 4.4 可変長引数 (`*args`) を受け取る関数
ユーザーが `("A", "B", "C")` のように任意の数の列名を渡し、純粋関数側で `(*arrays)` として受け取る場合です。（`average_across`などで利用）

```python
# 純粋関数: def average_across(*columns: np.ndarray, ignore_nan: bool = True) -> np.ndarray: ...

average_across = register_functional(
    functional.average_across,
    domain="core",
    name="average_across",
    # -1 を指定することで、全ての位置引数が列名とみなされ配列に展開される
    inject_columns={"num_inputs": -1, "cast_to_numpy": True},
    store_result={"result_naming": basic_naming("average_across")},
    signature_override={
        "*columns": ("column_names", tuple),
        "result_column": (str, None)
    }
)
# 使い方: col.ops.average_across("A", "B", "C", result_column="avg_ABC")
```
