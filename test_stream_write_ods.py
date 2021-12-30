from collections import OrderedDict
from io import BytesIO
from pyexcel_odsr import get_data
from stream_write_ods import stream_write_ods


def test_stream_write_ods():
    data = get_data(BytesIO(b''.join(stream_write_ods())))
    assert data == OrderedDict([('Sheet 1', [['Col 1', 'Col 2']])])
