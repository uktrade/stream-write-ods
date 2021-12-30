from collections import OrderedDict
from io import BytesIO
from tempfile import NamedTemporaryFile
from pandas_ods_reader import read_ods
from stream_write_ods import stream_write_ods


def test_stream_write_ods():
    with NamedTemporaryFile() as f:
        f.write(b''.join(stream_write_ods()))
        f.flush()
        data = list(read_ods(f.name).T.to_dict().values())

    assert data == [{'Col 1': 'Value 1', 'Col 2': 'Value 2'}]
