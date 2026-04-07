from typing import Dict, Callable, Optional, Any, List, Set, Union, Tuple
import inspect
import importlib
import pkgutil
from pathlib import Path
import functools

from .abstraction import inject_columns, transform_column, filter_rows, select_columns, inject_step_values, store_result

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
    def register_functional(
        cls,
        func: Callable,
        *,
        domain: str = "core",
        name: Optional[str] = None,
        inject_columns: Optional[Dict[str, Any]] = None,
        transform_column: Optional[Dict[str, Any]] = None,
        filter_rows: bool = False,
        select_columns: Optional[Dict[str, Any]] = None,
        inject_step_values: Optional[Dict[str, Any]] = None,
        store_result: Optional[Dict[str, Any]] = None,
        store_xy_result: Optional[Dict[str, Any]] = None,
        store_point_result: Optional[Dict[str, Any]] = None,
        store_multiple_results: Optional[Dict[str, Any]] = None,
        process_by_group: Optional[Dict[str, Any]] = None,
        shared_with: Optional[List[str]] = None,
        signature_override: Optional[Dict[str, Any]] = None,
        extra_decorators: Optional[List[Callable]] = None,
        inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
    ) -> Callable:
        """純粋関数をオペレーションとして登録するアダプターメソッド

        純粋関数（ColumnCollectionに依存しない関数）をラップし、
        適切なデコレータを適用してレジストリに登録します。

        Args:
            func: 登録する純粋関数
            domain: 登録先ドメイン
            name: オペレーション名（デフォルトは関数名）
            inject_columns: @inject_columns への引数辞書
            transform_column: @transform_column への引数辞書
            filter_rows: @filter_rows を適用するかどうか
            select_columns: @select_columns への引数辞書
            inject_step_values: @inject_step_values への引数辞書
            store_result: @store_result への引数辞書
            store_xy_result: @store_xy_result への引数辞書
            store_point_result: @store_point_result への引数辞書
            store_multiple_results: @store_multiple_results への引数辞書
            process_by_group: @process_by_group への引数辞書
            shared_with: 共有ドメインのリスト
            signature_override: スタブ生成用のシグネチャ上書き情報
                                {param_name: (type, default)} の形式
            extra_decorators: 追加で適用するデコレータのリスト（transform_columnの内側に適用されます）
            inject_metadata: メタデータ生成関数 (args, kwargs, result) -> dict
        """
        op_name = name or func.__name__
        
        # 1. Start with the pure function
        wrapped_func = func
        
        # 1.5 Apply extra decorators (inner-most, before abstraction decorators)
        if extra_decorators:
            for decorator in extra_decorators:
                wrapped_func = decorator(wrapped_func)
        
        # 2. Apply decorators in reverse order (inner to outer)
        
        # @inject_step_values (inner-most logic usually?)
        # Actually logic depends. usually:
        # transform_column handles inject_columns internally.
        
        if transform_column is not None:
             # transform_column applies store_result, handle_missing, inject_columns
             from .abstraction import transform_column as tc_decorator
             # Inject metadata into transform_column kwargs
             tc_kwargs = transform_column.copy()
             if inject_metadata:
                 tc_kwargs["inject_metadata"] = inject_metadata
             wrapped_func = tc_decorator(**tc_kwargs)(wrapped_func)
        else:
             # Manual composition
             if inject_step_values is not None:
                 from .abstraction import inject_step_values as isv_decorator
                 wrapped_func = isv_decorator(**inject_step_values)(wrapped_func)
                 
             if inject_columns is not None:
                 from .abstraction import inject_columns as ic_decorator
                 wrapped_func = ic_decorator(**inject_columns)(wrapped_func)
                 
             if filter_rows:
                 from .abstraction import filter_rows as fr_decorator
                 wrapped_func = fr_decorator(wrapped_func)
                 
             if store_result is not None:
                 from .abstraction import store_result as sr_decorator
                 # Ensure wrapper name is set for result naming
                 wrapped_func.__name__ = op_name
                 # Inject metadata into store_result kwargs
                 sr_kwargs = store_result.copy()
                 if inject_metadata:
                     sr_kwargs["inject_metadata"] = inject_metadata
                 wrapped_func = sr_decorator(**sr_kwargs)(wrapped_func)
             elif store_xy_result is not None:
                 from .abstraction import store_xy_result as cxr_decorator
                 wrapped_func.__name__ = op_name
                 sr_kwargs = store_xy_result.copy()
                 if inject_metadata:
                     sr_kwargs["inject_metadata"] = inject_metadata
                 wrapped_func = cxr_decorator(**sr_kwargs)(wrapped_func)
             elif store_point_result is not None:
                 from .abstraction import store_point_result as cpr_decorator
                 wrapped_func.__name__ = op_name
                 sr_kwargs = store_point_result.copy()
                 if inject_metadata:
                     sr_kwargs["inject_metadata"] = inject_metadata
                 wrapped_func = cpr_decorator(**sr_kwargs)(wrapped_func)
             elif store_multiple_results is not None:
                 from .abstraction import store_multiple_results as smr_decorator
                 wrapped_func.__name__ = op_name
                 sr_kwargs = store_multiple_results.copy()
                 if inject_metadata:
                     sr_kwargs["inject_metadata"] = inject_metadata
                 wrapped_func = smr_decorator(**sr_kwargs)(wrapped_func)
             elif process_by_group is not None:
                 from .abstraction import process_by_group as pbg_decorator
                 wrapped_func.__name__ = op_name
                 sr_kwargs = process_by_group.copy()
                 wrapped_func = pbg_decorator(**sr_kwargs)(wrapped_func)
             elif inject_metadata is not None:
                 # If store_result is not used, but inject_metadata is provided,
                 # we attach metadata to the result (as a tuple).
                 
                 # Prepare a wrapper that injects metadata
                 # Note: inject_metadata func signature is (args, kwargs, result) -> dict
                 # We need to capture the args passed to this specific wrapper.
                 
                 _meta_gen = inject_metadata
                 
                 # We need to use functools.wraps explicitly or manage __name__ manually
                 # 'wrapped_func' here is the function after inner decorators (like filters, inject_columns).
                 # So its args match what the inner decorators expect?
                 # Wait, 'wrapped_func' is built from inside out.
                 # inject_columns converts (collection, *args) -> (values, ...).
                 # so 'wrapped_func' expects (values, ...) or (steps, values, ...).
                 
                 # However, `inject_metadata` usually wants to see the arguments passed *to the operation* (e.g. min, max).
                 # Those arguments are passed through `inject_columns` wrapper if they are not consumed?
                 # `inject_columns` consumes `columns_arg` if specified in kwargs?
                 # But usually `min`, `max` are passed through.
                 
                 # The wrapper we are adding is OUTER to `inject_columns` etc?
                 # No, `wrapped_func` is currently the result of `inject_columns(filter_rows(... func ...))`.
                 # So `wrapped_func` signature is `(collection, *args, **kwargs)`.
                 
                 # So if we wrap it here, we see `collection` and user args.
                 # `inject_metadata` expects `(args, kwargs, result)`.
                 # `store_result` passes `(args, kwargs, result)` where `args` is tuple of user args (excluding collection).
                 
                 target_func = wrapped_func
                 
                 @functools.wraps(target_func)
                 def meta_wrapper(collection_or_data, *args, **kwargs):
                     # Call inner
                     result = target_func(collection_or_data, *args, **kwargs)
                     
                     # Generate metadata
                     # We pass args/kwargs as seen here.
                     # If collection was passed as first arg?
                     # store_result excludes collection from args passed to metadata generator.
                     
                     # Check if first arg is collection?
                     # wrapper signature is typically (collection, *args).
                     # So `args` tuple effectively excludes collection.
                     
                     try:
                         meta = _meta_gen(args, kwargs, result)
                         if meta:
                             return result, meta
                         return result
                     except Exception:
                         # Fallback or strict?
                         # Ideally should propagate error for debugging
                         raise 

                 wrapped_func = meta_wrapper

        # @select_columns (outermost usually)
        if select_columns is not None:
             from .abstraction import select_columns as sc_decorator
             wrapped_func = sc_decorator(**select_columns)(wrapped_func)

        # 3. Rename wrapper to match operation name
        wrapped_func.__name__ = op_name
        wrapped_func.__doc__ = func.__doc__
        
        # 4. Attach Signature Metadata for Stub Generator
        # This is CRITICAL for correct stub generation
        if signature_override or inject_columns or transform_column:
             # Construct virtual signature params if not provided explicitly?
             # For now, just attach what is passed or infer simplistic default
             # Stub generator will look for __tascpy_stub_signature__
             
             # If inject_columns is used with num_inputs=1, 
             # the first arg of pure func (values) becomes 'column' (or columns_arg) in operation.
             
             stub_sig = {}
             if signature_override:
                 stub_sig = signature_override
             
             # Auto-inference logic could go here, but explicit override is safer for now.
             # Or we can mark it as "wrapped_functional"
             
             setattr(wrapped_func, "__tascpy_stub_signature__", stub_sig)
             setattr(wrapped_func, "__tascpy_functional_origin__", func)

        # Flag if the operation returns a ColumnCollection
        returns_collection = any([
            store_result is not None,
            store_xy_result is not None,
            store_point_result is not None,
            store_multiple_results is not None,
            process_by_group is not None,
            transform_column is not None,
            filter_rows is True,
        ])
        if returns_collection:
            setattr(wrapped_func, "__tascpy_returns_collection__", True)


        # 5. Register
        cls.register(wrapped_func, domain=domain, shared_with=shared_with)
        
        return wrapped_func


    @classmethod
    def register_pipeline(
        cls,
        steps: List[Tuple[Callable, Dict[str, Any]]],
        domain: str = "core",
        name: Optional[str] = None,
        inject_columns: Optional[Dict[str, Any]] = None,
        transform_column: Optional[Dict[str, Any]] = None,
        filter_rows: Optional[bool] = None,
        select_columns: Optional[Dict[str, Any]] = None,
        inject_step_values: Optional[Dict[str, Any]] = None,
        store_result: Optional[Dict[str, Any]] = None,
        store_multiple_results: Optional[Dict[str, Any]] = None,
        process_by_group: Optional[Dict[str, Any]] = None,
        shared_with: Optional[List[str]] = None,
        signature_override: Optional[Dict[str, Any]] = None,
        extra_decorators: Optional[List[Callable]] = None,
        inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
    ) -> Callable:
        """パイプライン操作を登録します

        複数の純粋関数を連結して一つの操作として定義します。
        
        Args:
            steps: (関数, config_kwargs) のタプルリスト。
                   特殊なステップとして `tascpy.analytics.operations.abstraction.filter_rows` などを
                   含めることで、フラグ（filter_rows=True）を自動設定できます。
            ...他は register_functional と同様
        """
        # Control steps detection
        from .abstraction import filter_rows as filter_rows_decorator
        
        real_steps = []
        inferred_filter_rows = False
        
        for step_item in steps:
            # Handle (func, config) or just func
            if isinstance(step_item, tuple):
                func, config = step_item
            else:
                func, config = step_item, {}
                
            if func is filter_rows_decorator:
                inferred_filter_rows = True
            else:
                real_steps.append((func, config))
        
        # Use inferred filter_rows if not explicitly set
        final_filter_rows = filter_rows if filter_rows is not None else inferred_filter_rows

        if not real_steps:
             raise ValueError("パイプラインには少なくとも一つの有効なステップが必要です")

        # Define Composed Function
        def composed_func(first_arg, *args, **kwargs):
            current_val = first_arg
            
            for i, (func, config) in enumerate(real_steps):
                 # Inspect signature to filter kwargs for this function
                 sig = inspect.signature(func)
                 call_kwargs = {}
                 
                 # 1. Config (Static/Fixed)
                 call_kwargs.update(config)
                 
                 # 2. Dynamic Kwargs
                 # If *kwargs contains potential args for this step
                 for k, v in kwargs.items():
                     if k in sig.parameters and k not in call_kwargs:
                         call_kwargs[k] = v
                 
                 # 3. Positional Args
                 # Only first step receives original positional args
                 if i == 0:
                      current_val = func(current_val, *args, **call_kwargs)
                 else:
                      current_val = func(current_val, **call_kwargs)
            
            return current_val

        # Copy docstring/name from result? Or user provided?
        composed_func.__name__ = name or f"pipeline_{real_steps[0][0].__name__}"
        
        return cls.register_functional(
            composed_func,
            domain=domain,
            name=name,
            inject_columns=inject_columns,
            transform_column=transform_column,
            filter_rows=final_filter_rows,
            select_columns=select_columns,
            inject_step_values=inject_step_values,
            store_result=store_result,
            store_multiple_results=store_multiple_results,
            process_by_group=process_by_group,
            shared_with=shared_with,
            signature_override=signature_override,
            extra_decorators=extra_decorators,
            inject_metadata=inject_metadata
        )


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
register_functional = OperationRegistry.register_functional
register_pipeline = OperationRegistry.register_pipeline
