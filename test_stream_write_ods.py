from collections import OrderedDict
from io import BytesIO
from tempfile import NamedTemporaryFile
from pandas_ods_reader import read_ods
from stream_write_ods import stream_write_ods


def test_openable_with_pandas():
    with NamedTemporaryFile() as f:
        f.write(b''.join(stream_write_ods()))
        f.flush()
        data = list(read_ods(f.name, "Sheet 1").T.to_dict().values())

    assert data == [{'Col 1': 'Value 1', 'Col 2': 'Value 2'}]


def test_has_correct_magic_values():
    data = b''.join(stream_write_ods())

    # Per http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part3.odt
    assert data[0:2] == b'PK'
    assert data[30:38] == b'mimetype'
    assert data[38:84] == b'application/vnd.oasis.opendocument.spreadsheet'
