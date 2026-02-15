"""
スタブファイルジェネレーター

Pylanceのための静的型ヒントと自動補完機能を提供するスタブファイルを生成します。
"""

from typing import Dict, List, Set, Any, Optional, Callable, Union, Type, get_type_hints
import inspect
import os
import importlib
import sys
from pathlib import Path
import re
import ast
import logging
import typing  # 明示的なインポート追加

from .registry import OperationRegistry
from ..core.collection import ColumnCollection
from ..domains.factory import DomainCollectionFactory



def get_return_type_annotation(func: Callable) -> str:
    """関数の戻り値の型アノテーションを取得します

    get_type_hints を使って関数の戻り値の型情報を取得し、
    適切な文字列表現に変換します。

    Args:
        func: 型情報を取得する対象の関数

    Returns:
        str: 型アノテーションの文字列表現
    """
    annotations = get_type_hints(func)
    if "return" in annotations:
        return_type = annotations["return"]
        if hasattr(return_type, "__name__"):
            return return_type.__name__
        else:
            # Union などの複合型の場合
            return str(return_type).replace("typing.", "")
    return "Any"


def format_annotation(annotation: Any) -> str:
    """型アノテーションを適切な文字列形式に変換します

    複合型や特殊な型アノテーションを適切な文字列表現に変換します。
    Union, Optional, List などの typing モジュールの型に対応しています。

    Args:
        annotation: 変換する型アノテーション

    Returns:
        str: 文字列に変換した型アノテーション
    """
    # Noneの場合はNoneを返す
    if annotation is None:
        return "None"

    # inspect.Parameter.emptyの場合はAnyを返す
    if annotation is inspect.Parameter.empty:
        return "Any"

    # 単純な型（クラス型）の場合
    if isinstance(annotation, type):
        if annotation.__name__ == "NoneType":
            return "None"
        return annotation.__name__

    # typing モジュールの型の処理
    # Python 3.8以上では get_origin と get_args を使用
    if hasattr(typing, "get_origin") and hasattr(typing, "get_args"):
        origin = typing.get_origin(annotation)
        args = typing.get_args(annotation)

        # Unionの場合（Optionalを含む）
        if origin is Union:
            # NoneTypeが含まれていればOptionalとみなす
            if type(None) in args:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    return f"Optional[{format_annotation(non_none_args[0])}]"
            # 通常のUnion
            formatted_args = [format_annotation(arg) for arg in args]
            return f"Union[{', '.join(formatted_args)}]"

        # その他のジェネリック型（List、Dict、Tuple など）
        if origin is not None:
            origin_name = (
                origin.__name__
                if hasattr(origin, "__name__")
                else str(origin).replace("typing.", "")
            )
            if args:
                formatted_args = [format_annotation(arg) for arg in args]
                return f"{origin_name}[{', '.join(formatted_args)}]"
            else:
                return origin_name

    # __origin__ と __args__ 属性を持つ場合（古いPythonバージョン向け）
    if hasattr(annotation, "__origin__") and hasattr(annotation, "__args__"):
        origin = annotation.__origin__
        args = annotation.__args__

        # Unionの場合（Optionalを含む）
        if origin is Union or str(origin).endswith("Union"):
            # NoneTypeが含まれていればOptionalとみなす
            if any(arg is type(None) or str(arg) == "NoneType" for arg in args):
                non_none_args = [
                    arg
                    for arg in args
                    if arg is not type(None) and str(arg) != "NoneType"
                ]
                if len(non_none_args) == 1:
                    return f"Optional[{format_annotation(non_none_args[0])}]"
            # 通常のUnion
            formatted_args = [format_annotation(arg) for arg in args]
            return f"Union[{', '.join(formatted_args)}]"

        # その他のジェネリック型（List、Dict、Tuple など）
        origin_name = (
            origin.__name__
            if hasattr(origin, "__name__")
            else str(origin).replace("typing.", "")
        )
        if args:
            formatted_args = [format_annotation(arg) for arg in args]
            return f"{origin_name}[{', '.join(formatted_args)}]"
        else:
            return origin_name

    # その他の型は文字列として扱い、typing. プレフィックスを削除
    return str(annotation).replace("typing.", "")


