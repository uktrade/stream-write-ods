# stream-write-ods

[![PyPI package](https://img.shields.io/pypi/v/stream-write-ods?label=PyPI%20package&color=%234c1)](https://pypi.org/project/stream-write-ods/) [![Test suite](https://img.shields.io/github/actions/workflow/status/uktrade/stream-write-ods/test.yml?label=Test%20suite)](https://github.com/uktrade/stream-write-ods/actions/workflows/test.yml) [![Code coverage](https://img.shields.io/codecov/c/github/uktrade/stream-write-ods?label=Code%20coverage)](https://app.codecov.io/gh/uktrade/stream-write-ods)

Python function to construct an ODS (OpenDocument Spreadsheet) on the fly - without having to store the entire file in memory or disk.

Can be used to convert CSV, SQLite, or JSON to ODS format.


## Installation

```bash
pip install stream-write-ods
```


## Usage

In general, pass a nested iterable to `stream_write_ods` and it will return an interable of bytes of the ODS file, as follows.

```python
from stream_write_ods import stream_write_ods

def get_sheets():
    def get_rows_of_sheet_1():
        yield 'Value A', 'Value B'
        yield 'Value C', 'Value D'

    yield 'Sheet 1 name', ('col_1_name', 'col_2_name'), get_rows_of_sheet_1()

    def get_rows_of_sheet_2():
        yield 'col_1_value',

    yield 'Sheet 2 name', ('col_1_name',), get_rows_of_sheet_2()

ods_chunks = stream_write_ods(get_sheets())
```


## Usage: Convert CSV file to ODS

The following recipe converts a local CSV file to ODS

```python
import csv
from stream_write_ods import stream_write_ods

def get_sheets(sheet_name, csv_reader):
    yield sheet_name, next(csv_reader), csv_reader

with open('my.csv', 'r', encoding='utf-8', newline='') as f:
    csv_reader = csv.reader(f, csv.QUOTE_NONNUMERIC)
    ods_chunks = stream_write_ods(get_sheets('Sheet 1', csv_reader))
```


## Usage: Convert CSV bytes to ODS

Using [to-file-like-obj](https://github.com/uktrade/to-file-like-obj), the following recipe converts an iterable yielding the bytes of a CSV to ODS.

```python
import csv
from io import IOBase, TextIOWrapper
from to_file_like_obj import to_file_like_obj
from stream_write_ods import stream_write_ods

# Any iterable that yields the bytes of a CSV file
# Hard coded for the purposes of this example
bytes_iter = (
    b'col_1,col_2\n',
    b'1,"value"\n',
)

def get_sheets(sheet_name, csv_reader):
    yield sheet_name, next(csv_reader), csv_reader

lines_iter = TextIOWrapper(to_file_like_obj(bytes_iter), , encoding='utf-8', newline='')
csv_reader = csv.reader(lines_iter, csv.QUOTE_NONNUMERIC)
ods_chunks = stream_write_ods(get_sheets('Sheet 1', csv_reader))
```


## Usage: Convert large/chunked pandas dataframe to ODS

```python
from io import BytesIO
from itertools import chain
import pandas as pd
from stream_write_ods import stream_write_ods

# Hard coded for the purposes of this example,
# but could be any file-like object
csv_file = BytesIO((
    b'col_1,col_2\n' +
    b'1,"value"\n'
    b'2,"other value"\n'
))

def get_sheets(reader):
    columns = None

    def get_rows():
        nonlocal columns

        for chunk in reader:
            if columns is None:
                columns = tuple(chunk.columns.tolist())
            yield from (row for index, row in chunk.iterrows())

    rows = get_rows()
    first_row = next(rows)

    yield 'Sheet 1', columns, chain((first_row,), rows)

# Directly saves the chunked dataframe as ODS for the purposes
# of this example, but could include calculations / manipulations
with pd.read_csv(csv_file, chunksize=1024) as reader:
    ods_chunks = stream_write_ods(get_sheets(reader))
```


## Usage: Convert JSON to ODS

Using [ijson](https://github.com/ICRAR/ijson) to stream-parse a JSON file and [to-file-like-obj](https://github.com/uktrade/to-file-like-obj) to convert an iterable of bytes to a file-like object, it's possible to convert JSON data to ODS on the fly.

```python
import ijson
import itertools
from to_file_like_obj import to_file_like_obj
from stream_write_ods import stream_write_ods

# Any iterable that yields the bytes of a JSON file
# Hard coded for the purposes of this example
json_bytes_iter = (b'''{
  "data": [
      {"id": 1, "name": "Foo"},
      {"id": 2, "name": "Bar"}
  ]
}''',)

def get_sheets(json_file):
    columns = None

    def rows():
        nonlocal columns
        for item in ijson.items(json_file, 'data.item'):
            if columns is None:
                columns = list(item.keys())
            yield tuple(item[column] for column in columns)

    # Ensure columns populated
    rows_it = rows()
    first_row = next(rows_it)

    yield 'Sheet 1', columns, itertools.chain((first_row,), rows_it)

json_file = to_file_like_obj(json_bytes_iter)  # ijson requires a file-like object
ods_chunks = stream_write_ods(get_sheets(json_file))
```


## Usage: Convert SQLite to ODS

SQLite isn't particularly streaming-friendly since typically you need random access to the file. But it's still possible to use stream-write-ods to convert SQLite to ODS.

```python
import contextlib
import sqlite3
import tempfile
from stream_write_ods import stream_write_ods

@contextlib.contextmanager
def get_db():
    # Hard coded in memory database for the purposes of this example
    with sqlite3.connect(':memory:') as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE my_table_a (my_col text);")
        cur.execute("CREATE TABLE my_table_b (my_col text);")
        cur.execute("INSERT INTO my_table_a VALUES ('Value A')")
        cur.execute("INSERT INTO my_table_b VALUES ('Value B')")
        yield con

def quote_identifier(value):
    return '"' + value.replace('"', '""') + '"'

def get_sheets(db):
    cur_table = db.cursor()
    cur_table.execute('''
        SELECT name FROM sqlite_master
        WHERE type = "table" AND name NOT LIKE 'sqlite\\_%' ESCAPE '\\'
    ''')
    cur_data = db.cursor()
    for table, in cur_table:
        cur_data.execute(f'SELECT * FROM {quote_identifier(table)} ORDER BY rowid')
        yield table, tuple(col[0] for col in cur_data.description), cur_data

with get_db() as db:
    ods_chunks = stream_write_ods(get_sheets(db))
```


## Types

There are [8 possible data types in an Open Document Spreadsheet](https://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#attribute-office_value-type): boolean, currency, date, float, percentage, string, time, and void. 4 of these can be output by stream-write-ods, chosen automatically according to the following table.

| Python type | ODS type                      |
|:------------|:------------------------------|
| boolean     | boolean                       |
| date        | date - without time component |
| datetime    | date - with time component    |
| int         | float                         |
| float       | float                         |
| str         | string                        |
| bytes       | string - base64 encoded       |
| NoneType    | no type - empty cell          |

It is possible to change how each type is encoded by overriding the `encoders` parameter of the `stream_write_ods` function. See [stream-write-ods.py](https://github.com/uktrade/stream-write-ods/blob/main/stream_write_ods.py) for the default implementation.


## Modified at

ODS files are ZIP files, and as such _require_ a "modified at" time for each member file. This defaults to `datetime.now()`, but can be overridden by the `get_modified_at` parameter of the `stream_write_ods` function. See [stream-write-ods.py](https://github.com/uktrade/stream-write-ods/blob/main/stream_write_ods.py) for the default implementation.

This is useful if you want to make sure generated ODS files are byte-for-byte identical to a fixed reference, say from automated tests.


## Large ODS files

ODS spreadsheets are essentially ZIP archives containing several member files. By default, stream-write-ods creates ZIP files that are limited to 4GiB (gibibyte) of data for compatibility reasons, for example to support older versions of LibreOffice. If you attempt to store more than this limit a ZipOverflow exception will be raised.
 
To avoid this exception and to store more data, you can pass `use_zip_64=True` as an argument to stream-write-ods. This results in a more recent ZIP format used that allows 16 EiB (exbibyte) of data to be stored, but with the downside that older versions of LibreOffice will not be able to open the resulting ODS file.
