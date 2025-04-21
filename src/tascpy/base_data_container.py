from typing import Any, List, Dict, Tuple, Union, Callable
from pathlib import Path
from abc import ABC, abstractmethod

from matplotlib.pyplot import Axes

from .channel import Channel
from .step import Step

from .utils.plot import plot_data, add_x_max, add_x_min, add_y_max, add_y_min, set_axis
from .utils.data import filter_with_indices


class PlottingMixin:
    """プロット機能を提供するMixin"""

    def plot_xy(
        self,
        x: Union[List[str], str],
        y: Union[List[str], str],
        ax=None,
        show_unit=True,
        show_x_max=False,
        show_x_min=False,
        show_y_max=False,
        show_y_min=False,
        **kwargs,
    ):
        if ax is None:
            from matplotlib import pyplot as plt

            fig, ax = plt.subplots()
        if isinstance(x, str) and isinstance(y, str):
            ax = self._plot_helper(
                ax,
                x,
                y,
                show_unit,
                show_x_max,
                show_x_min,
                show_y_max,
                show_y_min,
                **kwargs,
            )
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                raise ValueError("凡例の数が一致しません.")
            for name_x, name_y in zip(x, y):
                ax = self._plot_helper(
                    ax,
                    name_x,
                    name_y,
                    show_unit,
                    show_x_max,
                    show_x_min,
                    show_y_max,
                    show_y_min,
                    **kwargs,
                )
        else:
            raise ValueError("xとyは両方とも文字列またはリストである必要があります.")
        return ax

    def plot_history(
        self,
        y: Union[List[str], str],
        ax=None,
        show_unit=True,
        show_x_max=False,
        show_x_min=False,
        show_y_max=False,
        show_y_min=False,
        **kwargs,
    ):
        return self.plot_xy(
            "step",
            y,
            ax=ax,
            show_unit=show_unit,
            show_x_max=show_x_max,
            show_x_min=show_x_min,
            show_y_max=show_y_max,
            show_y_min=show_y_min,
            **kwargs,
        )

    def _plot_helper(
        self,
        ax: Axes,
        x: str,
        y: str,
        show_unit: bool = True,
        show_x_max: bool = False,
        show_xmin: bool = False,
        show_y_max: bool = False,
        show_y_min: bool = False,
        **kwargs,
    ):
        """プロットする関数"""
        if x in ("step", "steps", "Step", "Steps", "STEP", "STEPS"):
            x_data = self.steps
            x_unit = "Step"
        else:
            x_data = self[x].data
            x_unit = f"{self[x].name}[{self[x].unit}]"
        y_data = self[y].data
        y_unit = f"{self[y].name}[{self[y].unit}]"
        ax = plot_data(ax, x_data, y_data, **kwargs)
        if show_unit:
            ax = set_axis(ax, x_unit, y_unit)
        if show_x_max:
            ax = add_x_max(ax, x_data, x_data)
        if show_xmin:
            ax = add_x_min(ax, x_data, y_data)
        if show_y_max:
            ax = add_y_max(ax, x_data, y_data)
        if show_y_min:
            ax = add_y_min(ax, x_data, y_data)
        return ax

    def plot_const_x(
        self, step: int, x: List[float], y: Union[List[str], str], ax=None, **kwargs
    ):
        """X軸固定プロット

        Args:
            step: 固定するステップ
            x: X軸の値リスト
            y: Y軸の名前リスト
            ax: プロット先の軸
            **kwargs: plot_helperに渡す追加引数

        Returns:
            プロット結果
        """
        step_obj: Step = self.fetch_step(step)
        if ax is None:
            from matplotlib import pyplot as plt

            fig, ax = plt.subplots()
        step_obj.plot_const_x(x, y, ax=ax, **kwargs)
        return ax

    def plot_const_y(
        self, step: int, y: List[float], x: Union[List[str], str], ax=None, **kwargs
    ):
        """Y軸固定プロット

        Args:
            step: 固定するステップ
            y: Y軸の値リスト
            x: X軸の名前リスト
            ax: プロット先の軸
            **kwargs: plot_helperに渡す追加引数

        Returns:
            プロット結果
        """
        step_obj: Step = self.fetch_step(step)
        if ax is None:
            from matplotlib import pyplot as plt

            fig, ax = plt.subplots()
        step_obj.plot_const_y(y, x, ax=ax, **kwargs)
        return ax


