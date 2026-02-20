
from typing import List, Optional, Dict, Any, Union, Tuple
import numpy as np

def select_indices(
    step_values: Union[List[Union[int, float]], np.ndarray],
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Tuple[List[int], Dict[str, Any]]:
    """指定されたステップまたはインデックスに基づいてデータを選択するためのインデックスを計算します。

    Args:
        step_values (Union[List[Union[int, float]], np.ndarray]): ステップ値のリストまたは配列。
        columns (Optional[List[str]], optional): 選択するカラム名のリスト（未使用、互換性のため維持）。デフォルトは None。
        indices (Optional[List[int]], optional): 直接指定するインデックスのリスト。デフォルトは None。
        steps (Optional[List[Union[int, float]]], optional): 選択するステップ値またはインデックスのリスト。デフォルトは None。
        by_step_value (bool, optional): `steps` をステップ値として扱うかどうか。Falseの場合はインデックスとして扱います。デフォルトは True。
        tolerance (float, optional): ステップ値一致判定の許容誤差。指定された場合、許容誤差内の最も近い値を選択します。デフォルトは None。

    Returns:
        Tuple[List[int], Dict[str, Any]]: 
            (選択されたインデックスのリスト, 実行結果のメタデータ辞書) のタプル。

    Raises:
        ValueError: indices と steps の両方が指定された場合。
    """
    # indicesとstepsの両方が指定された場合はエラー
    if indices is not None and steps is not None:
        raise ValueError("indicesとstepsは同時に指定できません")

    # データ長
    length = len(step_values)

    # ステップ値からインデックスへの変換処理
    final_indices = indices
    found_steps = []
    missing_steps = []
    metadata_update = {
        "operation": "select",
    }

    if steps is not None:
        metadata_update["operation"] = "select_step"
        final_indices = []  # stepsから変換されるインデックス

        if by_step_value:
            # ステップ値からインデックスに変換
            # step_values might be list or array
            is_array = isinstance(step_values, np.ndarray)
            
            for target_step in steps:
                idx = None
                if is_array:
                    # NumPy optimized search
                    if tolerance is None:
                         indices_found = np.where(step_values == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         # With tolerance
                         diff = np.abs(step_values - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                elif isinstance(step_values, list):
                     # List search
                     if tolerance is None:
                         try:
                              idx = step_values.index(target_step)
                         except ValueError:
                              pass
                     else:
                          for i, v in enumerate(step_values):
                              if abs(v - target_step) <= tolerance:
                                  idx = i
                                  break
                else:
                    # Generic / Numpy search fallback
                    arr_vals = np.array(step_values) if not isinstance(step_values, np.ndarray) else step_values
                    
                    if tolerance is None:
                         indices_found = np.where(arr_vals == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         # With tolerance
                         diff = np.abs(arr_vals - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                
                if idx is not None:
                    final_indices.append(idx)
                    found_steps.append(step_values[idx])
                else:
                    missing_steps.append(target_step)
        else:
            # 直接インデックスとして使用
            for idx in steps:
                if 0 <= idx < length:
                    final_indices.append(idx)
                    # Note: Original code accessed step_values[idx] here, assume it's safe if 0<=idx<length
                    try:
                        found_steps.append(step_values[idx])
                    except IndexError:
                         pass # Should be covered by length check but just in case
                else:
                    missing_steps.append(idx)
                    
        metadata_update.update({
            "selected_steps": found_steps,
            "missing_steps": missing_steps,
            "by_step_value": by_step_value,
        })
    
    return final_indices, metadata_update

def fetch_near_step(
    values: np.ndarray, value: float, **kwargs
) -> List[int]:
    """指定された値に最も近い要素のインデックスを検索します。

    Args:
        values (np.ndarray): 検索対象の数値配列。
        value (float): ターゲット値。
        **kwargs: その他のオプション（未使用）。

    Returns:
        List[int]: 最も近い値のインデックスを含むリスト（要素数1）。

    Raises:
        TypeError: values が数値型でない場合。
        ValueError: 有効なデータが見つからない場合（全てNaNなど）。
    """
    # 数値型変換とチェック
    # Handle list input if necessary (though type hint says ndarray)
    if isinstance(values, list):
         values = np.array(values)
    
    if not np.issubdtype(values.dtype, np.number):
         try:
             values = values.astype(float)
         except ValueError:
             raise TypeError(f"検索対象列は数値型ではありません")

    # 絶対差分
    diff = np.abs(values - value)
    
    # NaNが含まれる場合は無視
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        raise ValueError("有効なデータが見つかりません")

    return [int(idx)]
