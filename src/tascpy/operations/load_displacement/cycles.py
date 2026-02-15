"""荷重-変位データのサイクル処理関数"""

from typing import Union, List, Optional
import numpy as np
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection
from ...core.column import Column
from .utils import get_load_column, get_displacement_column


@operation(domain="load_displacement")
def cycle_count(
    collection: LoadDisplacementCollection,
    column: Optional[str] = None,
    step: float = 0.5,
    result_column: Optional[str] = None,
) -> LoadDisplacementCollection:
    """データの荷重符号反転からサイクル数をカウント

    荷重の符号変化（正負の反転）からサイクル数をカウントし、
    新しい列として追加します。

    Args:
        collection: 荷重-変位コレクション
        column: サイクルをカウントする列（指定がない場合は荷重列を使用）
        step: サイクルカウントの増分
        result_column: 結果を格納する列名

    Returns:
        LoadDisplacementCollection: サイクル数を含むコレクション
    """
    # 対象列の特定
    if column is None:
        # デフォルトは荷重列
        column = get_load_column(collection)

    if column not in collection.columns:
        raise ValueError(f"列 '{column}' が見つかりません")

    # データを取得
    data = collection[column].values

    # サイクルをカウント
    cycle = [1.0]
    for i in range(1, len(data)):
        if (
            data[i] is not None
            and data[i - 1] is not None
            and data[i] * data[i - 1] < 0
        ):  # 符号が変わった
            c = cycle[i - 1] + step
            cycle.append(c)
        else:
            cycle.append(cycle[i - 1])

    # 整数に変換
    markers = [int(c) for c in cycle]

    # 結果列名の決定
    if result_column is None:
        result_column = f"{column}_cycle"

    # 結果を新しいコレクションとして作成
    result = collection.clone()
    result.columns[result_column] = Column(
        ch=None,  # chパラメータを追加
        name=result_column,
        unit=None,  # unitパラメータを追加
        values=markers,
        metadata={
            "description": f"Cycle count based on {column}"
        },  # descriptionをmetadataに移動
    )

    return result


@operation(domain="load_displacement")
def split_by_cycles(
    collection: LoadDisplacementCollection, cycle_column: Optional[str] = None
) -> List[LoadDisplacementCollection]:
    """サイクル番号ごとにデータを分割

    データをサイクル番号ごとに分割し、各サイクルの
    荷重-変位コレクションのリストを返します。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

    Returns:
        List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト
    """
    # サイクル列の特定または作成
    if cycle_column is None:
        # 既存のサイクル列を探す
        for col_name in collection.columns:
            if "cycle" in col_name.lower():
                cycle_column = col_name
                break

        # 見つからない場合は荷重列に対してcycle_countを実行
        if cycle_column is None:
            temp_result = cycle_count(collection)
            cycle_column = [
                c for c in temp_result.columns if c not in collection.columns
            ][0]
            collection = temp_result

    # サイクルで分割
    from ...operations.core.split import split_by_integers

    return split_by_integers(collection, collection[cycle_column].values)


def _calculate_polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """多角形の面積を計算（靴紐の公式）
    
    Args:
        x: X座標配列
        y: Y座標配列
        
    Returns:
        float: 面積（絶対値）
    """
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


