from stream_write_ods import stream_write_ods


def test_stream_write_ods():
    ods = b''.join(stream_write_ods())
    assert isinstance(ods, bytes)
