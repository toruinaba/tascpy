from typing import Dict, Callable, Optional, Any, List, Set, Union
import inspect
import importlib
import pkgutil
from pathlib import Path


class OperationRegistry:
    """操作を登録・管理するためのレジストリ"""

    # ドメイン → {操作名 → 操作関数} の辞書
    _operations: Dict[str, Dict[str, Callable]] = {}

    # 初期化済みドメインの集合
    _initialized_domains: Set[str] = set()

    # スタブファイルが生成されたかどうかのフラグ
    _stubs_generated: bool = False

    @classmethod
    def register(
        cls,
        func: Optional[Callable] = None,
        *,
        domain: str = "core",
        shared_with: Optional[List[str]] = None,
    ) -> Callable:
        """操作をレジストリに登録するデコレーターです

        指定されたドメインに操作（関数）を登録し、必要に応じて複数のドメインと共有します。

        Args:
            func: 登録する関数（デコレーターとして使用する場合）
            domain: 操作のドメイン（"core", "timeseries", "signal" など）
            shared_with: 操作を共有する追加ドメインのリスト

        Returns:
            Callable: 登録された関数（変更なし）

        例:
            @operation
            def filter_by_value(collection, column_name, value):
                # 実装...

            @operation(domain="timeseries")
            def resample(collection, frequency):
                # 実装...
        """

        def decorator(f: Callable) -> Callable:
            # 主要ドメインに登録
            if domain not in cls._operations:
                cls._operations[domain] = {}

            # 操作名（関数名）を取得
            operation_name = f.__name__

            # 主要ドメインに登録
            cls._operations[domain][operation_name] = f

            # 追加ドメインに共有（指定されている場合）
            if shared_with:
                for shared_domain in shared_with:
                    if shared_domain not in cls._operations:
                        cls._operations[shared_domain] = {}
                    cls._operations[shared_domain][operation_name] = f

            return f

        # デコレーターとして直接使用する場合
        if func is None:
            return decorator

        # 引数なしで直接関数に適用する場合
        return decorator(func)

    @classmethod
    def get_operations(cls, domain: str = "core") -> Dict[str, Callable]:
        """指定されたドメインの操作を取得します

        ドメイン内に登録されている全ての操作を辞書形式で返します。
        まだ初期化されていないドメインの場合は、自動的に検出・初期化します。

        Args:
            domain: 操作のドメイン名

        Returns:
            Dict[str, Callable]: 指定されたドメインの操作の辞書 {操作名 → 関数}
        """
        # 初期化されていない場合は自動検出
        if domain not in cls._initialized_domains:
            cls._discover_operations_in_domain(domain)

        return cls._operations.get(domain, {})

    @classmethod
    def get_all_operations(cls) -> Dict[str, Callable]:
        """全ての操作を取得します

        全てのドメインに登録されている操作を一つの辞書にまとめて返します。
        複数のドメインに同名の操作がある場合は、後のドメインの操作で上書きされます。

        Returns:
            Dict[str, Callable]: 全ドメインの操作を統合した辞書 {操作名 → 関数}
        """
        all_ops = {}
        for domain_ops in cls._operations.values():
            all_ops.update(domain_ops)
        return all_ops

    @classmethod
    def discover_domains(cls) -> List[str]:
        """利用可能なドメインを動的に検出します

        operations ディレクトリ内のサブディレクトリからドメイン名を検出し、
        それぞれのドメインのオペレーションを自動的に読み込みます。

        Returns:
            List[str]: 検出されたドメイン名のリスト
        """
        # コアドメインは常に存在する
        domains = ["core"]

        try:
            # 操作モジュールのパスを検出
            operations_path = Path(__file__).parent

            # サブディレクトリを探索
            for item in operations_path.iterdir():
                if item.is_dir() and item.name != "__pycache__" and item.name != "core":
                    domains.append(item.name)

            # 各ドメインの操作を読み込む
            for domain in domains:
                if domain not in cls._initialized_domains:
                    cls._discover_operations_in_domain(domain)

        except (ImportError, ModuleNotFoundError) as e:
            print(f"ドメイン検出中にエラーが発生しました: {str(e)}")

        return domains

    @classmethod
    def _discover_operations_in_domain(cls, domain: str) -> None:
        """指定ドメインの操作関数を動的に読み込む

        Args:
            domain: 読み込むドメイン名
        """
        try:
            # ドメインパスを構築
            if domain == "core":
                domain_path = f"src.operations.core"
            else:
                domain_path = f"src.operations.{domain}"

            # モジュールをインポート
            try:
                domain_package = importlib.import_module(domain_path)
            except (ImportError, ModuleNotFoundError):
                # ドメインパッケージが存在しない場合は空の辞書を登録して終了
                if domain not in cls._operations:
                    cls._operations[domain] = {}
                cls._initialized_domains.add(domain)
                return

            # パッケージのパスを取得
            domain_dir = getattr(domain_package, "__path__", None)

            if domain_dir:
                # 全モジュールを読み込む
                for _, name, is_pkg in pkgutil.iter_modules(
                    domain_dir, f"{domain_path}."
                ):
                    if not is_pkg:
                        try:
                            importlib.import_module(name)
                        except (ImportError, ModuleNotFoundError) as e:
                            print(
                                f"モジュール '{name}' の読み込み中にエラーが発生しました: {str(e)}"
                            )

            cls._initialized_domains.add(domain)

        except Exception as e:
            print(f"ドメイン '{domain}' の操作検出中にエラーが発生しました: {str(e)}")
            # エラーが発生した場合でも辞書を初期化
            if domain not in cls._operations:
                cls._operations[domain] = {}
            cls._initialized_domains.add(domain)

    @classmethod
    def list_available_operations(
        cls, domain: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """利用可能な操作の一覧を取得します

        特定のドメインまたは全てのドメインにおける利用可能な操作を一覧表示します。

        Args:
            domain: 特定のドメイン（None の場合は全ドメイン）

        Returns:
            Dict[str, List[str]]: {ドメイン名: [操作名のリスト]} の辞書
        """
        result = {}

        if domain:
            # 特定のドメインの操作を取得
            ops = cls.get_operations(domain)
            result[domain] = sorted(ops.keys())
        else:
            # 全ドメインの操作を取得
            domains = cls.discover_domains()
            for d in domains:
                ops = cls.get_operations(d)
                result[d] = sorted(ops.keys())

        return result

    @classmethod
    def get_operation_info(
        cls, operation_name: str, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """操作の詳細情報を取得します

        指定された操作名に対応する関数の詳細情報（シグネチャ、ドキュメント、パラメータ情報など）を
        辞書形式で取得します。

        Args:
            operation_name: 操作名
            domain: ドメイン（None の場合は全ドメインから検索）

        Returns:
            Dict[str, Any]: 操作の詳細情報を含む辞書
        """
        # 操作関数を見つける
        func = None
        found_domain = None

        if domain:
            # 特定のドメインから検索
            ops = cls.get_operations(domain)
            if operation_name in ops:
                func = ops[operation_name]
                found_domain = domain
        else:
            # 全ドメインから検索
            for d, ops in cls._operations.items():
                if operation_name in ops:
                    func = ops[operation_name]
                    found_domain = d
                    break

        if not func:
            return {"error": f"操作 '{operation_name}' が見つかりません"}

        # 関数の情報を取得
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""

        return {
            "name": operation_name,
            "domain": found_domain,
            "signature": str(sig),
            "docstring": doc,
            "parameters": [
                {
                    "name": name,
                    "default": (
                        param.default if param.default is not param.empty else None
                    ),
                    "annotation": (
                        str(param.annotation)
                        if param.annotation is not param.empty
                        else None
                    ),
                    "required": param.default is param.empty and param.name != "self",
                }
                for name, param in sig.parameters.items()
                if name != "self"  # self パラメータを除外
            ],
        }

    @classmethod
    def generate_stubs(cls) -> None:
        """操作のスタブファイルを生成します

        Pylance などの静的型チェッカーのための型情報を提供するスタブファイルを生成します。
        このメソッドは、メソッドチェーンの自動補完を有効にするために使用されます。
        """
        # スタブ生成を避けるための循環インポートの回避
        if cls._stubs_generated:
            return

        from .stub_generator import generate_stubs

        generate_stubs()

        # スタブの最終修正を実行（型情報の修正）
        cls._fix_generated_stubs()

        cls._stubs_generated = True

    @classmethod
    def _fix_generated_stubs(cls) -> None:
        """生成されたスタブファイルの型情報を修正する

        特にジェネリック型が正しく処理されない場合の修正を行います。
        """
        import re
        import os
        from pathlib import Path

        # スタブディレクトリパス
        stubs_dir = Path(__file__).parent / "stubs"
        if not stubs_dir.exists() or not stubs_dir.is_dir():
            return

        # Pythonファイルを順に処理
        for file_path in stubs_dir.glob("*.py"):
            if file_path.name == "__init__.py" or file_path.name == "proxy_base.py":
                continue

            # ファイルを読み込み
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # パターンを検出して修正
            # Optional = None を Optional[Any] = None に修正
            content = re.sub(
                r"(\w+): Optional = None", r"\1: Optional[Any] = None", content
            )

            # Optional = ... を Optional[Any] = ... に修正
            content = re.sub(
                r"(\w+): Optional = ([^N][^o][^n][^e].*)",
                r"\1: Optional[Any] = \2",
                content,
            )

            # List = None を List[Any] = None に修正
            content = re.sub(r"(\w+): List = None", r"\1: List[Any] = None", content)

            # Dict = None を Dict[Any, Any] = None に修正
            content = re.sub(
                r"(\w+): Dict = None", r"\1: Dict[Any, Any] = None", content
            )

            # Union = None を Union[Any] = None に修正
            content = re.sub(r"(\w+): Union = None", r"\1: Union[Any] = None", content)

            # 修正した内容を書き戻す
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)


# デコレーターのエイリアス（より簡潔な名前で使用可能）
operation = OperationRegistry.register
