import functools
import numpy as np

class TascpyOperationError(RuntimeError):
    """TascpyのOperation実行時に発生するエラーをラップする例外クラス"""
    pass

def handle_operation_errors(func):
    """Operation実行時の予期せぬエラーを捕捉し、ユーザーフレンドリなエラーに変換するデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            raise TascpyOperationError(f"[{func.__name__}] 指定された列が見つかりません。列名を確認してください: {e}") from e
        except Exception as e:
            if isinstance(e, np.linalg.LinAlgError):
                 raise TascpyOperationError(f"[{func.__name__}] 数値計算が収束しませんでした。データ範囲や特異性（変化がない等）を確認してください。詳細: {e}") from e
            if isinstance(e, TascpyOperationError):
                 raise
            raise TascpyOperationError(f"[{func.__name__}] 実行中に予期せぬエラーが発生しました: {e}") from e
    return wrapper
