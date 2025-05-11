"""
get_type_hints の動作を確認するためのテストスクリプト
"""

from typing import Optional, List, Dict, Any, Union, get_type_hints
import inspect
import sys


def test_function(
    param1: str,
    param2: int,
    param3: Optional[float] = None,
    param4: List[str] = None,
    param5: Dict[str, Any] = None,
) -> Union[str, None]:
    """テスト用関数"""
    return "test"


def main():
    """メイン関数"""
    print(f"Python バージョン: {sys.version}")

    try:
        # get_type_hints を使用して型情報を取得
        print("\n==== get_type_hints の結果 ====")
        type_hints = get_type_hints(test_function)

        for param, type_hint in type_hints.items():
            print(f"{param}: {type_hint}")
            print(f"  - repr: {repr(type_hint)}")
            print(f"  - str: {str(type_hint)}")
            if hasattr(type_hint, "__origin__"):
                print(f"  - origin: {type_hint.__origin__}")
            if hasattr(type_hint, "__args__"):
                print(f"  - args: {type_hint.__args__}")
    except Exception as e:
        print(f"get_type_hints でエラーが発生: {e}")
        print(f"エラータイプ: {type(e).__name__}")

    try:
        # inspect.signature を使用した場合の比較
        print("\n==== inspect.signature の結果 ====")
        sig = inspect.signature(test_function)

        for name, param in sig.parameters.items():
            print(f"{name}: {param.annotation}")
            print(f"  - repr: {repr(param.annotation)}")
            print(f"  - annotation クラス: {type(param.annotation).__name__}")

            # Optional などの複合型の詳細情報
            if hasattr(param.annotation, "__origin__"):
                print(f"  - origin: {param.annotation.__origin__}")
            if hasattr(param.annotation, "__args__"):
                print(f"  - args: {param.annotation.__args__}")
    except Exception as e:
        print(f"inspect.signature でエラーが発生: {e}")

    # 特定の型について
    print("\n==== Optional[float] の検査 ====")
    opt_float_type = Optional[float]
    print(f"Optional[float]: {opt_float_type}")
    print(f"  - repr: {repr(opt_float_type)}")
    print(f"  - str: {str(opt_float_type)}")
    if hasattr(opt_float_type, "__origin__"):
        print(f"  - origin: {opt_float_type.__origin__}")
    if hasattr(opt_float_type, "__args__"):
        print(f"  - args: {opt_float_type.__args__}")


if __name__ == "__main__":
    main()
