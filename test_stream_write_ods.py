from datetime import date, datetime
from collections import OrderedDict
from tempfile import NamedTemporaryFile
from pandas_ods_reader import read_ods
from stream_write_ods import stream_write_ods


def get_sheets():
    def get_sheet_1_rows():
        yield 'Row 1 Column 1 <&>', 'Row 1 Column 2 <&>'
        yield 'Row 2 Column 1 <&>', 'Row 2 Column 2 <&>'

    yield 'Sheet 1 <&> \'""', ('Column 1 <&>', 'Column 2 <&>'), get_sheet_1_rows()

    def get_sheet_2_rows():
        yield 'Row 1 Column 1',
        yield datetime(2021,1,1,10,1,4),
        yield date(2021,1,1),
        yield 2,
        yield 3.4,
        yield True,
        yield b'Binary data',
        yield None,
        yield '<![CDATA[',

    yield 'Sheet 2', ('Column 1',), get_sheet_2_rows()


def test_openable_with_pandas():
    with NamedTemporaryFile() as f:
        f.write(b''.join(stream_write_ods(get_sheets())))
        f.flush()
        sheet_1 = read_ods(f.name, 'Sheet 1 <&> \'""')
        sheet_1_rows = sheet_1.values.tolist()
        sheet_1_cols =  sheet_1.columns.tolist()
        sheet_2 = read_ods(f.name, "Sheet 2")
        sheet_2_rows = sheet_2.values.tolist()
        sheet_2_cols =  sheet_2.columns.tolist()

    assert sheet_1_rows == [
        ['Row 1 Column 1 <&>', 'Row 1 Column 2 <&>'],
        ['Row 2 Column 1 <&>', 'Row 2 Column 2 <&>'],
    ]
    assert sheet_1_cols == ['Column 1 <&>', 'Column 2 <&>']
    assert sheet_2_rows == [
        ['Row 1 Column 1',],
        ['2021-01-01T10:01:04',],
        ['2021-01-01',],
        [2.0,],
        [3.4,],
        [True,],
        ['QmluYXJ5IGRhdGE=',],
        [None,],
        ['<![CDATA[',]
    ]
    assert sheet_2_cols == ['Column 1',]


def test_openable_with_pandas_zip_64():
    with NamedTemporaryFile() as f:
        f.write(b''.join(stream_write_ods(get_sheets(), use_zip_64=True)))
        f.flush()
        sheet_1 = read_ods(f.name, 'Sheet 1 <&> \'""')
        sheet_1_rows = sheet_1.values.tolist()
        sheet_1_cols =  sheet_1.columns.tolist()
        sheet_2 = read_ods(f.name, "Sheet 2")
        sheet_2_rows = sheet_2.values.tolist()
        sheet_2_cols =  sheet_2.columns.tolist()

    assert sheet_1_rows == [
        ['Row 1 Column 1 <&>', 'Row 1 Column 2 <&>'],
        ['Row 2 Column 1 <&>', 'Row 2 Column 2 <&>'],
    ]
    assert sheet_1_cols == ['Column 1 <&>', 'Column 2 <&>']
    assert sheet_2_rows == [
        ['Row 1 Column 1',],
        ['2021-01-01T10:01:04',],
        ['2021-01-01',],
        [2.0,],
        [3.4,],
        [True,],
        ['QmluYXJ5IGRhdGE=',],
        [None,],
        ['<![CDATA[',]
    ]
    assert sheet_2_cols == ['Column 1',]


def test_has_correct_magic_values():
    data = b''.join(stream_write_ods(get_sheets()))

    # Per http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part3.odt
    assert data[0:2] == b'PK'
    assert data[30:38] == b'mimetype'
    assert data[38:84] == b'application/vnd.oasis.opendocument.spreadsheet'


def test_has_correct_magic_values_zip_64():
    data = b''.join(stream_write_ods(get_sheets(), use_zip_64=True))

    assert data[0:2] == b'PK'
    assert data[30:38] == b'mimetype'
    assert data[38:84] == b'application/vnd.oasis.opendocument.spreadsheet'