def is_returning_collection_list(func: Callable) -> bool:
    """関数が List[ColumnCollection] を返すかどうかを判定します

    Args:
        func: 判定対象の関数

    Returns:
        bool: List[ColumnCollection]を返す場合はTrue
    """
    # 型アノテーションから判定
    try:
        type_hints = get_type_hints(func)
        if "return" not in type_hints:
            return False

        return_type = type_hints["return"]
        origin = typing.get_origin(return_type)
        args = typing.get_args(return_type)

        # リスト型でかつ要素がColumnCollectionかチェック
        if origin is list and args:
            arg_type = args[0]
            try:
                if isinstance(arg_type, type) and issubclass(
                    arg_type, ColumnCollection
                ):
                    return True
            except TypeError:
                # arg_typeがクラス型でない場合
                pass
    except Exception as e:
        logging.debug(f"関数 {func.__name__} の戻り値型判定でエラー: {e}")

    # コード解析による判定（型アノテーションがない場合のフォールバック）
    try:
        source = inspect.getsource(func)
        # 'return [' または 'return List[' のパターンを検出（簡易的な検出）
        if re.search(r"return\s+\[\w", source) or "List[ColumnCollection]" in source:
            return True
    except Exception:
        pass

    return False


def generate_operation_stub(
    func: Callable, domain: str, output_file: Path, class_name: str
) -> None:
    """操作関数からスタブメソッドを生成しファイルに書き込みます

    指定された関数を解析し、メソッドチェーン用のスタブメソッドを生成して
    指定されたファイルに追記します。関数の引数、型ヒント、docstring を
    解析してスタブ情報を作成します。

    Args:
        func: スタブを生成する操作関数
        domain: 操作のドメイン名
        output_file: スタブを書き込む出力先ファイルパス
        class_name: 生成するスタブクラス名
    """
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""

    # get_type_hints を使用して正確な型情報を取得
    try:
        type_hints = get_type_hints(func)
    except Exception as e:
        logging.debug(f"関数 {func.__name__} の get_type_hints でエラー: {e}")
        type_hints = {}

    # 第一引数 (collection) を除外したパラメータと型アノテーションを取得
    params = []
    first = True
    for name, param in sig.parameters.items():
        if first:
            first = False
            continue  # collection引数をスキップ

        # パラメータの種類に応じた処理
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            # *args のような可変長位置引数
            param_str = f"*{name}"
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            # **kwargs のような可変長キーワード引数
            param_str = f"**{name}"
        else:
            # 通常の引数（位置引数またはキーワード引数）
            param_str = f"{name}"

        # 型アノテーションの処理
        # 1. get_type_hints から取得した型情報を優先
        # 2. なければ signature から取得
        if name in type_hints:
            annotation_str = format_annotation(type_hints[name])
            param_str += f": {annotation_str}"
        elif param.annotation != inspect.Parameter.empty:
            annotation_str = format_annotation(param.annotation)
            param_str += f": {annotation_str}"

        # デフォルト値の処理
        if param.default != inspect.Parameter.empty and param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.VAR_KEYWORD:
            if param.default is None:
                param_str += " = None"
            else:
                default_repr = repr(param.default)
                param_str += f" = {default_repr}"

        params.append(param_str)

    # 関数が List[ColumnCollection] を返すかどうかを判定
    if is_returning_collection_list(func):
        # CollectionListOperations を返すスタブを生成
        return_type = f'"CollectionListOperations[{class_name}]"'
    else:
        # 通常の操作関数の戻り値を取得
        # get_type_hintsの結果から、ColumnCollectionを返すかどうか判定
        original_return = "Any"
        is_collection = False
        
        if "return" in type_hints:
            ret_type = type_hints["return"]
            
            # クラス型で判定
            try:
                if isinstance(ret_type, type) and issubclass(ret_type, ColumnCollection):
                    is_collection = True
            except TypeError:
                pass
                
            # 文字列等で判定（前方参照など）
            if not is_collection:
                ret_str = str(ret_type)
                if ret_str.endswith("ColumnCollection") or ret_str == class_name:
                    is_collection = True

        if is_collection:
            # CollectionOperations (連鎖) を返す
            return_type = f'"{class_name}"'
        else:
            # 元の戻り値を返す（連鎖終了）
            # Anyの場合はAnyとするが、元の型ヒントがあればそれを使う
            if "return" in type_hints:
                return_annotation = format_annotation(type_hints["return"])
                return_type = return_annotation
            else:
                 # 型ヒントがない場合はデフォルトで連鎖継続とみなしていたが、
                 # 安全側に倒してAnyにするか？
                 # 既存コードとの互換性を考えると、明示的な型がないものはAnyが無難
                 return_type = "Any"

    # メソッド定義を生成
    joined_params = ",\n        ".join(params)
    method_def = f"""
    def {func.__name__}(
        self,
        {joined_params}
    ) -> {return_type}:
        \"\"\"{doc}\"\"\"
        ...
    """

    # ファイルに書き込み
    with output_file.open("a", encoding="utf-8") as f:
        f.write(method_def)
        f.write("\n")


