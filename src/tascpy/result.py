from typing import Any, List, Union
from dataclasses import dataclass


@dataclass
class Result:
    """チャンネルデータ単一格納クラス

    チャンネルデータ(タスクの列)を格納するデータクラス.
    """

    ch: str
    """チャンネル"""
    name: str
    """名前"""
    unit: str
    """単位"""
    data: List[Union[float, bool, None]]
    """データ"""

    def __getitem__(self, i):
        return self.data[i]

    @property
    def removed_data(self):
        """Noneの除くデータ"""
        return [x for x in self.data if x is not None]

    @property
    def max(self):
        """最大値"""
        return max(self.removed_data)

    @property
    def maxrow(self):
        """最大値インデックス"""
        return self.data.index(self.max)

    @property
    def maxstep(self):
        """最大値ステップ"""
        return self.maxrow + 1

    @property
    def min(self):
        """最小値"""
        return min(self.removed_data)

    @property
    def minrow(self):
        """最小値インデックス"""
        return self.data.index(self.min)

    @property
    def minstep(self):
        """最小値ステップ"""
        return self.minrow + 1

    @property
    def absmax(self):
        """絶対値最大"""
        abs_list = [abs(x) for x in self.removed_data]
        return max(abs_list)

    @property
    def absmin(self):
        """絶対値最小"""
        return min([abs(x) for x in self.removed_data])


class Results:
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

    def __init__(self, f):
        """初期化関数"""
        all_lines = f.io.readlines()
        self.title = all_lines[self.TITLE_ROW].rstrip()
        rows = [x.rstrip() for x in all_lines]
        self.chs, self.names, units, data = self._data_from_rows(rows)
        cols = [x for x in zip(*data)]
        self.steps = self._extract_steps(rows)
        self.date = self._extract_date(rows)
        self.time = self._extract_time(rows)
        self.dict = {
            x: Result(x, y, z, w)
            for x, y, z, w in zip(self.chs, self.names, units, cols)
        }  

    def __getitem__(self, item):
        if item in self.names:
            ch = self.chs[self.names.index(item)]
            return self.dict[ch]
        else:
            return self.dict[item]

    def get_step(self, step_num: int):
        """指定ステップ取得関数

        指定ステップの計測値一覧を取得する関数
        :param step_num: ステップ数(1以上)

        """
        if step_num < 1:
            raise ValueError("ステップは1以上を設定してください.")
        row = [x.data[step_num - 1] for x in self.dict.values()]
        return row
    
    def _data_from_rows(self, rows):
        chs = self._extract_ch(rows[self.CH_ROW])
        names = self._extract_names(rows[self.NAME_ROW])
        units = self._extract_units(rows[self.UNIT_ROW])
        data = self._extract_data(rows)
        return chs, names, units, data

    def _extract_ch(self, ch_row):
        return ch_row.split(self.DELIMITER)[self.DATA_START_COL:]

    def _extract_names(self, name_row):
        return name_row.split(self.DELIMITER)[self.DATA_START_COL:]

    def _extract_units(self, unit_row):
        return unit_row.split(self.DELIMITER)[self.DATA_START_COL:]

    def _extract_steps(self, rows):
        return [int(x.split(self.DELIMITER)[self.STEP_COL]) for x in rows[self.DATA_START_ROW:]]

    def _extract_date(self, rows):
        return [x.split('\t')[self.DATE_COL] for x in rows[self.DATA_START_ROW:]]
    
    def _extract_time(self, rows):
        return [x.split('\t')[self.TIME_COL] for x in rows[self.DATA_START_ROW:]]

    def _extract_data(self, rows):
        return [
            tuple(map(self._opt_float, x.split('\t')[self.DATA_START_COL:]))
            for x in rows[self.DATA_START_ROW:]
        ]

    def _opt_float(self, value: str, nan = None):
        try:
            return float(value)
        except ValueError:
            if value == "none":
                return nan
            else:
                return False