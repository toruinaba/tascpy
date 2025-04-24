from .channel import Channel


class ChannelOperations:
    def __init__(self, channel: Channel):
        self._channel = channel

    def end(self):
        """チェーンを終了してチャンネルを返却する関数"""
        return self._channel
