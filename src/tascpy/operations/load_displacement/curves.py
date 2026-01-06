"""荷重-変位データの特殊曲線生成関数"""

from typing import List, Optional, Dict, Tuple, Union, Any, Literal
import numpy as np
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection
from ...core.column import Column, NumberColumn
from ...utils.split import split_list_by_integers
from .utils import (
    get_load_column,
    get_displacement_column,
    get_load_data,
    get_displacement_data,
)
from .cycles import cycle_count


def _extend_data_edge(x_data, y_data, target, target_type="x", extend_position="end"):
    """指定された方向にデータを線形補間により延長する関数

    Args:
        x_data: x座標データ
        y_data: y座標データ
        target: 延長先のターゲット値
        target_type: 延長する軸の種類 ("x"または"y")
        extend_position: 延長する位置 ("start"または"end")

    Returns:
        Tuple: 延長後の(x, y)座標
    """
    if extend_position == "end":
        if len(x_data) < 2 or len(y_data) < 2:
            return target, y_data[-1] if target_type == "x" else x_data[-1]

        x1, y1 = x_data[-2], y_data[-2]
        x2, y2 = x_data[-1], y_data[-1]
    else:  # start
        if len(x_data) < 2 or len(y_data) < 2:
            return target, y_data[0] if target_type == "x" else x_data[0]

        x1, y1 = x_data[0], y_data[0]
        x2, y2 = x_data[1], y_data[1]

    if target_type == "x":
        if x1 == x2:
            return target, y1
        y = y1 + (y2 - y1) * (target - x1) / (x2 - x1)
        return target, y
    else:  # "y"
        if y1 == y2:
            return x1, target
        x = x1 + (x2 - x1) * (target - y1) / (y2 - y1)
        return x, target


@operation(domain="load_displacement")
def get_curve_data(
    collection: LoadDisplacementCollection,
    curve_name: str,
) -> Dict[str, Any]:
    """メタデータに格納された曲線データを取得

    Args:
        collection: 荷重-変位コレクション
        curve_name: 曲線名（例: "skeleton_curve", "cumulative_curve"）

    Returns:
        Dict[str, Any]: 曲線データ（x, y, metadataを含む辞書）

    Raises:
        ValueError: 指定した曲線が存在しない場合
    """
    if (
        collection.metadata is None
        or "curves" not in collection.metadata
        or curve_name not in collection.metadata["curves"]
    ):
        raise ValueError(f"曲線 '{curve_name}' はコレクションに存在しません")

    return collection.metadata["curves"][curve_name]


@operation(domain="load_displacement")
def get_curve_columns(
    collection: LoadDisplacementCollection,
    curve_name: str,
) -> Tuple[Optional[Column], Optional[Column]]:
    """メタデータに格納された曲線データをColumnオブジェクトとして取得

    Args:
        collection: 荷重-変位コレクション
        curve_name: 曲線名（例: "skeleton_curve", "cumulative_curve"）

    Returns:
        Tuple[Optional[Column], Optional[Column]]:
            (x軸のColumn, y軸のColumn)のタプル。曲線が存在しない場合は(None, None)

    Raises:
        ValueError: 指定した曲線データにColumnが含まれていない場合
        ValueError: 指定した曲線が存在しない場合
    """
    if (
        collection.metadata is None
        or "curves" not in collection.metadata
        or curve_name not in collection.metadata["curves"]
    ):
        raise ValueError(f"曲線 '{curve_name}' が存在しません")

    curve_data = collection.metadata["curves"][curve_name]

    if "columns" not in curve_data:
        raise ValueError(f"曲線 '{curve_name}' にColumnデータが含まれていません")

    return curve_data["columns"]["x"], curve_data["columns"]["y"]


@operation(domain="load_displacement")
def list_available_curves(
    collection: LoadDisplacementCollection,
) -> List[str]:
    """利用可能な曲線の一覧を取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        List[str]: 利用可能な曲線名のリスト
    """
    if collection.metadata is None or "curves" not in collection.metadata:
        return []

    return list(collection.metadata["curves"].keys())


