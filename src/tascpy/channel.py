from typing import Any, List, Dict, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

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
    
    def remove_none(self) -> 'Channel':
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
            data=filtered_data
        )

    def fetch_near_step(
        self, value, comparison_mode="closest", maxstep=None
    ) -> int:
        """値検索関数
        引数に対して一番近い値を検索.
        comparison_mode="closest"の場合は距離絶対値最小
        comparison_mode="less_than"は指定値以下の距離絶対値最小
        comparison_mode="more_than"は指定値以上の距離絶対値最小
        """
        if maxstep:
            obj_data = [x for x in self.data[:maxstep - 1] if x is not None]
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
        """対象ステップのデータ抽出
        """
        idxs = [self.steps.index(x) for x in steps]
        extracted = [self.data[x] for x in idxs]
        return Channel(self.ch, self.name, self.unit, steps, extracted)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_csv(self, output_path: Union[Path, str], delimiter=",") -> None:
        if isinstance(output_path, str):
            output_path = Path(output_path)
        ch_line = delimiter.join(["CH", self.ch])
        name_line = delimiter.join(["NAME", self.name])
        unit_line = delimiter.join(["UNIT", self.unit])
        data_lines = [delimiter.join([str(x), y]) for x, y in zip(self.steps, self.str_data)]
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

    def split_by_chunks(self, chunk_size: int) -> List['Channel']:
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
                data=data_chunk
            )
            for steps_chunk, data_chunk in zip(steps_chunks, data_chunks)
        ]
    
    def split_by_count(self, count: int) -> List['Channel']:
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
                data=data_chunk
            )
            for steps_chunk, data_chunk in zip(steps_chunks, data_chunks)
        ]
    
    def split_by_condition(self, condition: Callable[[Union[float, bool, None]], bool]) -> Tuple['Channel', 'Channel']:
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
        satisfied_items, not_satisfied_items = split_list_by_condition(combined_data, combined_condition)
        
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
            data=satisfied_data
        )
        
        not_satisfied_channel = Channel(
            ch=self.ch,
            name=self.name,
            unit=self.unit,
            steps=not_satisfied_steps,
            data=not_satisfied_data
        )
        
        return satisfied_channel, not_satisfied_channel
    
    def split_at_indices(self, indices: List[int]) -> List['Channel']:
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
                data=data_chunk
            )
            for steps_chunk, data_chunk in zip(steps_chunks, data_chunks)
        ]
    
    def split_by_threshold(self, threshold: float, include_threshold: bool = True) -> Tuple['Channel', 'Channel']:
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
    
    def split_by_segments(self, segment_sizes: List[int]) -> List['Channel']:
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
            raise ValueError(f"セグメントサイズの合計 ({sum(segment_sizes)}) がデータサイズ ({len(self.data)}) と一致しません")
        
        # 分割位置をインデックスで計算
        indices = []
        current_idx = 0
        for size in segment_sizes[:-1]:  # 最後のセグメントは残りすべてになるので含めない
            current_idx += size
            indices.append(current_idx)
        
        # インデックスに基づいて分割
        return self.split_at_indices(indices)

    def split_by_classifier(self, classify_func: Callable[[Union[float, bool, None]], int]) -> List['Channel']:
        """
        個々のデータ値を分類クラスにマッピングしてチャンネルを分割します。
        
        Args:
            classify_func: データ値を分類クラス（1以上の整数）に変換する関数
                None、bool値の場合は None を返すことで除外可能
                
        Returns:
            分類クラスごとに分割されたChannelオブジェクトのリスト（クラス番号順）
            
        Examples:
            # データ値の範囲で3クラスに分類する例
            def value_classifier(value):
                if value is None or isinstance(value, bool):
                    return None
                if value < 0: return 1    # 負の値
                if value < 100: return 2   # 中間の値
                return 3                   # 大きな値
                
            channels = channel.split_by_classifier(value_classifier)
        """
        # 分類クラスとそのインデックスをグループ化
        class_groups = {}
        
        for i, value in enumerate(self.data):
            class_label = classify_func(value)
            if class_label is not None and isinstance(class_label, int) and class_label > 0:
                if class_label not in class_groups:
                    class_groups[class_label] = []
                class_groups[class_label].append(i)
        
        # 各分類クラスに対応するChannelを作成
        result = []
        for _, indices in sorted(class_groups.items()):
            steps = [self.steps[i] for i in indices]
            data = [self.data[i] for i in indices]
            channel = Channel(
                ch=self.ch,
                name=self.name,
                unit=self.unit,
                steps=steps,
                data=data
            )
            result.append(channel)
        
        return result
    
    def split_by_array_classifier(self, array_classify_func: Callable[[List[Union[float, bool, None]]], List[int]]) -> List['Channel']:
        """
        データ配列全体を一括で分類してチャンネルを分割します。
        
        Args:
            array_classify_func: データ値のリストを受け取り、分類クラス（1以上の整数）のリストを返す関数
                None、bool値に対応する位置には None を返すことで除外可能
                
        Returns:
            分類クラスごとに分割されたChannelオブジェクトのリスト（クラス番号順）
            
        Examples:
            # データの統計量に基づいて分類する例
            def array_classifier(values):
                valid_values = [v for v in values if isinstance(v, (int, float)) and v is not None]
                if not valid_values:
                    return [None] * len(values)
                
                mean_val = sum(valid_values) / len(valid_values)
                std_dev = (sum((x - mean_val) ** 2 for x in valid_values) / len(valid_values)) ** 0.5
                
                result = []
                for value in values:
                    if value is None or isinstance(value, bool):
                        result.append(None)
                    elif value < mean_val - std_dev:
                        result.append(1)    # 低値（-1σ未満）
                    elif value > mean_val + std_dev:
                        result.append(3)    # 高値（+1σ超）
                    else:
                        result.append(2)    # 中間値（±1σ以内）
                return result
                
            channels = channel.split_by_array_classifier(array_classifier)
        """
        # データ全体に対して分類を実行
        class_labels = array_classify_func(self.data)
        
        if len(class_labels) != len(self.data):
            raise ValueError("分類関数の出力長がデータ長と一致しません")
        
        # 分類クラスとそのインデックスをグループ化
        class_groups = {}
        
        for i, label in enumerate(class_labels):
            if label is not None and isinstance(label, int) and label > 0:
                if label not in class_groups:
                    class_groups[label] = []
                class_groups[label].append(i)
        
        # 各分類クラスに対応するChannelを作成
        result = []
        for _, indices in sorted(class_groups.items()):
            steps = [self.steps[i] for i in indices]
            data = [self.data[i] for i in indices]
            channel = Channel(
                ch=self.ch,
                name=self.name,
                unit=self.unit,
                steps=steps,
                data=data
            )
            result.append(channel)
        
        return result