def generate_list_operation_stub(
    func: Callable, output_file: Path
) -> None:
    """CollectionListOperations用のスタブメソッドを生成します"""
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""

    try:
        type_hints = get_type_hints(func)
    except Exception:
        type_hints = {}

    # パラメータの構築 (generate_operation_stubと同様)
    params = []
    first = True
    for name, param in sig.parameters.items():
        if first:
            first = False
            continue

        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            param_str = f"*{name}"
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            param_str = f"**{name}"
        else:
            param_str = f"{name}"

        if name in type_hints:
            annotation_str = format_annotation(type_hints[name])
            param_str += f": {annotation_str}"
        elif param.annotation != inspect.Parameter.empty:
            annotation_str = format_annotation(param.annotation)
            param_str += f": {annotation_str}"

        if param.default != inspect.Parameter.empty and param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.VAR_KEYWORD:
            if param.default is None:
                param_str += " = None"
            else:
                default_repr = repr(param.default)
                param_str += f" = {default_repr}"

        params.append(param_str)

    # 戻り値の型判定
    # ColumnCollection (またはそのサブクラス) を返す場合は CollectionListOperations[C]
    # それ以外は List[T]
    
    is_collection_return = False
    if "return" in type_hints:
        ret_type = type_hints["return"]
        # Unionの場合の考慮が必要だが、簡易的に
        try:
             if isinstance(ret_type, type) and issubclass(ret_type, ColumnCollection):
                 is_collection_return = True
        except TypeError:
             # 文字列参照などの場合
             if str(ret_type).endswith("ColumnCollection"):
                 is_collection_return = True
    
    # generate_operation_stubのis_returning_collection_listも考慮
    if is_returning_collection_list(func):
        # List[ColumnCollection] を返す場合 -> List[CollectionListOperations] ?
        # mapの実装では、List[CollectionListOperations] ではなく flattened CollectionListOperations になる場合と
        # List[List[Collection]] になる場合があり得るが、
        # 基本的には CollectionListOperations を返すと仮定 (splitなど)
        # もし split が List[Collection] を返すなら、list_proxy.split は CollectionListOperations (of original) を返す
        # mapの実装: results.append(result) -> resultがlistならList[List]
        # しかしColListOpsはList[Collection]をラップするもの。
        # splitの結果は「分割されたコレクションのリスト」。
        # これを各要素に適用すると、「リストのリスト」ができる。
        # ここは型定義が難しいが、実用的には CollectionListOperations[C] でチェインを続けたいケースが多い
        return_type = '"CollectionListOperations[C]"'
    elif is_collection_return:
        return_type = '"CollectionListOperations[C]"'
    else:
        # 通常の値を返す場合 -> List[ReturnType]
        original_ret = "Any"
        if "return" in type_hints:
             original_ret = format_annotation(type_hints["return"])
        return_type = f"List[{original_ret}]"

    joined_params = ",\n        ".join(params)
    method_def = f"""
    def {func.__name__}(
        self,
        {joined_params}
    ) -> {return_type}:
        \"\"\"{doc}\"\"\"
        ...
    """

    with output_file.open("a", encoding="utf-8") as f:
        f.write(method_def)
        f.write("\n")