class DataExtractionMixin:
    """データ抽出機能を提供するMixin"""

    def fetch_step(self, step_num: int) -> Step:
        """指定ステップ取得関数

        指定ステップの計測値一覧を取得する関数
        :param step_num: ステップ数(1以上)

        """
        if step_num < 1:
            raise ValueError("ステップは1以上を設定してください.")
        row = [x.data[step_num - 1] for x in self.dict.values()]
        step = Step(self.chs, self.names, self.units, step_num, row)
        return step

    def fetch_near_step(
        self, item: str, value: float, comparison_mode="closest", maxstep=None
    ) -> Step:
        target = self[item].fetch_near_step(
            value, comparison_mode=comparison_mode, maxstep=maxstep
        )
        return self.fetch_step(target)

    def extract_data(self, names: List[str] = None, steps: List[int] = None):
        if not names and not steps:
            raise ValueError("ステップか名称のどちらかが必要です")
        if steps:
            idxs = [self.steps.index(x) for x in steps]
        else:
            idxs = list(range(len(self.steps)))
            steps = self.steps
        if names:
            ch_objs = [self[name] for name in names]
        else:
            ch_objs = list(self.dict.values())
        chs = [x.ch for x in ch_objs]
        names = [x.name for x in ch_objs]
        units = [x.unit for x in ch_objs]
        data = {x.ch: x.extract_data(steps) for x in ch_objs}
        from .channel_group import ChannelGroup

        return ChannelGroup(chs, names, units, steps, data)

    def remove_data(self, names: List[str] = None, steps: List[int] = None):
        """
        指定された名称またはステップのデータが削除されたChannelGroupを返します。
        :param names: 削除するチャンネル名のリスト
        :param steps: 削除するステップのリスト
        """
        if not names and not steps:
            raise ValueError("ステップか名称のどちらかが必要です")
        if steps:
            idxs = [self.steps.index(x) for x in steps]
        else:
            idxs = list(range(len(self.steps)))
            steps = []
        if names:
            # namesに含まれていないチャンネルを取得
            ch_objs = [self[name] for name in names if name not in self.names]
        else:
            ch_objs = list(self.dict.values())
        chs = [x.ch for x in ch_objs]
        names = [x.name for x in ch_objs]
        units = [x.unit for x in ch_objs]
        data = {x.ch: x.remove_data(steps) for x in ch_objs}
        remaining_steps = [step for step in self.steps if step not in steps]
        from .channel_group import ChannelGroup

        return ChannelGroup(chs, names, units, remaining_steps, data)

    def remove_none(self):
        """
        全てのチャンネルからNone値を同期的に除外した新しいChannelGroupを返します。
        あるチャンネルでNoneの位置にある値は、他のチャンネルでもNoneとして扱われます。

        Returns:
            ChannelGroup: 同期的にNone値を除外した新しいChannelGroupオブジェクト
        """
        # 各チャンネルのNoneではない位置のインデックス集合を取得
        channel_indices = []
        for ch in self.chs:
            _, indices = filter_with_indices(self.dict[ch].data)
            channel_indices.append(set(indices))

        # 全てのチャンネルで共通してNoneではない位置のインデックスを取得
        common_indices = set.intersection(*channel_indices)
        common_indices = sorted(list(common_indices))

        # 共通インデックスを使用して新しいチャンネルを作成
        new_data = {}
        for ch in self.chs:
            filtered_steps = [self.steps[i] for i in common_indices]
            filtered_data = [self.dict[ch].data[i] for i in common_indices]

            new_data[ch] = Channel(
                ch=ch,
                name=self.names[self.chs.index(ch)],
                unit=self.units[self.chs.index(ch)],
                steps=filtered_steps,
                data=filtered_data,
            )
        from .channel_group import ChannelGroup

        return ChannelGroup(
            chs=self.chs,
            names=self.names,
            units=self.units,
            steps=filtered_steps,
            data=new_data,
        )

    def remove_consecutive_duplicates_across(self, items: List[str]):
        """
        複数のチャンネル間で共通の連続重複データを削除した新しいChannelGroupオブジェクトを返します。

        すべての指定されたチャンネルで、連続するデータポイントが同じ値を持つ場合にのみ、
        その重複を1つだけ残して削除します。

        Args:
            items: 処理対象のチャンネル識別子のリスト

        Returns:
            ChannelGroup: 連続する重複を削除したデータを持つ新しいChannelGroupオブジェクト

        Examples:
            >>> # self["A"].data = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]
            >>> # self["B"].data = [10.0, 20.0, 30.0, 30.0, 40.0, 50.0]
            >>> # self["C"].data = [5, 5, 2, 2, 8, 8]
            >>> result = channel_group.remove_consecutive_duplicates_across(["A", "B", "C"])
            >>> # result["A"].data = [1.0, 1.0, 2.0, 3.0, 3.0]
            >>> # result["B"].data = [10.0, 20.0, 30.0, 40.0, 50.0]
            >>> # result["C"].data = [5, 5, 2, 8, 8]
        """
        # 指定されたチャンネルを取得
        channels = [self[item] for item in items]

        # データの長さが一致しているか確認
        data_length = len(channels[0].data)
        if not all(len(channel.data) == data_length for channel in channels):
            raise ValueError("すべてのチャンネルのデータ長は同じである必要があります")

        # 保持するインデックスを特定
        indices_to_keep = []

        # 最初のインデックスは常に保持
        indices_to_keep.append(0)

        # 2番目以降のインデックスをチェック
        for i in range(1, data_length):
            # いずれかのチャンネルで値が変化していれば、そのインデックスを保持
            should_keep = False
            for channel in channels:
                if channel.data[i] != channel.data[i - 1]:
                    should_keep = True
                    break

            if should_keep:
                indices_to_keep.append(i)

        # 新しいChannelGroupを作成
        new_data = {}
        for item in self.dict:
            channel = self[item]
            new_steps = [channel.steps[i] for i in indices_to_keep]
            new_values = [channel.data[i] for i in indices_to_keep]
            new_data[item] = Channel(
                ch=channel.ch,
                name=channel.name,
                unit=channel.unit,
                steps=new_steps,
                data=new_values,
            )
        from .channel_group import ChannelGroup

        return ChannelGroup(
            chs=self.chs,
            names=self.names,
            units=self.units,
            steps=[self.steps[i] for i in indices_to_keep] if indices_to_keep else [],
            data=new_data,
        )


