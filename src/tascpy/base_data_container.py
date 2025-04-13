from typing import Any, List, Dict, Tuple, Union, Callable
from pathlib import Path
from abc import ABC, abstractmethod

from .channel import Channel
from .step import Step

from .utils.plot import plot_helper
from .utils.data import filter_with_indices


class PlottingMixin:
    """プロット機能を提供するMixin"""

    def plot_history(self, y: Union[List[str], str], ax=None, show_unit=True, **kwargs):
        if isinstance(y, str):
            x_data = self.steps
            y_data = self[y].data
            x_label = "Step"
            y_label = f"{self[y].name} [{self[y].unit}]" if show_unit else self[y].name
            return plot_helper(x_data, y_data, x_label, y_label, ax, **kwargs)

    def plot_xy(self, x: Union[List[str], str], y: Union[List[str], str], ax=None, show_unit=True, **kwargs):
        if ax:
            if isinstance(x, str) and isinstance(y, str):
                ax.plot(self[x].data, self[y].data, label=y, **kwargs)
                ax.set_xlabel(f"{self[x].name} [{self[x].unit}]" if show_unit else self[x].name)
                ax.set_ylabel(f"{self[y].name} [{self[y].unit}]" if show_unit else self[y].name)
            elif isinstance(x, list) and isinstance(y, list):
                if len(x) != len(y):
                    raise ValueError("凡例の数が一致しません.")
                for name_x, name_y in zip(x, y):
                    ax.plot(self[name_x].data, self[name_y].data, label=y, **kwargs)
                    ax.set_xlabel(f"{self[name_x].name} [{self[name_x].unit}]" if show_unit else self[name_x].name)
                    ax.set_ylabel(f"{self[name_y].name} [{self[name_y].unit}]" if show_unit else self[name_y].name)
            return ax
        else:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            if isinstance(x, str) and isinstance(y, str):
                plt.plot(self[x].data, self[y].data, **kwargs)              
                plt.xlabel(f"{self[x].name} [{self[x].unit}]" if show_unit else self[x].name)
                plt.ylabel(f"{self[y].name} [{self[y].unit}]" if show_unit else self[y].name)
            elif isinstance(x, list) and isinstance(y, list):
                if len(x) != len(y):
                    raise ValueError("凡例の数が一致しません")
                for name_x, name_y in zip(x, y):
                    plt.plot(self[name_x].data, self[name_y].data, **kwargs)
                    plt.xlabel(f"{self[name_x].name} [{self[name_x].unit}]" if show_unit else self[name_x].name)
                    plt.ylabel(f"{self[name_y].name} [{self[name_y].unit}]" if show_unit else self[name_y].name)


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
        self, 
        item: str,
        value: float,
        comparison_mode="closest",
        maxstep=None
    ) -> Step:
        target = self[item].fetch_near_step(value, comparison_mode=comparison_mode, maxstep=maxstep)
        return self.fetch_step(target)

    def extract_data(
        self,
        names: List[str]=None,
        steps: List[int]=None
    ):
        if not names and not steps:
            raise ValueError("ステップか名称のどちらかが必要です")
        if steps:
            idxs = [self.steps.index(x) for x in steps]
        else:
            idxs = list(range(len(self.steps)))
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
                data=filtered_data
            )
        from .channel_group import ChannelGroup
        return ChannelGroup(
            chs=self.chs,
            names=self.names,
            units=self.units,
            steps=filtered_steps,
            data=new_data
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
            chunk_data = {
                ch: split_channels[ch][i]
                for ch in self.chs
            }
            
            # 最初のチャンネルからステップ情報を取得
            chunk_steps = chunk_data[self.chs[0]].steps
            chunk_group = ChannelGroup(
                chs=self.chs,
                names=self.names,
                units=self.units,
                steps=chunk_steps,
                data=chunk_data
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
            ch: self.dict[ch].split_by_chunks(chunk_size)
            for ch in self.chs
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
        
        split_channels = {
            ch: self.dict[ch].split_by_count(count)
            for ch in self.chs
        }
        
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
            ch: self.dict[ch].split_at_indices(indices)
            for ch in self.chs
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
            ch: self.dict[ch].split_by_threshold(threshold, include_threshold=include_threshold)
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
            ch: self.dict[ch].split_by_segments(segments)
            for ch in self.chs
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
            ch: self.dict[ch].split_by_condition(condition)
            for ch in self.chs
        }
        
        return self.__create_split_groups(split_channels)

    def split_by_ref_ch_condition(self, item: str, condition: Callable[[Union[float, bool, None]], bool]):
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
        satisfied_ch_group = self.extract_data(satisfied_steps, steps=satisfied_steps)
        not_satisfied_group = self.extract_data(not_satisfied_steps, steps=not_satisfied_steps)
        return [satisfied_ch_group, not_satisfied_group]


class IOHandlerMixin:
    """IO操作関連機能を提供するMixin"""

    DELIMITER = '\t'
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
        data_lines_with_step = [delimiter.join([str(x), y]) for x, y in zip(self.steps, data_lines)]
        all_lines = [ch_line, name_line, unit_line] + data_lines_with_step
        all_txt = "\n".join(all_lines)
        with open(output_path, "w") as f:
            f.write(all_txt)

    @classmethod
    def load(cls, f):
        """IOストリームからのクラス定義
        """
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
            x: Channel(x, y, z, steps, w)
            for x, y, z, w in zip(chs, names, units, cols)
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
        return ch_row.split(cls.DELIMITER)[cls.DATA_START_COL:]

    @classmethod
    def _extract_names(cls, name_row) -> List[str]:
        return [x.strip('"').strip("'") for x in name_row.split(cls.DELIMITER)[cls.DATA_START_COL:]]

    @classmethod
    def _extract_units(cls, unit_row) -> List[str]:
        return [x.strip('"').strip("'") for x in unit_row.split(cls.DELIMITER)[cls.DATA_START_COL:]]

    @classmethod
    def _extract_steps(cls, rows) -> List[int]:
        return [int(x.split(cls.DELIMITER)[cls.STEP_COL]) for x in rows[cls.DATA_START_ROW:]]

    @classmethod
    def _extract_date(cls, rows) -> List[str]:
        return [x.split(cls.DELIMITER)[cls.DATE_COL] for x in rows[cls.DATA_START_ROW:]]
    
    @classmethod
    def _extract_time(cls, rows) -> List[str]:
        return [x.split(cls.DELIMITER)[cls.TIME_COL] for x in rows[cls.DATA_START_ROW:]]

    @classmethod
    def _extract_data(cls, rows) -> List[List[Union[float, bool, None]]]:
        return [
            tuple(map(cls._opt_float, x.split(cls.DELIMITER)[cls.DATA_START_COL:]))
            for x in rows[cls.DATA_START_ROW:]
        ]

    @staticmethod
    def _opt_float(value: str, nan = None) -> Union[float, bool, None]:
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
        data: Dict[str, Channel]
    ):
        """初期化関数"""
        self.chs = chs
        self.names = names
        self.units = units
        self.steps = steps
        self.dict = data

    @abstractmethod
    def __getitem__(self, item) -> Channel:
        """キーを指定してChannelオブジェクトにアクセスする"""
        if item in self.names:
            ch = self.chs[self.names.index(item)]
            return self.dict[ch]
        else:
            return self.dict[item]
