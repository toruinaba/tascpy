from typing import Any, List, Dict, Tuple, Union
from pathlib import Path

from .channel import Channel
from .step import Step

class Experimental_data:
    """全計測結果格納クラス
    """

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

    def __init__(
        self,
        title: str,
        chs: List[str],
        names: List[str],
        units: List[str],
        steps: List[int],
        date: List[str],
        time: List[str],
        data: Dict[str, Channel]
    ):
        """初期化関数"""
        self.title = title
        self.chs = chs
        self.names = names
        self.units = units
        self.steps = steps
        self.date = date
        self.time = time
        self.dict = data

    def __getitem__(self, item) -> Channel:
        if item in self.names:
            ch = self.chs[self.names.index(item)]
            return self.dict[ch]
        else:
            return self.dict[item]

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
        method=0,
        maxstep=None
    ) -> Step:
        target = self[item].fetch_near_step(value, method=method, maxstep=maxstep)
        return self.fetch_step(target)

    def extract_data(
        self,
        names: List[str]=None,
        steps: List[int]=None
    ):
        if not names and steps:
            raise ValueError("ステップか名称のどちらかが必要です")
        if steps:
            idxs = [self.steps.index(x) for x in steps]
        else:
            idxs = list(range(len(self.steps)))
        if names:
            ch_objs = [self[name] for name in names]
        chs = [x.ch for x in ch_objs]
        names = [x.name for x in ch_objs]
        units = [x.unit for x in ch_objs]
        date = [self.date[x] for x in idxs]
        time = [self.time[x] for x in idxs]
        data = {x.ch: x.extract_data(steps) for x in ch_objs}
        return Experimental_data(self.title, chs, names, units, steps, date, time, data)

    def plot_history(self, y: Union[List[str], str], ax=None, show_unit=True, **kwargs):
        if ax:
            if isinstance(y, str):
                ax.plot(self.steps, self[y].data, label=y, **kwargs)
                ax.set_xlabel("Step")
                ax.set_ylabel(f"{self[y].name} [{self[y].unit}]" if show_unit else self[y].name)
            elif isinstance(y, list):
                for name in y:
                    ax.plot(self.steps, self[name].data, label=name, **kwargs)
            return ax
        else:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            if isinstance(y, str):
                plt.plot(self.steps, self[y].data, **kwargs)
                plt.xlabel("Step")
                plt.ylabel(f"{self[y].name} [{self[y].unit}]" if show_unit else self[y].name)
            elif isinstance(y, list):
                for name in y:
                    plt.plot(self.steps, self[name].data, **kwargs)

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
        return name_row.split(cls.DELIMITER)[cls.DATA_START_COL:]

    @classmethod
    def _extract_units(cls, unit_row) -> List[str]:
        return unit_row.split(cls.DELIMITER)[cls.DATA_START_COL:]

    @classmethod
    def _extract_steps(cls, rows) -> List[int]:
        return [int(x.split(cls.DELIMITER)[cls.STEP_COL]) for x in rows[cls.DATA_START_ROW:]]

    @classmethod
    def _extract_date(cls, rows) -> List[str]:
        return [x.split('\t')[cls.DATE_COL] for x in rows[cls.DATA_START_ROW:]]
    
    @classmethod
    def _extract_time(cls, rows) -> List[str]:
        return [x.split('\t')[cls.TIME_COL] for x in rows[cls.DATA_START_ROW:]]

    @classmethod
    def _extract_data(cls, rows) -> List[List[Union[float, bool, None]]]:
        return [
            tuple(map(cls._opt_float, x.split('\t')[cls.DATA_START_COL:]))
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
