from src.tascpy.channel import Channel
import src.tascpy.basic_operations


def test_filter_none():
    channel = Channel("@1", "test", "m", [1, 2, 3], [1, None, 3])
    res = channel.ops.filter_none().end()
    assert res.data == [1, 3]
    assert res.steps == [1, 2, 3]