@operation(domain="load_displacement")
def create_skeleton_curve(
    collection: LoadDisplacementCollection,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
    cycle_column: Optional[str] = None,
    result_load_column: Optional[str] = None,
    result_disp_column: Optional[str] = None,
    store_as_columns: bool = False,
) -> LoadDisplacementCollection:
    """荷重-変位データからスケルトン曲線を作成

    複数サイクルの荷重-変位データから、包絡線（スケルトン曲線）を作成します。
    スケルトン曲線は、各サイクルの最大応答値を結んだ曲線です。

    デフォルトでは、スケルトン曲線はメタデータの "curves" セクションに格納されます。
    これにより、列の長さが異なるデータを格納できます。
    また、メタデータ内にColumnオブジェクトとしても格納されるため、いつでも取得可能です。

    Args:
        collection: 荷重-変位コレクション
        has_decrease: 減少部分も含めるか
        decrease_type: 減少部分の処理方法 ('envelope', 'continuous_only', 'both')
        cycle_column: サイクル列名（指定なしの場合は自動生成）
        result_load_column: 結果の荷重列名（指定なしの場合は自動生成）
        result_disp_column: 結果の変位列名（指定なしの場合は自動生成）
        store_as_columns: Trueの場合、旧形式との互換性のために列としても格納

    Returns:
        LoadDisplacementCollection: スケルトン曲線データを含むコレクション
    """
    # 列の特定
    load_column = get_load_column(collection)
    disp_column = get_displacement_column(collection)

    # サイクル列の特定または作成
    if cycle_column is None:
        # サイクル列が存在するかチェック
        cycle_columns = [c for c in collection.columns if "cycle" in c.lower()]
        if cycle_columns:
            cycle_column = cycle_columns[0]
        else:
            # サイクル列を作成
            temp_result = cycle_count(collection)
            cycle_column = [
                c for c in temp_result.columns if c not in collection.columns
            ][0]
            collection = temp_result

    # データの取得
    loads = get_load_data(collection)
    displacements = get_displacement_data(collection)
    markers = np.array(
        [i if i is not None else 0 for i in collection[cycle_column].values]
    )

    # NumPyの配列からNaNを除外してリスト化（プラグインからの移植を容易にするため）
    loads_list = loads.tolist()
    disps_list = displacements.tolist()
    markers_list = markers.tolist()

    # サイクルごとに分割
    splitted_loads = split_list_by_integers(loads_list, markers_list)
    splitted_disps = split_list_by_integers(disps_list, markers_list)

    # 最大荷重のサイクルを特定
    max_load_idx = np.nanargmax(loads)
    max_marker = int(markers[max_load_idx])
    end_marker = int(np.nanmax(markers))

    # スケルトン曲線の計算
    p_ske = []
    d_ske = []
    p_max = 0.0

    # 増加部分（最大荷重まで）
    for cyc in range(1, max_marker + 1):
        # 該当するサイクルのインデックスを探す
        cyc_indices = np.where(markers == cyc)[0]
        if len(cyc_indices) == 0:
            continue

        # 該当サイクルのデータを取得
        cyc_idx = cyc - 1  # 0ベースのインデックス
        if cyc_idx >= len(splitted_loads) or cyc_idx >= len(splitted_disps):
            continue

        load = splitted_loads[cyc_idx]
        disp = splitted_disps[cyc_idx]

        if not load or not disp:
            continue

        d_offset = 0.0

        for i in range(len(load)):
            if load[i] is not None and not np.isnan(load[i]) and load[i] > p_max:
                p_max = load[i]
                if d_offset == 0.0 and len(p_ske) >= 2:
                    x, _ = _extend_data_edge(d_ske, p_ske, load[i], "y", "end")
                    d_offset = x - disp[i]
                p_ske.append(load[i])
                d_ske.append(disp[i] + d_offset)

    # 減少部分（指定がある場合）
    if has_decrease and max_marker <= end_marker:
        for cyc in range(max_marker, end_marker + 1):
            # 該当するサイクルのインデックスを探す
            cyc_indices = np.where(markers == cyc)[0]
            if len(cyc_indices) == 0:
                continue

            # 該当サイクルのデータを取得
            cyc_idx = cyc - 1  # 0ベースのインデックス
            if cyc_idx >= len(splitted_loads) or cyc_idx >= len(splitted_disps):
                continue

            load = splitted_loads[cyc_idx]
            disp = splitted_disps[cyc_idx]

            if not load or not disp:
                continue

            # 有効なデータをフィルタリング
            valid_indices = [
                i
                for i, (l, d) in enumerate(zip(load, disp))
                if l is not None
                and not np.isnan(l)
                and d is not None
                and not np.isnan(d)
            ]

            if not valid_indices:
                continue

            valid_load = [load[i] for i in valid_indices]
            valid_disp = [disp[i] for i in valid_indices]

            if not valid_load or not valid_disp:
                continue

            # 最大荷重と最大変位のインデックスを取得
            load_max = max(valid_load)
            disp_max = max(valid_disp)
            load_max_idx = valid_indices[valid_load.index(load_max)]
            disp_max_idx = valid_indices[valid_disp.index(disp_max)]

            if decrease_type == "envelope":
                # 最大変位点を使用
                p_end = load[disp_max_idx]
                d_end = disp[disp_max_idx]
                if (
                    p_end is not None
                    and not np.isnan(p_end)
                    and d_end is not None
                    and not np.isnan(d_end)
                ):
                    p_ske.append(p_end)
                    d_ske.append(d_end + d_offset)

            elif decrease_type == "continuous_only":
                # 最大荷重から最大変位までの連続的な部分
                if load_max_idx == disp_max_idx:
                    continue

                for i in range(
                    min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1
                ):
                    # 既に登録済みの点はスキップ
                    if (
                        load[i] is None
                        or np.isnan(load[i])
                        or disp[i] is None
                        or np.isnan(disp[i])
                    ):
                        continue

                    if (
                        p_ske
                        and load[i] == p_ske[-1]
                        and disp[i] + d_offset == d_ske[-1]
                    ):
                        continue

                    p_ske.append(load[i])
                    d_ske.append(disp[i] + d_offset)

            elif decrease_type == "both":
                # envelopeとcontinuous_onlyの組み合わせ
                if load_max_idx == disp_max_idx:
                    if (
                        load[disp_max_idx] is not None
                        and not np.isnan(load[disp_max_idx])
                        and disp[disp_max_idx] is not None
                        and not np.isnan(disp[disp_max_idx])
                    ):
                        p_ske.append(load[disp_max_idx])
                        d_ske.append(disp[disp_max_idx] + d_offset)
                else:
                    for i in range(
                        min(load_max_idx, disp_max_idx),
                        max(load_max_idx, disp_max_idx) + 1,
                    ):
                        if (
                            load[i] is None
                            or np.isnan(load[i])
                            or disp[i] is None
                            or np.isnan(disp[i])
                        ):
                            continue

                        if (
                            p_ske
                            and load[i] == p_ske[-1]
                            and disp[i] + d_offset == d_ske[-1]
                        ):
                            continue

                        p_ske.append(load[i])
                        d_ske.append(disp[i] + d_offset)
            else:
                raise ValueError(
                    "decrease_typeは'envelope', 'continuous_only', 'both'のいずれかである必要があります"
                )

    # 結果列名の決定
    if result_load_column is None:
        result_load_column = f"{load_column}_skeleton"
    if result_disp_column is None:
        result_disp_column = f"{disp_column}_skeleton"

    # 結果を新しいコレクションとして作成
    result = collection.clone()

    # 単位情報の取得
    load_unit = (
        collection[load_column].unit
        if hasattr(collection[load_column], "unit")
        else None
    )
    disp_unit = (
        collection[disp_column].unit
        if hasattr(collection[disp_column], "unit")
        else None
    )

    # メタデータにカーブデータを格納
    if result.metadata is None:
        result.metadata = {}

    if "curves" not in result.metadata:
        result.metadata["curves"] = {}

    # 荷重と変位のColumnオブジェクトを作成
    load_column_obj = NumberColumn(
        ch=collection[load_column].ch,
        name=f"skeleton_curve_load",
        unit=load_unit,
        values=p_ske,
        metadata={
            "description": f"Skeleton curve load from {load_column}",
            "source_column": load_column,
        },
    )

    disp_column_obj = NumberColumn(
        ch=collection[disp_column].ch,
        name=f"skeleton_curve_disp",
        unit=disp_unit,
        values=d_ske,
        metadata={
            "description": f"Skeleton curve displacement from {disp_column}",
            "source_column": disp_column,
        },
    )

    # スケルトン曲線データをメタデータに格納
    result.metadata["curves"]["skeleton_curve"] = {
        "x": d_ske,
        "y": p_ske,
        "columns": {
            "x": disp_column_obj,
            "y": load_column_obj,
        },
        "metadata": {
            "source_columns": {"load": load_column, "displacement": disp_column},
            "description": "Skeleton curve derived from load-displacement data",
            "units": {"x": disp_unit, "y": load_unit},
            "parameters": {
                "has_decrease": has_decrease,
                "decrease_type": decrease_type,
            },
        },
    }

    # 互換性のために列も追加する（オプション）
    if store_as_columns:
        result.columns[result_load_column] = load_column_obj.clone()
        result.columns[result_load_column].name = result_load_column

        result.columns[result_disp_column] = disp_column_obj.clone()
        result.columns[result_disp_column].name = result_disp_column

    return result