def generate_collection_list_operations_stub(stub_dir: Path) -> None:
    """CollectionListOperationsクラスのスタブを生成します

    Args:
        stub_dir: スタブファイルを保存するディレクトリのパス
    """
    list_proxy_file = stub_dir / "list_proxy.py"
    
    with list_proxy_file.open("w", encoding="utf-8") as f:
        f.write("# 自動生成されたCollectionListOperationsスタブ - 編集しないでください\n")
        f.write("from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic, overload\n")
        f.write("from ..core.collection import ColumnCollection\n")
        f.write("from .proxy_base import CollectionOperationsBase\n")
        f.write("from typing import Literal\n")

        # ドメインごとのコレクションクラスをインポート
        domains = OperationRegistry.discover_domains()
        for domain in domains:
            collection_cls = DomainCollectionFactory.get_collection_class(domain)
            if collection_cls:
                if hasattr(collection_cls, "__module__") and hasattr(collection_cls, "__name__"):
                    module_path = collection_cls.__module__
                    class_name = collection_cls.__name__
                    
                    # src.tascpy.domains.xxx -> ..domains.xxx に変換
                    if "tascpy.domains" in module_path:
                        parts = module_path.split("tascpy.domains.")
                        if len(parts) > 1:
                            relative_path = f"..domains.{parts[1]}"
                            f.write(f"from {relative_path} import {class_name}\n")
                        else:
                             f.write(f"from ..domains.{domain} import {class_name}\n")
                    else:
                        f.write(f"from ..domains.{domain} import {class_name}\n")
        
        f.write("\n")
        
        f.write("# コレクション型のTypeVar\n")
        f.write("C = TypeVar('C', bound=ColumnCollection)\n\n")
        
        f.write("class CollectionListOperations(Generic[C]):\n")
        f.write('    """複数のColumnCollectionを一度に操作するためのプロキシクラス\n')
        f.write("    \n")
        f.write("    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。\n")
        f.write("    実際の実行には使用されません。\n")
        f.write('    """\n\n')
        
        # 基本メソッドを追加
        f.write("    def __len__(self) -> int:\n")
        f.write('        """コレクションリストの長さを返します"""\n')
        f.write("        ...\n\n")
        
        f.write("    def __getitem__(\n")
        f.write("        self, index: Union[int, slice]\n")
        f.write("    ) -> Union[CollectionOperationsBase[C], \"CollectionListOperations[C]\"]:\n")
        f.write('        """指定されたインデックスのCollectionOperationsを返します\n')
        f.write("        \n")
        f.write("        Args:\n")
        f.write("            index: アクセスするインデックスまたはスライス\n")
        f.write("            \n")
        f.write("        Returns:\n")
        f.write("            インデックスの場合はCollectionOperations、スライスの場合はCollectionListOperations\n")
        f.write("            \n")
        f.write("        Raises:\n")
        f.write("            IndexError: インデックスが範囲外の場合\n")
        f.write("            TypeError: インデックスが整数またはスライスでない場合\n")
        f.write('        """\n')
        f.write("        ...\n\n")
        
        # map メソッド
        f.write("    def map(\n")
        f.write("        self, operation: str, *args: Any, **kwargs: Any\n")
        f.write("    ) -> Union[\"CollectionListOperations[C]\", List[Any]]:\n")
        f.write('        """各コレクションに同じ操作を適用します\n')
        f.write("        \n")
        f.write("        Args:\n")
        f.write("            operation: 適用する操作名\n")
        f.write("            *args: 操作に渡す位置引数\n")
        f.write("            **kwargs: 操作に渡すキーワード引数\n")
        f.write("            \n")
        f.write("        Returns:\n")
        f.write("            操作結果のCollectionListOperationsまたは結果のリスト\n")
        f.write("            \n")
        f.write("        Raises:\n")
        f.write("            AttributeError: 指定された操作が存在しない場合\n")
        f.write('        """\n')
        f.write("        ...\n\n")
        
        # filter メソッド
        f.write("    def filter(\n")
        f.write("        self, predicate: Callable[[C], bool]\n")
        f.write("    ) -> \"CollectionListOperations[C]\":\n")
        f.write('        """条件を満たすコレクションだけをフィルタリングします\n')
        f.write("        \n")
        f.write("        Args:\n")
        f.write("            predicate: フィルタリング条件を判定する関数\n")
        f.write("            \n")
        f.write("        Returns:\n")
        f.write("            フィルタリングされたコレクションを持つCollectionListOperations\n")
        f.write('        """\n')
        f.write("        ...\n\n")
        
        # concat メソッド
        f.write("    def concat(self) -> CollectionOperationsBase[C]:\n")
        f.write('        """全てのコレクションを連結して一つのCollectionOperationsを返します\n')
        f.write("        \n")
        f.write("        Returns:\n")
        f.write("            連結されたデータを持つCollectionOperations\n")
        f.write("            \n")
        f.write("        Raises:\n")
        f.write("            ValueError: 連結するコレクションが存在しない場合\n")
        f.write('        """\n')
        f.write("        ...\n\n")
        
        # end_all メソッド
        f.write("    def end_all(self) -> List[C]:\n")
        f.write('        """操作を終了し、ColumnCollectionのリストを返します"""\n')
        f.write("        ...\n\n")
        
        # as_domain メソッド
        # ドメインごとのオーバーロードを追加
        domains = OperationRegistry.discover_domains()
        for domain in domains:
            collection_cls = DomainCollectionFactory.get_collection_class(domain)
            if collection_cls and hasattr(collection_cls, "__name__"):
                 class_name = collection_cls.__name__
            else:
                 class_name = "ColumnCollection"
            
            # Literalのインポートが必要（冒頭で追加済み）
            # クラス名のインポートも必要だが、ここでは文字列定義で簡略化するか、適切にimport文を追加する必要がある
            # list_proxy.pyの冒頭で必要なimportを追加するロジックがないため、
            # Generic[C] の C が解決されることを期待するか、クラス名を文字列として扱う
            # ただし、Genericなので C が変わるわけではない。
            # CollectionListOperations[NewDomainCollection] を返す
            
            # クラスのインポートを追加する必要がある
            # ここでは簡易的に文字列で指定
            
            f.write("    @overload\n")
            f.write(f"    def as_domain(self, domain: Literal['{domain}'], **kwargs: Any) -> \"CollectionListOperations[{class_name}]\":\n")
            f.write("        ...\n\n")

        f.write("    def as_domain(self, domain: str, **kwargs: Any) -> \"CollectionListOperations\":\n")
        f.write('        """全てのコレクションを指定されたドメインに変換します\n')
        f.write("        \n")
        f.write("        Args:\n")
        f.write("            domain: 変換先のドメイン名\n")
        f.write("            **kwargs: 変換に渡す追加引数\n")
        f.write("            \n")
        f.write("        Returns:\n")
        f.write("            変換されたコレクションリスト\n")
        f.write('        """\n')
        f.write("        ...\n")

    # 全ドメインの操作を追加
    domains = OperationRegistry.discover_domains()
    # 既に追加したメソッド名を追跡して重複を防止 (coreとdomainで重複がある場合など)
    added_methods = {"map", "filter", "concat", "end_all", "as_domain"}
    
    # coreを先に処理
    if "core" in domains:
        ops = OperationRegistry.get_operations("core")
        for name, func in ops.items():
            if name not in added_methods:
                generate_list_operation_stub(func, list_proxy_file)
                added_methods.add(name)
    
    # 他のドメインを処理
    for domain in domains:
        if domain == "core":
            continue
        ops = OperationRegistry.get_operations(domain)
        for name, func in ops.items():
            if name not in added_methods:
                generate_list_operation_stub(func, list_proxy_file)
                added_methods.add(name)



