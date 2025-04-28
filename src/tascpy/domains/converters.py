from typing import Optional, Any, Dict, List, Union
from datetime import datetime, timedelta
import numpy as np
from ..core.collection import ColumnCollection
from ..core.indices import Indices


def prepare_for_domain_conversion(
    collection: ColumnCollection, target_domain: str, **kwargs: Any
) -> ColumnCollection:
    """ドメイン変換の前準備を行う

    Args:
        collection: 変換元のColumnCollection
        target_domain: 変換先のドメイン名
        **kwargs: 変換パラメータ

    Returns:
        変換準備が完了したColumnCollection
    """
    # 元のコレクションをクローン
    result = collection.clone()

    # 時系列ドメインへの変換前処理
    if target_domain == "timeseries":
        _prepare_for_timeseries(result, **kwargs)

    # 信号処理ドメインへの変換前処理
    elif target_domain == "signal":
        _prepare_for_signal(result, **kwargs)

    return result


def _prepare_for_timeseries(collection: ColumnCollection, **kwargs: Any) -> None:
    """時系列ドメインへの変換前処理

    Args:
        collection: 前処理するコレクション
        **kwargs: 変換パラメータ
    """
    # ステップが数値で、start_dateが指定されている場合は日付に変換
    if (
        len(collection.step.values) > 0
        and not isinstance(collection.step.values[0], datetime)
        and "start_date" in kwargs
    ):

        # 開始日を解析
        if isinstance(kwargs["start_date"], str):
            start_date = datetime.fromisoformat(kwargs["start_date"])
        else:
            start_date = kwargs["start_date"]

        # 頻度を解析（デフォルトは1日）
        freq = kwargs.get("frequency", "1D")
        if freq == "1D":
            delta = timedelta(days=1)
        elif freq == "1H":
            delta = timedelta(hours=1)
        elif freq == "1min" or freq == "1m":
            delta = timedelta(minutes=1)
        elif freq == "1s":
            delta = timedelta(seconds=1)
        else:
            # カスタム形式の解析（例: "2H", "30min"）
            import re

            match = re.match(r"(\d+)([DHMSdhms])", freq)
            if match:
                value, unit = int(match.group(1)), match.group(2).upper()
                if unit == "D":
                    delta = timedelta(days=value)
                elif unit == "H":
                    delta = timedelta(hours=value)
                elif unit == "M":
                    delta = timedelta(minutes=value)
                elif unit == "S":
                    delta = timedelta(seconds=value)
                else:
                    delta = timedelta(days=1)  # デフォルト
            else:
                delta = timedelta(days=1)  # 解析失敗時はデフォルト

        # ステップを日付に変換
        step_values = [
            start_date + (delta * float(step)) for step in collection.step.values
        ]

        # 新しいStepオブジェクトを作成
        collection.step = Indices(values=step_values)

        # 使用済みのキーをkwargsから削除
        kwargs.pop("start_date", None)


def _prepare_for_signal(collection: ColumnCollection, **kwargs: Any) -> None:
    """信号処理ドメインへの変換前処理

    Args:
        collection: 前処理するコレクション
        **kwargs: 変換パラメータ
    """
    # 日付ステップを時間軸に変換
    if len(collection.step.values) > 0 and isinstance(
        collection.step.values[0], datetime
    ):

        # サンプリングレートを取得
        sample_rate = kwargs.get("sample_rate", 1.0)

        # 開始時間を0とする時間軸に変換
        start_time = collection.step.values[0]
        time_values = [
            (dt - start_time).total_seconds() for dt in collection.step.values
        ]

        # 新しいStepオブジェクトを作成
        collection.step = Indices(values=time_values)

        # 元の時間情報をメタデータに保存
        collection.metadata["original_timestamps"] = {
            "start": start_time.isoformat(),
            "sample_rate": sample_rate,
        }

        # 時間が等間隔でない場合、リサンプリングの警告をメタデータに追加
        time_diffs = np.diff(time_values)
        if len(time_diffs) > 0 and np.std(time_diffs) > 1e-6:
            collection.metadata["signal_warning"] = (
                "非等間隔データです。信号処理前にリサンプリングを検討してください。"
            )