class DataSplitMixin:
    def __create_split_groups(self, split_channels: Dict[str, List[Channel]]):
        """
        分割されたチャンネルからChannelGroupのリストを作成する内部メソッド

        Args:
            split_channels: チャンネル名をキー、分割されたChannelのリストを値とする辞書

        Returns:
            分割されたChannelGroupオブジェクトのリスト
        """
        result = []
        from .channel_group import ChannelGroup

        for i in range(len(split_channels[self.chs[0]])):
            chunk_data = {ch: split_channels[ch][i] for ch in self.chs}

            # 最初のチャンネルからステップ情報を取得
            chunk_steps = chunk_data[self.chs[0]].steps
            chunk_group = ChannelGroup(
                chs=self.chs,
                names=self.names,
                units=self.units,
                steps=chunk_steps,
                data=chunk_data,
            )
            result.append(chunk_group)

        return result

    def split_by_chunks(self, chunk_size: int):
        """
        チャンネルを指定サイズのチャンクに均等に分割します。
        Args:
            chunk_size: 各チャンクのサイズ
        Returns:
            chunk_size サイズのデータを持つChannelGroupオブジェクトのリスト
        Raises:
            ValueError: chunk_size が 1 未満の場合
        """
        if chunk_size < 1:
            raise ValueError("chunk_size must be greater than 0")

        split_channels = {
            ch: self.dict[ch].split_by_chunks(chunk_size) for ch in self.chs
        }

        return self.__create_split_groups(split_channels)

    def split_by_count(self, count: int):
        """
        チャンネルを指定された数の部分チャンネルに分割します。
        Args:
            count: 分割後のチャンネル数
        Returns:
            count 個のChannelGroupオブジェクトからなるリスト
        Raises:
            ValueError: count が 1 未満の場合
        """
        if count < 1:
            raise ValueError("count must be greater than 0")

        split_channels = {ch: self.dict[ch].split_by_count(count) for ch in self.chs}

        return self.__create_split_groups(split_channels)

    def split_at_indices(self, indices: List[int]):
        """
        指定されたインデックスでチャンネルグループを分割します。

        Args:
            indices: 分割するインデックスのリスト

        Returns:
            分割されたChannelGroupオブジェクトのリスト
        """
        if not indices:
            raise ValueError("indices must not be empty")

        # 各チャンネルを分割
        split_channels = {
            ch: self.dict[ch].split_at_indices(indices) for ch in self.chs
        }
        return self.__create_split_groups(split_channels)

    def split_by_threshold(self, threshold: float, include_threshold: bool = True):
        """
        データ値がしきい値を超えるかどうかに基づいてチャンネルグループを分割します。

        Args:
            threshold: 分割のしきい値
            include_threshold: Trueの場合、しきい値と等しい値は「以上」として扱う（デフォルトはTrue）

        Returns:
            しきい値で分割されたChannelGroupオブジェクトのリスト
        """
        # 各チャンネルを分割
        split_channels = {
            ch: self.dict[ch].split_by_threshold(
                threshold, include_threshold=include_threshold
            )
            for ch in self.chs
        }
        return self.__create_split_groups(split_channels)

    def split_by_segments(self, segments: List[Tuple[int, int]]):
        """
        指定されたセグメントでチャンネルグループを分割します。

        Args:
            segments: 分割するセグメントのリスト（タプル形式で開始インデックスと終了インデックスを指定）

        Returns:
            分割されたChannelGroupオブジェクトのリスト
        """
        # 各チャンネルを分割
        split_channels = {
            ch: self.dict[ch].split_by_segments(segments) for ch in self.chs
        }

        return self.__create_split_groups(split_channels)

    def split_by_condition(self, condition: Callable[[Union[float, bool, None]], bool]):
        """
        指定された条件でチャンネルグループを分割します。

        Args:
            condition: 分割条件

        Returns:
            分割されたChannelGroupオブジェクトのリスト
        """
        # 各チャンネルを分割
        split_channels = {
            ch: self.dict[ch].split_by_condition(condition) for ch in self.chs
        }

        return self.__create_split_groups(split_channels)

    def split_by_ref_ch_condition(
        self, item: str, condition: Callable[[Union[float, bool, None]], bool]
    ):
        """
        指定された条件でチャンネルグループを分割します。

        Args:
            item: 条件を適用するチャンネル名
            condition: 分割条件

        Returns:
            分割されたChannelGroupオブジェクトのリスト
        """
        # 各チャンネルを分割
        ch = self[item]
        satisfied_ch, not_satisfied_ch = ch.split_by_condition(condition)
        satisfied_steps = satisfied_ch.steps
        not_satisfied_steps = not_satisfied_ch.steps
        satisfied_ch_group = self.extract_data(steps=satisfied_steps)
        not_satisfied_group = self.extract_data(steps=not_satisfied_steps)
        return [satisfied_ch_group, not_satisfied_group]

    def split_by_integers(self, markers: List[int]):
        """
        指定したチャンネルのデータに基づいて、整数リストの値でチャンネルグループを分割します。
        マーカー値が同じデータは同じグループに振り分けられます。

        Args:
            item: マーカー値を適用するチャンネル名
            markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）

        Returns:
            分割後のChannelGroupオブジェクトのリスト。各ChannelGroupは同じマーカー値を持つデータで構成され、
            マーカー値に基づいて昇順に並べられます。

        Raises:
            ValueError: データとマーカーの長さが一致しない場合

        Examples:
            # データ値を3つのグループに分類
            markers = [2, 1, 2, 3, 1, 3]  # マーカー値が示す分類グループ
            channel_groups = channel_group.split_by_integers("ch1", markers)
            # 結果: [グループ1のChannelGroup, グループ2のChannelGroup, グループ3のChannelGroup]
        """
        from .utils.split import split_list_by_integers

        if len(self.steps) != len(markers):
            raise ValueError(
                f"{len(self.steps)}vs{len(markers)}:データリストとマーカーリストの長さは一致する必要があります."
            )

        # ステップとマーカーの組み合わせを作成
        step_marker_pairs = list(zip(self.steps, markers))

        # マーカー値によってステップを分割
        grouped_steps = split_list_by_integers(
            [pair[0] for pair in step_marker_pairs], markers
        )

        # 各グループのChannelGroupオブジェクトを作成
        result = []
        from .channel_group import ChannelGroup

        for steps_group in grouped_steps:
            # 各チャンネルから該当するステップのデータを抽出
            channels_data = {}
            for ch in self.chs:
                channel = self.dict[ch]
                # ステップに基づいてチャンネルデータを抽出
                extracted_channel = channel.extract_data(steps_group)
                channels_data[ch] = extracted_channel

            # 新しいChannelGroupオブジェクトを作成
            channel_group = ChannelGroup(
                chs=self.chs,
                names=self.names,
                units=self.units,
                steps=steps_group,
                data=channels_data,
            )
            result.append(channel_group)

        return result