@operation(domain="load_displacement")
def analyze_hysteresis(
    collection: LoadDisplacementCollection,
    cycle_column: Optional[str] = None
) -> LoadDisplacementCollection:
    """ヒステリシスループ解析（エネルギー散逸の計算）

    各サイクルのヒステリシスループ面積（エネルギー散逸）を計算し、
    サイクルごとの統計量を含む新しいコレクションを返します。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル番号列（指定がない場合は自動検出）

    Returns:
        LoadDisplacementCollection: サイクル番号、エネルギー、最大荷重などを列として持つコレクション
    """
    # サイクルごとに分割
    try:
        cycles = split_by_cycles(collection, cycle_column)
    except Exception:
        # サイクル列がない場合は全体を1サイクルとして処理
        cycles = [collection]

    # 結果リスト
    cycle_nums = []
    energies = []
    max_loads = []
    min_loads = []
    max_disps = []
    min_disps = []
    
    load_col_name = get_load_column(collection)
    disp_col_name = get_displacement_column(collection)
    
    # サイクル列名の特定（split_by_cyclesで使用されたもの）
    if cycle_column is None:
         for col_name in collection.columns:
            if "cycle" in col_name.lower():
                cycle_column = col_name
                break
    
    first_cycle_num = 1
    if cycle_column and cycle_column in collection.columns:
        first_vals = collection[cycle_column].values
        if len(first_vals) > 0 and first_vals[0] is not None:
            first_cycle_num = int(first_vals[0])

    for i, cycle_data in enumerate(cycles):
        # 荷重と変位のデータを取得（NumPy配列化、欠損値除去）
        loads = cycle_data[load_col_name].values
        disps = cycle_data[disp_col_name].values
        
        valid_indices = [k for k, (l, d) in enumerate(zip(loads, disps)) if l is not None and d is not None]
        
        if len(valid_indices) < 3:
            # 点が少なすぎて面積計算不能
            energy = 0.0
            max_l, min_l = np.nan, np.nan
            max_d, min_d = np.nan, np.nan
        else:
            l_arr = np.array([loads[k] for k in valid_indices], dtype=float)
            d_arr = np.array([disps[k] for k in valid_indices], dtype=float)
            
            # 面積計算 (エネルギー散逸)
            # 閉じたループとみなして計算
            energy = _calculate_polygon_area(d_arr, l_arr)
            
            max_l = np.max(l_arr)
            min_l = np.min(l_arr)
            max_d = np.max(d_arr)
            min_d = np.min(d_arr)

        # サイクル番号 (cycle_columnがあればその値、なければ連番)
        # split_by_cyclesの結果は昇順のはずだが、ユニークなサイクル値を取得するのはコストがかかる
        # ここでは簡易的に、i + first_cycle_num とする
        # 正確には、各cycle_dataからcycle_columnの代表値を取るべき
        c_num = i + first_cycle_num
        if cycle_column and cycle_column in cycle_data.columns:
             vals = cycle_data[cycle_column].values
             if len(vals) > 0:
                 c_num = vals[0]

        cycle_nums.append(c_num)
        energies.append(energy)
        max_loads.append(max_l)
        min_loads.append(min_l)
        max_disps.append(max_d)
        min_disps.append(min_d)

    # 結果コレクションの作成
    # 既存のmetadataを引き継ぎつつ、解析結果であることを明記
    metadata = collection.metadata.copy()
    metadata["analysis_type"] = "hysteresis_analysis"
    
    result_columns = {
        "cycle": Column(name="cycle", values=cycle_nums, unit=None, ch=None),
        "energy": Column(name="energy", values=energies, unit="J", ch=None, metadata={"description": "Hysteresis loop area"}), # 単位は仮
        "max_load": Column(name="max_load", values=max_loads, unit=collection[load_col_name].unit, ch=None),
        "min_load": Column(name="min_load", values=min_loads, unit=collection[load_col_name].unit, ch=None),
        "max_disp": Column(name="max_disp", values=max_disps, unit=collection[disp_col_name].unit, ch=None),
        "min_disp": Column(name="min_disp", values=min_disps, unit=collection[disp_col_name].unit, ch=None),
    }
    
    return LoadDisplacementCollection(
        step=cycle_nums, # stepをサイクル番号にする
        columns=result_columns,
        metadata=metadata,
        load_column="max_load",
        displacement_column="max_disp"
    )


@operation(domain="load_displacement")
def analyze_stiffness_degradation(
    collection: LoadDisplacementCollection,
    cycle_column: Optional[str] = None
) -> LoadDisplacementCollection:
    """剛性低下解析（サイクルごとの割線剛性）

    各サイクルの最大荷重点と最小荷重点を結ぶ直線の傾き（割線剛性）を計算し、
    剛性の推移を示す新しいコレクションを返します。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル番号列（指定がない場合は自動検出）

    Returns:
        LoadDisplacementCollection: サイクル番号、剛性を含むコレクション
    """
    # ヒステリシス解析の結果を利用すれば効率的
    hysteresis_result = analyze_hysteresis(collection, cycle_column)
    
    cycles = hysteresis_result["cycle"].values
    max_loads = hysteresis_result["max_load"].values
    min_loads = hysteresis_result["min_load"].values
    max_disps = hysteresis_result["max_disp"].values
    min_disps = hysteresis_result["min_disp"].values
    
    stiffnesses = []
    
    for ml, minl, md, mind in zip(max_loads, min_loads, max_disps, min_disps):
        if md is None or mind is None or ml is None or minl is None:
            stiffnesses.append(None)
            continue
            
        delta_disp = md - mind
        delta_load = ml - minl
        
        if abs(delta_disp) < 1e-9:
            # 変位差がほぼゼロの場合は計算不可
            stiffnesses.append(None)
        else:
            k = delta_load / delta_disp
            stiffnesses.append(k)
            
    # 結果に追加
    result = hysteresis_result.clone()
    result.metadata["analysis_type"] = "stiffness_degradation_analysis"
    
    # 単位の推定 (例: kN / mm)
    load_unit = hysteresis_result["max_load"].unit or ""
    disp_unit = hysteresis_result["max_disp"].unit or ""
    stiffness_unit = f"{load_unit}/{disp_unit}" if load_unit and disp_unit else None
    
    result.columns["stiffness"] = Column(name="stiffness", values=stiffnesses, unit=stiffness_unit, ch=None, metadata={"description": "Secant stiffness"})
    
    return result