@operation(domain="load_displacement")
def create_cumulative_curve(
    collection: LoadDisplacementCollection,
    cycle_column: Optional[str] = None,
    result_load_column: Optional[str] = None,
    result_disp_column: Optional[str] = None,
    store_as_columns: bool = False,
) -> LoadDisplacementCollection:
    """荷重-変位データから累積曲線を作成

    複数サイクルの荷重-変位データから、累積変形曲線を作成します。
    累積曲線は、各サイクルの変形を累積的に加算した曲線です。

    デフォルトでは、累積曲線はメタデータの "curves" セクションに格納されます。
    これにより、列の長さが異なるデータを格納できます。
    また、メタデータ内にColumnオブジェクトとしても格納されるため、いつでも取得可能です。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル列名（指定なしの場合は自動生成）
        result_load_column: 結果の荷重列名（指定なしの場合は自動生成）
        result_disp_column: 結果の変位列名（指定なしの場合は自動生成）
        store_as_columns: Trueの場合、旧形式との互換性のために列としても格納

    Returns:
        LoadDisplacementCollection: 累積曲線データを含むコレクション
    """
    # 列の特定
    load_column = get_load_column(collection)
    disp_column = get_displacement_column(collection)

    # サイクル列の特定または作成
    if cycle_column is None:
        # サイクル列が存在するかチェック
        cycle_columns = [c for c in collection.columns if "cycle" in c.lower()]
        if cycle_columns:
            cycle_column = cycle_columns[0]
        else:
            # サイクル列を作成
            temp_result = cycle_count(collection)
            cycle_column = [
                c for c in temp_result.columns if c not in collection.columns
            ][0]
            collection = temp_result

    # データの取得
    loads = get_load_data(collection)
    displacements = get_displacement_data(collection)
    markers = np.array(
        [i if i is not None else 0 for i in collection[cycle_column].values]
    )

    # NumPyの配列からNaNを除外してリスト化
    loads_list = loads.tolist()
    disps_list = displacements.tolist()
    markers_list = markers.tolist()

    # サイクルごとに分割
    splitted_loads = split_list_by_integers(loads_list, markers_list)
    splitted_displacements = split_list_by_integers(disps_list, markers_list)

    # 累積曲線の計算
    p_cum = []
    d_cum = []

    for i in range(len(splitted_loads)):
        load = splitted_loads[i]
        displacement = splitted_displacements[i]

        # None値のフィルタリング
        valid_indices = [
            j
            for j, (l, d) in enumerate(zip(load, displacement))
            if (l is not None and not np.isnan(l) and d is not None and not np.isnan(d))
        ]
        valid_load = [load[j] for j in valid_indices]
        valid_disp = [displacement[j] for j in valid_indices]

        if not valid_load or not valid_disp:
            continue

        # 正の荷重部分を抽出
        pos_idx = [j for j, x in enumerate(valid_load) if x >= 0.0]
        pos_loads = [valid_load[j] for j in pos_idx]
        pos_displacements = [valid_disp[j] for j in pos_idx]

        if not pos_loads or not pos_displacements:
            continue

        # 荷重ゼロでの開始・終了点を計算
        x_s, y_s = _extend_data_edge(pos_displacements, pos_loads, 0.0, "y", "start")
        x_e, y_e = _extend_data_edge(pos_displacements, pos_loads, 0.0, "y", "end")

        # 前のサイクルからの変位オフセットを計算
        d_offset = d_cum[-1] - x_s if d_cum else 0.0

        # 拡張データを累積曲線に追加
        p_extended = [y_s] + pos_loads + [y_e]
        d_extended = [x_s] + pos_displacements + [x_e]
        d_offsetted = [x + d_offset for x in d_extended]

        p_cum.extend(p_extended)
        d_cum.extend(d_offsetted)

    # 結果列名の決定
    if result_load_column is None:
        result_load_column = f"{load_column}_cumulative"
    if result_disp_column is None:
        result_disp_column = f"{disp_column}_cumulative"

    # 結果を新しいコレクションとして作成
    result = collection.clone()

    # 単位情報の取得
    load_unit = (
        collection[load_column].unit
        if hasattr(collection[load_column], "unit")
        else None
    )
    disp_unit = (
        collection[disp_column].unit
        if hasattr(collection[disp_column], "unit")
        else None
    )

    # メタデータにカーブデータを格納
    if result.metadata is None:
        result.metadata = {}

    if "curves" not in result.metadata:
        result.metadata["curves"] = {}

    # 荷重と変位のColumnオブジェクトを作成
    load_column_obj = NumberColumn(
        ch=collection[load_column].ch,
        name=f"cumulative_curve_load",
        unit=load_unit,
        values=p_cum,
        metadata={
            "description": f"Cumulative curve load from {load_column}",
            "source_column": load_column,
        },
    )

    disp_column_obj = NumberColumn(
        ch=collection[disp_column].ch,
        name=f"cumulative_curve_disp",
        unit=disp_unit,
        values=d_cum,
        metadata={
            "description": f"Cumulative curve displacement from {disp_column}",
            "source_column": disp_column,
        },
    )

    # 累積曲線データをメタデータに格納
    result.metadata["curves"]["cumulative_curve"] = {
        "x": d_cum,
        "y": p_cum,
        "columns": {
            "x": disp_column_obj,
            "y": load_column_obj,
        },
        "metadata": {
            "source_columns": {"load": load_column, "displacement": disp_column},
            "description": "Cumulative curve derived from load-displacement data",
            "units": {"x": disp_unit, "y": load_unit},
        },
    }

    # 互換性のために列も追加する（オプション）
    if store_as_columns:
        result.columns[result_load_column] = load_column_obj.clone()
        result.columns[result_load_column].name = result_load_column

        result.columns[result_disp_column] = disp_column_obj.clone()
        result.columns[result_disp_column].name = result_disp_column

    return result