class IOHandlerMixin:
    """IO操作関連機能を提供するMixin"""

    DELIMITER = "\t"
    """区切り文字"""
    TITLE_ROW = 0
    """タイトル行"""
    CH_ROW = 1
    """チャンネル行"""
    NAME_ROW = 2
    """名称行"""
    UNIT_ROW = 3
    """単位行"""
    DATA_START_ROW = 4
    """計測データ開始行"""
    STEP_COL = 0
    """ステップ列"""
    DATE_COL = 1
    """日付列"""
    TIME_COL = 2
    """時間列"""
    DATA_START_COL = 3
    """計測データ開始列"""

    def to_dict(self) -> Dict[str, Any]:
        rtn_dict = {k: v.to_dict() for k, v in self.dict.items()}
        return rtn_dict

    def to_csv(self, output_path: Union[Path, str], delimiter=",") -> None:
        if isinstance(output_path, str):
            output_path = Path(output_path)
        ch_line = delimiter.join(["CH"] + self.chs)
        name_line = delimiter.join(["NAME"] + self.names)
        unit_line = delimiter.join(["UNIT"] + self.units)
        datas = [self.dict[x].str_data for x in self.chs]
        data_lines = [delimiter.join(x) for x in zip(*datas)]
        data_lines_with_step = [
            delimiter.join([str(x), y]) for x, y in zip(self.steps, data_lines)
        ]
        all_lines = [ch_line, name_line, unit_line] + data_lines_with_step
        all_txt = "\n".join(all_lines)
        with open(output_path, "w") as f:
            f.write(all_txt)

    @classmethod
    def load(cls, f):
        """IOストリームからのクラス定義"""
        all_lines = f.io.readlines()
        title = all_lines[cls.TITLE_ROW].rstrip()
        rows = [x.rstrip() for x in all_lines]
        chs, names, units, data = cls._data_from_rows(rows)
        cols = [x for x in zip(*data)]
        steps = cls._extract_steps(rows)
        date = cls._extract_date(rows)
        time = cls._extract_time(rows)

        # Import Channel here to allow for mocking in tests
        from .channel import Channel

        data = {
            x: Channel(x, y, z, steps, w) for x, y, z, w in zip(chs, names, units, cols)
        }
        return cls(title, chs, names, units, steps, date, time, data)

    @classmethod
    def _data_from_rows(
        cls, rows
    ) -> Tuple[List[str], List[str], List[str], List[List[Union[float, bool, None]]]]:
        chs = cls._extract_ch(rows[cls.CH_ROW])
        names = cls._extract_names(rows[cls.NAME_ROW])
        units = cls._extract_units(rows[cls.UNIT_ROW])
        data = cls._extract_data(rows)
        return chs, names, units, data

    @classmethod
    def _extract_ch(cls, ch_row) -> List[str]:
        return ch_row.split(cls.DELIMITER)[cls.DATA_START_COL :]

    @classmethod
    def _extract_names(cls, name_row) -> List[str]:
        return [
            x.strip('"').strip("'")
            for x in name_row.split(cls.DELIMITER)[cls.DATA_START_COL :]
        ]

    @classmethod
    def _extract_units(cls, unit_row) -> List[str]:
        return [
            x.strip('"').strip("'")
            for x in unit_row.split(cls.DELIMITER)[cls.DATA_START_COL :]
        ]

    @classmethod
    def _extract_steps(cls, rows) -> List[int]:
        return [
            int(x.split(cls.DELIMITER)[cls.STEP_COL])
            for x in rows[cls.DATA_START_ROW :]
        ]

    @classmethod
    def _extract_date(cls, rows) -> List[str]:
        return [
            x.split(cls.DELIMITER)[cls.DATE_COL] for x in rows[cls.DATA_START_ROW :]
        ]

    @classmethod
    def _extract_time(cls, rows) -> List[str]:
        return [
            x.split(cls.DELIMITER)[cls.TIME_COL] for x in rows[cls.DATA_START_ROW :]
        ]

    @classmethod
    def _extract_data(cls, rows) -> List[List[Union[float, bool, None]]]:
        return [
            tuple(map(cls._opt_float, x.split(cls.DELIMITER)[cls.DATA_START_COL :]))
            for x in rows[cls.DATA_START_ROW :]
        ]

    @staticmethod
    def _opt_float(value: str, nan=None) -> Union[float, bool, None]:
        try:
            return float(value)
        except ValueError:
            if value == "none":
                return nan
            else:
                return False


class BaseDataContainer(ABC):
    """ExperimentとChannelGroupの抽象基底クラス

    データコンテナの共通機能を提供する抽象基底クラス
    """

    @abstractmethod
    def __init__(
        self,
        chs: List[str],
        names: List[str],
        units: List[str],
        steps: List[int],
        data: Dict[str, Channel],
    ):
        """初期化関数"""
        self.chs = chs
        self.names = names
        self.units = units
        self.steps = steps
        self.dict = data

    @abstractmethod
    def __getitem__(self, item: Union[str, int]) -> Channel:
        """キーを指定してChannelオブジェクトにアクセスする"""

        if item in self.names:
            ch = self.chs[self.names.index(item)]
            return self.dict[ch]
        else:
            return self.dict[item]