def generate_stubs() -> None:
    """全てのドメインとそれらの操作メソッドのスタブを生成します

    各ドメインの操作関数を解析し、VS Code の Pylance などの静的型チェッカーで
    自動補完と型チェックが機能するためのスタブファイルを生成します。
    生成されたスタブは typing ディレクトリに保存されます。
    """
    logging.info("スタブファイルの生成を開始します...")

    # スタブディレクトリを作成 - operations/stubs から typing に変更
    stub_dir = Path(__file__).parent.parent / "typing"
    stub_dir.mkdir(exist_ok=True)

    # __init__.pyファイルを作成
    init_file = stub_dir / "__init__.py"
    with init_file.open("w", encoding="utf-8") as f:
        f.write("# 自動生成されたスタブファイル - 編集しないでください\n")
        f.write("# このファイルはPylanceの自動補完と型チェック用です\n\n")
        f.write(
            "from typing import cast, TypeVar, Union, overload, Any, Dict, List, Optional, Callable, Generic, Literal\n"
        )
        f.write("from ..core.collection import ColumnCollection\n\n")

    # すべてのドメインを発見
    domains = OperationRegistry.discover_domains()

    # プロキシ基本クラスの定義をスタブ化
    proxy_file = stub_dir / "proxy_base.py"
    with proxy_file.open("w", encoding="utf-8") as f:
        f.write("# 自動生成されたプロキシベーススタブ - 編集しないでください\n")
        f.write(
            "from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic, overload, Literal\n"
        )
        f.write("from ..core.collection import ColumnCollection\n\n")
        f.write("# コレクション型のTypeVar\n")
        f.write("C = TypeVar('C', bound=ColumnCollection)\n")
        f.write("# 戻り値型のTypeVar\n")
        f.write("T = TypeVar('T', bound='CollectionOperationsBase')\n\n")
        f.write("class CollectionOperationsBase(Generic[C]):\n")
        f.write('    """コレクション操作の基底クラス"""\n\n')
        f.write("    def end(self) -> C:\n")
        f.write('        """操作チェーンを終了し、最終的なColumnCollectionを取得"""\n')
        f.write("        ...\n\n")
        f.write("    def debug(self, message: Optional[str] = None) -> T:\n")
        f.write('        """デバッグメッセージを表示\n')
        f.write("        \n")
        f.write("        Args:\n")
        f.write("            message: デバッグメッセージ\n")
        f.write("        \n")
        f.write("        Returns:\n")
        f.write("            自身を返す\n")
        f.write('        """\n')
        f.write("        ...\n\n")
    
    # CollectionListOperationsのスタブファイルを生成
    generate_collection_list_operations_stub(stub_dir)

    # ドメインごとのコレクションクラスとインポートパスを取得
    domain_to_collection_class = {}
    domain_import_paths = {}

    for domain in domains:
        collection_cls = DomainCollectionFactory.get_collection_class(domain)
        if collection_cls:
            # クラス名を取得
            if hasattr(collection_cls, "__name__"):
                class_name = collection_cls.__name__
            else:
                class_name = str(collection_cls)
            
            domain_to_collection_class[domain] = class_name
            
            # モジュールパスを取得
            if hasattr(collection_cls, "__module__"):
                # src.tascpy.domains.xxx -> ..domains.xxx に変換
                module_path = collection_cls.__module__
                if "tascpy.domains" in module_path:
                    # tascpy.domains以降を抽出
                    parts = module_path.split("tascpy.domains.")
                    if len(parts) > 1:
                        relative_path = f"..domains.{parts[1]}"
                        domain_import_paths[domain] = relative_path
                    else:
                        domain_import_paths[domain] = f"..domains.{domain}"
                else:
                     # フォールバック
                    domain_import_paths[domain] = f"..domains.{domain}"
            else:
                domain_import_paths[domain] = f"..domains.{domain}"
        else:
            # デフォルト
            domain_to_collection_class[domain] = "ColumnCollection"
            domain_import_paths[domain] = f"..domains.{domain}"


    # coreドメインの操作を取得しておく（他のドメインのスタブにも追加するため）
    core_operations = OperationRegistry.get_operations("core") 

    for domain in domains:
        # ドメイン固有のスタブファイルを作成
        domain_file = stub_dir / f"{domain}.py"

        # ドメイン特化コレクションクラス名
        collection_class_name = domain_to_collection_class.get(
            domain, "ColumnCollection"
        )

        with domain_file.open("w", encoding="utf-8") as f:
            f.write(
                f"# 自動生成された{domain}ドメインのスタブファイル - 編集しないでください\n"
            )
            f.write(
                "from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast, Generic, overload, Literal\n"
            )
            f.write("from ..core.collection import ColumnCollection\n")

            # ドメイン特化コレクションのインポート
            if domain != "core" and collection_class_name != "ColumnCollection":
                # ドメイン特化型のインポートパス
                import_path = domain_import_paths.get(domain, f"..domains.{domain}")
                f.write(f"from {import_path} import {collection_class_name}\n")

            f.write("from .proxy_base import CollectionOperationsBase\n")
            f.write("from .list_proxy import CollectionListOperations\n")
            
            # 非coreドメインは必要なドメイン特化クラスをインポート（as_domainの戻り値型用）
            if domain != "core":
                f.write("from .core import CoreCollectionOperations\n")
                
                # 相互参照のために他のドメインの特化クラスをインポート
                for other_domain in domains:
                    if other_domain != domain and other_domain != "core":
                        other_class = f"{other_domain.title().replace('_', '')}CollectionOperations"
                        # 循環インポートを避けるためTYPE_CHECKINGを使用
                        f.write(f"from typing import TYPE_CHECKING\n")
                        f.write(f"if TYPE_CHECKING:\n")
                        f.write(f"    from .{other_domain} import {other_class}\n")
            
            f.write("\n")

            # 他のドメイン型のインポート(coreドメインの場合)
            if domain == "core":
                # as_domain メソッドで使用するために他のドメインの型をインポート
                for other_domain in domains:
                    if other_domain != "core":
                        other_class = f"{other_domain.title().replace('_', '')}CollectionOperations"
                        f.write(f"from .{other_domain} import {other_class}\n")
                f.write("\n")

            # ドメイン固有のクラス名を生成 (例: CoreCollectionOperations)
            class_name = f"{domain.title().replace('_', '')}CollectionOperations"

            # 特化コレクション型をジェネリックパラメータとして使用
            f.write(
                f"class {class_name}(CollectionOperationsBase[{collection_class_name}]):\n"
            )
            f.write(f'    """{domain}ドメインの操作メソッドスタブ定義\n')
            f.write(f"    \n")
            f.write(
                f"    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。\n"
            )
            f.write(f"    実際の実行には使用されません。\n")
            f.write(f'    """\n\n')

            # end() メソッドをオーバーライド
            f.write(f"    def end(self) -> {collection_class_name}:\n")
            f.write(
                f'        """操作チェーンを終了し、最終的なColumnCollectionを取得"""\n'
            )
            f.write(f"        ...\n\n")

            # デバッグメソッドをオーバーライド
            f.write(
                f"    def debug(self, message: Optional[str] = None)"
                f' -> "{class_name}":\n'
            )
            f.write(f'        """デバッグメッセージを表示\n')
            f.write(f"        \n")
            f.write(f"        Args:\n")
            f.write(f"            message: デバッグメッセージ\n")
            f.write(f"        \n")
            f.write(f"        Returns:\n")
            f.write(f"            {class_name}: 自身を返す\n")
            f.write(f'        """\n')
            f.write(f"        ...\n\n")

        # ドメインの操作関数を取得
        operations = OperationRegistry.get_operations(domain)

        # 各操作関数のスタブを生成
        for name, func in operations.items():
            generate_operation_stub(func, domain, domain_file, class_name)

        # 非coreドメインの場合は、core操作のスタブも追加
        if domain != "core":
            for name, func in core_operations.items():
                # 同じ名前の操作が既にドメイン固有のものとして定義されていない場合のみ追加
                if name not in operations:
                    generate_operation_stub(func, "core", domain_file, class_name)

        # as_domain メソッドのスタブをオーバーロード形式で追加
        if domain == "core":
            with domain_file.open("a", encoding="utf-8") as f:
                # ドメインごとにオーバーロードバージョンを追加
                for target_domain in domains:
                    if target_domain != "core":
                        target_class = f"{target_domain.title().replace('_', '')}CollectionOperations"
                        # Literal型を使用したオーバーロード版（デフォルト値なし）
                        f.write(f"\n    @overload\n")
                        f.write(
                            f"    def as_domain(self, domain: Literal['{target_domain}'], **kwargs: Any) -> {target_class}:\n"
                        )
                        f.write(f"        ...\n")

                # 一般版（どのドメインにも対応）
                f.write(
                    f"\n    def as_domain(self, domain: str, **kwargs: Any) -> Any:\n"
                )
                f.write(f'        """現在のコレクションを指定されたドメインに変換\n')
                f.write(f"        \n")
                f.write(f"        Args:\n")
                f.write(f"            domain: 変換先のドメイン名\n")
                f.write(f"            **kwargs: 変換に渡す追加の引数\n")
                f.write(f"        \n")
                f.write(f"        Returns:\n")
                f.write(
                    f"            適切なドメイン特化型のCollectionOperationsオブジェクト\n"
                )
                f.write(f'        """\n')
                f.write(f"        ...\n")
        
        # 非coreドメインの場合は、as_domain メソッドも追加
        if domain != "core":
            with domain_file.open("a", encoding="utf-8") as f:
                # ドメインごとにオーバーロードバージョンを追加
                for target_domain in domains:
                    if target_domain != domain:  # 自分自身のドメインは除外
                        target_class = f"{target_domain.title().replace('_', '')}CollectionOperations"
                        # Literal型を使用したオーバーロード版
                        f.write(f"\n    @overload\n")
                        f.write(
                            f"    def as_domain(self, domain: Literal['{target_domain}'], **kwargs: Any) -> {target_class}:\n"
                        )
                        f.write(f"        ...\n")

                # 一般版（最低限CoreCollectionOperationsを返すことを保証）
                f.write(
                    f"\n    def as_domain(self, domain: str, **kwargs: Any) -> Union[CoreCollectionOperations, Any]:\n"
                )
                f.write(f'        """現在のコレクションを指定されたドメインに変換\n')
                f.write(f"        \n")
                f.write(f"        Args:\n")
                f.write(f"            domain: 変換先のドメイン名\n")
                f.write(f"            **kwargs: 変換に渡す追加の引数\n")
                f.write(f"        \n")
                f.write(f"        Returns:\n")
                f.write(
                    f"            適切なドメイン特化型のCollectionOperationsオブジェクト\n"
                )
                f.write(f'        """\n')
                f.write(f"        ...\n")
        

        # ドメインクラスを__init__.pyに登録
        with init_file.open("a", encoding="utf-8") as f:
            f.write(f"from .{domain} import {class_name}\n")

    # CollectionListOperationsを__init__.pyに追加
    with init_file.open("a", encoding="utf-8") as f:
        f.write("from .list_proxy import CollectionListOperations\n")

    # 型情報を__init__.pyに追加
    with init_file.open("a", encoding="utf-8") as f:
        f.write("\n# 型ヒント用の変数\n")
        f.write("T = TypeVar('T', bound='CollectionOperationsBase')\n\n")
        f.write("# ドメインごとのスタブ型をエクスポート\n")
        f.write("__all__ = [\n")
        for domain in domains:
            class_name = f"{domain.title().replace('_', '')}CollectionOperations"
            f.write(f"    '{class_name}',\n")
        f.write("    'CollectionListOperations',\n")
        f.write("]\n")

    logging.info(f"スタブファイルを {stub_dir} に生成しました")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_stubs()
