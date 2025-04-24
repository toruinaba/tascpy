def channel_operation(name=None):
    """チャンネル操作デコレーター"""

    def decorator(func):
        operation_name = name or func.__name__

        # ChannelOperationsクラスにメソッドを動的に追加する関数
        def operation_method(self, *args, **kwargs):
            from ..operations import ChannelOperations

            new_channel = self._channel.apply(operation_name, func, *args, **kwargs)
            return ChannelOperations(new_channel)

        # メソッドをChannelOperationsクラスに追加
        from ..operations import ChannelOperations

        setattr(ChannelOperations, func.__name__, operation_method)
        return func

    return decorator
