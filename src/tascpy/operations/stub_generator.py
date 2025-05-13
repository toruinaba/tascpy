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
        if param.default != inspect.Parameter.empty:
            if param.default is None:
                param_str += " = None"
            else:
                default_repr = repr(param.default)
                param_str += f" = {default_repr}"

        params.append(param_str)

    # 返値の型を CollectionOperations の適切なサブクラスに変更 - 常にメソッドチェーンのため自分自身を返す
    return_type = f'"{class_name}"'

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
            "from typing import cast, TypeVar, Union, overload, Any, Dict, List, Optional, Callable\n"
        )
        f.write("from ..core.collection import ColumnCollection\n\n")

    # すべてのドメインを発見
    domains = OperationRegistry.discover_domains()

    # プロキシ基本クラスの定義をスタブ化
    proxy_file = stub_dir / "proxy_base.py"
    with proxy_file.open("w", encoding="utf-8") as f:
        f.write("# 自動生成されたプロキシベーススタブ - 編集しないでください\n")
        f.write(
            "from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic\n"
        )
        f.write("from ..core.collection import ColumnCollection\n\n")
        f.write("T = TypeVar('T', bound='CollectionOperationsBase')\n\n")
        f.write("class CollectionOperationsBase:\n")
        f.write('    """コレクション操作の基底クラス"""\n\n')
        f.write("    def end(self) -> ColumnCollection:\n")
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

    for domain in domains:
        # ドメイン固有のスタブファイルを作成
        domain_file = stub_dir / f"{domain}.py"
        with domain_file.open("w", encoding="utf-8") as f:
            f.write(
                f"# 自動生成された{domain}ドメインのスタブファイル - 編集しないでください\n"
            )
            f.write(
                "from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast\n"
            )
            f.write("from ..core.collection import ColumnCollection\n")
            f.write("from .proxy_base import CollectionOperationsBase\n\n")

            # ドメイン固有のクラス名を生成 (例: CoreCollectionOperations)
            class_name = f"{domain.title().replace('_', '')}CollectionOperations"

            f.write(f"class {class_name}(CollectionOperationsBase):\n")
            f.write(f'    """{domain}ドメインの操作メソッドスタブ定義\n')
            f.write(f"    \n")
            f.write(
                f"    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。\n"
            )
            f.write(f"    実際の実行には使用されません。\n")
            f.write(f'    """\n\n')

            # end() メソッドをオーバーライド
            f.write(f"    def end(self) -> ColumnCollection:\n")
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

        # ドメインクラスを__init__.pyに登録
        with init_file.open("a", encoding="utf-8") as f:
            f.write(f"from .{domain} import {class_name}\n")

    # 型情報を__init__.pyに追加
    with init_file.open("a", encoding="utf-8") as f:
        f.write("\n# 型ヒント用の変数\n")
        f.write("T = TypeVar('T', bound='CollectionOperationsBase')\n\n")
        f.write("# ドメインごとのスタブ型をエクスポート\n")
        f.write("__all__ = [\n")
        for domain in domains:
            class_name = f"{domain.title().replace('_', '')}CollectionOperations"
            f.write(f"    '{class_name}',\n")
        f.write("]\n")

    logging.info(f"スタブファイルを {stub_dir} に生成しました")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_stubs()