@operation(domain="load_displacement")
def find_peaks_and_valleys(
    collection: LoadDisplacementCollection,
    column: Optional[str] = None,
    result_column: str = "peak_valley",
    distance: int = 1,
    threshold: Optional[float] = None,
    prominence: Optional[float] = None,
) -> LoadDisplacementCollection:
    """ピーク（極大値）とバレー（極小値）を検出します

    指定された列の極大値と極小値を検出し、
    1（ピーク）、-1（バレー）、0（その他）のフラグを持つ新しい列を追加します。

    Args:
        collection: 荷重-変位コレクション
        column: 検出対象の列（指定がない場合は荷重列を使用）
        result_column: 結果を格納する列名
        distance: ピーク間の最小距離（インデックス数）
        threshold: 隣接点との最小差
        prominence: ピークの突出度（未実装: scipyが必要なため）

    Returns:
        LoadDisplacementCollection: ピーク/バレーフラグを含むコレクション
    """
    if column is None:
        column = get_load_column(collection)

    if column not in collection.columns:
        raise ValueError(f"列 '{column}' が見つかりません")

    data = np.array(collection[column].values)
    
    # None対応: NoneをNaNに変換して処理するが、極値判定では除外が必要
    # ここでは簡易的に、Noneを含むインデックスは極値としない
    # float型に変換
    data_float = np.array([float(x) if x is not None else np.nan for x in data])

    flags = np.zeros(len(data), dtype=int)

    # シンプルな極大・極小判定
    # distanceパラメータのデフォルトは1より大きくないと意味がないが、
    # ユーザー指定が1の場合は隣接チェックのみ
    dist = max(1, distance)

    # 極大値 (Peaks)
    for i in range(1, len(data) - 1):
        if np.isnan(data_float[i]):
            continue
            
        # 簡易的なピーク判定: 両隣より大きい
        if data_float[i] > data_float[i-1] and data_float[i] > data_float[i+1]:
            is_peak = True
            
            # distanceチェック
            # 前方
            start = max(0, i - dist)
            if np.any(data_float[start:i] >= data_float[i]):
                 is_peak = False
            
            # 後方
            if is_peak:
                end = min(len(data), i + dist + 1)
                if np.any(data_float[i+1:end] >= data_float[i]):
                    is_peak = False

            # thresholdチェック
            if is_peak and threshold is not None:
                # 前後の最小値との差がthreshold以上か確認（簡易的）
                min_neighbor = min(data_float[max(0, i-1)], data_float[min(len(data)-1, i+1)])
                if data_float[i] - min_neighbor < threshold:
                    is_peak = False

            if is_peak:
                 flags[i] = 1

    # 極小値 (Valleys)
    for i in range(1, len(data) - 1):
        if np.isnan(data_float[i]):
            continue
            
        # 簡易的なバレー判定: 両隣より小さい
        if data_float[i] < data_float[i-1] and data_float[i] < data_float[i+1]:
            is_valley = True
            
            # distanceチェック
            # 前方
            start = max(0, i - dist)
            if np.any(data_float[start:i] <= data_float[i]):
                 is_valley = False
            
            # 後方
            if is_valley:
                end = min(len(data), i + dist + 1)
                if np.any(data_float[i+1:end] <= data_float[i]):
                    is_valley = False

            # thresholdチェック
            if is_valley and threshold is not None:
                # 前後の最大値との差がthreshold以上か確認
                max_neighbor = max(data_float[max(0, i-1)], data_float[min(len(data)-1, i+1)])
                if max_neighbor - data_float[i] < threshold:
                     is_valley = False

            if is_valley:
                flags[i] = -1

    # 結果を格納
    result = collection.clone()
    result.columns[result_column] = Column(
        ch=None,
        name=result_column,
        unit=None,
        values=flags.tolist(),
        metadata={"description": f"Peak(1)/Valley(-1) of {column}"},
    )

    return result
