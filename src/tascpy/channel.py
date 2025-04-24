from typing import Any, List, Dict, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import copy

from .cell import Cell
from .utils.data import filter_with_indices

from typing import TypeAlias, Union, List, Callable


@dataclass
class Channel:
    """チャンネルデータ単一格納クラス

    チャンネルデータ(タスクの列)を格納するデータクラス.
    """

    ch: str
    """チャンネル"""
    name: str
    """名前"""
    unit: str
    """単位"""
    steps: List[int]
    """ステップ"""
    data: List[Union[float, bool, None]]
    """データ"""

    def __getitem__(self, i) -> Cell:
        return Cell(self.ch, self.name, self.name, self.steps[i], self.data[i])

    def __repr__(self) -> str:
        return str(self.data)

    def __len__(self) -> int:
        """データ数"""
        return len(self.data)

    def __iter__(self):
        """イテレータ"""
        return iter(self.data)

    def __eq__(self, other: "Channel") -> bool:
        """チャンネル同士の比較"""
        if not isinstance(other, Channel):
            return False
        return (
            self.ch == other.ch
            and self.name == other.name
            and self.unit == other.unit
            and self.steps == other.steps
            and self.data == other.data
        )

    def __hash__(self) -> int:
        """ハッシュ値"""
        return hash(
            (self.ch, self.name, self.unit, tuple(self.steps), tuple(self.data))
        )

    def clone(self):
        """チャンネルオブジェクトの複製"""
        new_channel = Channel(
            self.ch,
            self.name,
            self.unit,
            copy.deepcopy(self.steps),
            copy.deepcopy(self.data),
        )
        return new_channel

    def apply(self, operation_name, transform_func, *args, **kwargs):
        new_channel = self.clone()
        new_channel.data = transform_func(self.data, *args, **kwargs)
        return new_channel

    @property
    def removed_data(self) -> List[Union[float, bool]]:
        """Noneを除くデータ"""
        from .utils.data import filter_none_values

        return filter_none_values(self.data)

    @property
    def str_data(self) -> List[str]:
        """None, Falseを変換したデータ"""
        return [self._to_str(x) for x in self.data]

    @property
    def removed_step(self) -> List[int]:
        """Noneのデータを除くステップ"""
        from .utils.data import filter_with_indices

        _, indices = filter_with_indices(self.data)
        return [self.steps[i] for i in indices]

    @property
    def max(self) -> float:
        """最大値"""
        return max(self.removed_data)

    @property
    def max_index(self) -> int:
        """最大値インデックス"""
        return self.data.index(self.max)

    @property
    def max_step(self) -> int:
        """最大値ステップ"""
        return self.max_index + 1

    @property
    def min(self) -> float:
        """最小値"""
        return min(self.removed_data)

    @property
    def min_index(self) -> int:
        """最小値インデックス"""
        return self.data.index(self.min)

    @property
    def min_step(self) -> int:
        """最小値ステップ"""
        return self.min_index + 1

    @property
    def absmax(self) -> float:
        """絶対値最大"""
        abs_list = [abs(x) for x in self.removed_data]
        return max(abs_list)

    @property
    def absmin(self) -> float:
        """絶対値最小"""
        return min([abs(x) for x in self.removed_data])

    @property
    def ops(self):
        """プロキシオブジェクトへの変換メソッド"""
        from .operations import ChannelOperations

        return ChannelOperations(self)

    def remove_none(self) -> "Channel":
        """
        None値を除外した新しいChannelオブジェクトを返します。

        Returns:
            Channel: None値を除外したデータを持つ新しいChannelオブジェクト
        """
        # filter_with_indicesを使用してNoneを除外し、インデックスを取得
        filtered_data, indices = filter_with_indices(self.data)

        # インデックスを使用してステップをフィルタリング
        filtered_steps = [self.steps[i] for i in indices]

        return Channel(
            ch=self.ch,
            name=self.name,
            unit=self.unit,
            steps=filtered_steps,
            data=filtered_data,
        )

    def remove_consecutive_duplicates(self) -> "Channel":
        """
        連続する重複データを削除した新しいChannelオブジェクトを返します。

        連続するデータポイントが同じ値を持つ場合に、その重複を1つだけ残します。
        データ圧縮や、一定値が連続するセグメントの処理に有用です。

        Returns:
            Channel: 連続する重複を削除したデータを持つ新しいChannelオブジェクト

        Examples:
            >>> channel = Channel(ch="1", name="Temperature", unit="°C",
            ...                   steps=[1, 2, 3, 4, 5, 6, 7],
            ...                   data=[20.5, 20.5, 21.0, 21.0, 21.0, 22.0, 22.0])
            >>> result = channel.remove_consecutive_duplicates()
            >>> result.data
            [20.5, 21.0, 22.0]
            >>> result.steps
            [1, 3, 6]
        """
        from .utils.data import remove_consecutive_duplicates

        # データから連続する重複を削除する
        unique_data = remove_consecutive_duplicates(self.data)

        # 残ったデータに対応するインデックスを特定
        indices = []
        last_value = None
        for i, value in enumerate(self.data):
            if value != last_value:
                indices.append(i)
                last_value = value

        # インデックスを使用してステップをフィルタリング
        filtered_steps = [self.steps[i] for i in indices]

        return Channel(
            ch=self.ch,
            name=self.name,
            unit=self.unit,
            steps=filtered_steps,
            data=unique_data,
        )

    def fetch_near_step(self, value, comparison_mode="closest", maxstep=None) -> int:
        """値検索関数
        引数に対して一番近い値を検索.
        comparison_mode="closest"の場合は距離絶対値最小
        comparison_mode="less_than"は指定値以下の距離絶対値最小
        comparison_mode="more_than"は指定値以上の距離絶対値最小
        """
        if maxstep:
            obj_data = [x for x in self.data[: maxstep - 1] if x is not None]
        else:
            obj_data = [x for x in self.data if x is not None]
        if comparison_mode == "closest":
            distances = [abs(x - value) for x in obj_data]
        elif comparison_mode == "less_than":
            distances = [abs(x - value) for x in obj_data if x - value < 0]
        elif comparison_mode == "more_than":
            distances = [abs(x - value) for x in obj_data if x - value >= 0]
        near_value = obj_data[distances.index(min(distances))]
        return self.data.index(near_value) + 1

    def extract_data(self, steps: List[int]):
        """対象ステップのデータ抽出"""
        if steps:
            idxs = [self.steps.index(x) for x in steps]
        else:
            idxs = list(range(len(self.steps)))
            steps = self.steps
        extracted = [self.data[x] for x in idxs]
        return Channel(self.ch, self.name, self.unit, steps, extracted)

    def remove_data(self, steps: List[int]) -> "Channel":
        """対象ステップのデータ削除"""
        # 除外するステップ以外のステップを取得
        remaining_steps = [step for step in self.steps if step not in steps]
        # extract_dataを使用して残すステップのみを返す
        return self.extract_data(remaining_steps)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_csv(self, output_path: Union[Path, str], delimiter=",") -> None:
        if isinstance(output_path, str):
            output_path = Path(output_path)
        ch_line = delimiter.join(["CH", self.ch])
        name_line = delimiter.join(["NAME", self.name])
        unit_line = delimiter.join(["UNIT", self.unit])
        data_lines = [
            delimiter.join([str(x), y]) for x, y in zip(self.steps, self.str_data)
        ]
        all_lines = [ch_line, name_line, unit_line] + data_lines
        all_txt = "\n".join(all_lines)
        with open(output_path, "w") as f:
            f.write(all_txt)

    def _to_str(self, value: Union[float, bool, None]) -> str:
        if isinstance(value, bool):
            return "*******"
        elif value is None:
            return "none"
        else:
            return str(value)

    def split_by_chunks(self, chunk_size: int) -> List["Channel"]:
        """
        チャンネルを指定サイズのチャンクに均等に分割します。

        Args:
            chunk_size: 各チャンクのサイズ

        Returns:
            chunk_size サイズのデータを持つChannelオブジェクトのリスト

        Raises:
            ValueError: chunk_size が 1 未満の場合
        """
        from .utils.split import split_list_by_chunks

        steps_chunks = split_list_by_chunks(self.steps, chunk_size)
        data_chunks = split_list_by_chunks(self.data, chunk_size)

        return [
            Channel(
                ch=self.ch,
                name=self.name,
                unit=self.unit,
                steps=steps_chunk,
                data=data_chunk,
            )
            for steps_chunk, data_chunk in zip(steps_chunks, data_chunks)
        ]

    def split_by_count(self, count: int) -> List["Channel"]:
        """
        チャンネルを指定された数の部分チャンネルに分割します。

        Args:
            count: 分割後のチャンネル数

        Returns:
            count 個のChannelオブジェクトからなるリスト

        Raises:
            ValueError: count が 1 未満の場合
        """
        from .utils.split import split_list_by_count

        steps_chunks = split_list_by_count(self.steps, count)
        data_chunks = split_list_by_count(self.data, count)

        return [
            Channel(
                ch=self.ch,
                name=self.name,
                unit=self.unit,
                steps=steps_chunk,
                data=data_chunk,
            )
            for steps_chunk, data_chunk in zip(steps_chunks, data_chunks)
        ]

    def split_by_condition(
        self, condition: Callable[[Union[float, bool, None]], bool]
    ) -> Tuple["Channel", "Channel"]:
        """
        条件関数に基づいてチャンネルを2つのチャンネルに分割します。

        Args:
            condition: データ値を評価する条件関数

        Returns:
            (条件を満たすデータを持つChannel, 条件を満たさないデータを持つChannel) のタプル
        """
        from .utils.split import split_list_by_condition

        # データとステップを組み合わせたアイテムのリストを作成
        combined_data = list(zip(self.steps, self.data))

        # アイテムを条件でフィルタリングする関数
        def combined_condition(item):
            _, value = item
            return condition(value)

        # 条件に基づいて組み合わせを分割
        satisfied_items, not_satisfied_items = split_list_by_condition(
            combined_data, combined_condition
        )

        # 分割された組み合わせからステップとデータを抽出
        satisfied_steps = [item[0] for item in satisfied_items]
        satisfied_data = [item[1] for item in satisfied_items]

        not_satisfied_steps = [item[0] for item in not_satisfied_items]
        not_satisfied_data = [item[1] for item in not_satisfied_items]

        # 新しいChannelオブジェクトを作成
        satisfied_channel = Channel(
            ch=self.ch,
            name=self.name,
            unit=self.unit,
            steps=satisfied_steps,
            data=satisfied_data,
        )

        not_satisfied_channel = Channel(
            ch=self.ch,
            name=self.name,
            unit=self.unit,
            steps=not_satisfied_steps,
            data=not_satisfied_data,
        )

        return satisfied_channel, not_satisfied_channel

    def split_at_indices(self, indices: List[int]) -> List["Channel"]:
        """
        指定されたインデックスでチャンネルを分割します。

        Args:
            indices: 分割位置を示すインデックスのリスト（0始まり）

        Returns:
            分割後のChannelオブジェクトを要素とするリスト
        """
        from .utils.split import split_list_at_indices

        steps_chunks = split_list_at_indices(self.steps, indices)
        data_chunks = split_list_at_indices(self.data, indices)

        return [
            Channel(
                ch=self.ch,
                name=self.name,
                unit=self.unit,
                steps=steps_chunk,
                data=data_chunk,
            )
            for steps_chunk, data_chunk in zip(steps_chunks, data_chunks)
        ]

    def split_by_threshold(
        self, threshold: float, include_threshold: bool = True
    ) -> Tuple["Channel", "Channel"]:
        """
        データ値がしきい値を超えるかどうかに基づいてチャンネルを分割します。

        Args:
            threshold: 分割のしきい値
            include_threshold: Trueの場合、しきい値と等しい値は「以上」として扱う（デフォルトはTrue）

        Returns:
            条件に応じて (threshold以上/より大きいのデータを持つChannel, threshold未満/以下のデータを持つChannel) のタプル
        """

        # 数値データのみをフィルタリング（None や boolean は除外）
        def is_valid_number(value):
            if value is None or isinstance(value, bool):
                return False
            return value >= threshold if include_threshold else value > threshold

        return self.split_by_condition(is_valid_number)

    def split_by_segments(self, segment_sizes: List[int]) -> List["Channel"]:
        """
        チャンネルを指定されたサイズのセグメントに分割します。

        Args:
            segment_sizes: 各セグメントのサイズを指定するリスト

        Returns:
            指定されたサイズに分割されたChannelオブジェクトのリスト

        Raises:
            ValueError: セグメントサイズの合計がデータサイズと一致しない場合
        """
        if sum(segment_sizes) != len(self.data):
            raise ValueError(
                f"セグメントサイズの合計 ({sum(segment_sizes)}) がデータサイズ ({len(self.data)}) と一致しません"
            )

        # 分割位置をインデックスで計算
        indices = []
        current_idx = 0
        for size in segment_sizes[
            :-1
        ]:  # 最後のセグメントは残りすべてになるので含めない
            current_idx += size
            indices.append(current_idx)

        # インデックスに基づいて分割
        return self.split_at_indices(indices)

    def split_by_integers(self, markers: List[int]) -> List["Channel"]:
        """
        整数リストの値に基づいてチャンネルを分割します。マーカー値が同じデータは同じグループに振り分けられます。

        Args:
            markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）

        Returns:
            分割後のChannelオブジェクトのリスト。各Channelは同じマーカー値を持つデータで構成されます。
            Channelはマーカー値に基づいて昇順に並べられます。

        Raises:
            ValueError: データとマーカーの長さが一致しない場合

        Examples:
            # データ値を3つのグループに分類
            markers = [2, 1, 2, 3, 1, 3]  # マーカー値が示す分類グループ
            channels = channel.split_by_integers(markers)
            # 結果: [グループ1のChannel, グループ2のChannel, グループ3のChannel]
        """
        from .utils.split import split_list_by_integers

        if len(self.data) != len(markers):
            raise ValueError(
                "データリストとマーカーリストの長さは一致する必要があります"
            )

        # ステップとデータをzipして1つのリストにする
        combined_data = list(zip(self.steps, self.data))

        # split_list_by_integersを使用して分割
        grouped_data = split_list_by_integers(combined_data, markers)

        # 分割された各グループからChannelオブジェクトを作成
        result = []
        for group in grouped_data:
            steps = [item[0] for item in group]
            data = [item[1] for item in group]
            channel = Channel(
                ch=self.ch, name=self.name, unit=self.unit, steps=steps, data=data
            )
            result.append(channel)

        return result