@operation(domain="load_displacement")
def export_curve_to_csv(
    collection: LoadDisplacementCollection,
    curve_name: str,
    file_path: str,
    columns: Tuple[str, str] = ("x", "y"),
    encoding: str = "utf-8",
    include_header: bool = True,
) -> None:
    """メタデータに格納された曲線データを CSV ファイルにエクスポートします。

    Args:
        collection: LoadDisplacementCollection オブジェクト
        curve_name: エクスポートする曲線名（"skeleton_curve" や "cumulative_curve" など）
        file_path: 出力先の CSV ファイルパス
        columns: エクスポートするカラム名タプル（デフォルトは ("x", "y")）
        encoding: ファイルエンコーディング（デフォルトは "utf-8"）
        include_header: ヘッダー行を含めるかどうか

    Raises:
        ValueError: 指定した曲線が存在しない場合、またはデータが不正な場合
        IOError: ファイル書き込みに失敗した場合
    """
    if (
        collection.metadata is None
        or "curves" not in collection.metadata
        or curve_name not in collection.metadata["curves"]
    ):
        raise ValueError(f"曲線 '{curve_name}' はコレクションに存在しません")
    curve_data = collection.metadata["curves"][curve_name]
    x_data = curve_data.get(columns[0])
    y_data = curve_data.get(columns[1])
    if x_data is None or y_data is None:
        raise ValueError(f"曲線 '{curve_name}' に {columns} データが存在しません")
    if len(x_data) != len(y_data):
        raise ValueError(
            f"x, y データの長さが一致しません: {len(x_data)} vs {len(y_data)}"
        )
    import csv

    try:
        with open(file_path, mode="w", encoding=encoding, newline="") as f:
            writer = csv.writer(f)
            if include_header:
                writer.writerow([columns[0], columns[1]])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])
    except Exception as e:
        raise IOError(f"CSV ファイルの書き込みに失敗しました: {e}")
