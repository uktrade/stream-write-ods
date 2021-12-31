# stream-write-ods [![CircleCI](https://circleci.com/gh/uktrade/stream-write-ods.svg?style=shield)](https://circleci.com/gh/uktrade/stream-write-ods) [![Test Coverage](https://api.codeclimate.com/v1/badges/1a894f9bd9860544b409/test_coverage)](https://codeclimate.com/github/uktrade/stream-write-ods/test_coverage)

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


## Usage: Convert CSV to ODS

The following recipe converts a CSV to ODS.

```python
import codecs
import csv
from stream_write_ods import stream_write_ods

# Any iterable that yields the bytes of a CSV file
# Hard coded for the purposes of this example
csv_bytes_iter = (
    b'col_1,col_2\n',
    b'1,"value"\n',
)

def get_sheets(sheet_name, csv_reader):
    yield sheet_name, next(csv_reader), csv_reader

csv_str_iter = codecs.iterdecode(csv_bytes_iter, 'utf-8')
csv_reader = csv.reader(csv_str_iter, csv.QUOTE_NONNUMERIC)
ods_chunks = stream_write_ods(get_sheets('Sheet 1', csv_reader))
```


## Usage: Convert JSON to ODS

Using [ijson](https://github.com/ICRAR/ijson) to stream-parse a JSON file, it's possible to convert JSON data to ODS on the fly:

```python
import ijson
import itertools
from stream_write_ods import stream_write_ods

# Any iterable that yields the bytes of a JSON file
# Hard coded for the purposes of this example
json_bytes_iter = (b'''{
  "data": [
      {"id": 1, "name": "Foo"},
      {"id": 2, "name": "Bar"}
  ]
}''',)

# ijson requires a file-like object
def to_file_like_obj(bytes_iter):
    chunk = b''
    offset = 0
    it = iter(bytes_iter)

    def up_to_iter(num):
        nonlocal chunk, offset

        while num:
            if offset == len(chunk):
                try:
                    chunk = next(it)
                except StopIteration:
                    break
                else:
                    offset = 0
            to_yield = min(num, len(chunk) - offset)
            offset = offset + to_yield
            num -= to_yield
            yield chunk[offset - to_yield:offset]

    class FileLikeObj:
        def read(self, n):
            return b''.join(up_to_iter(n))

    return FileLikeObj()

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

json_file = to_file_like_obj(json_bytes_iter)
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
| NoneType    | string - as #NA               |


## Limitations

ODS spreadsheets are essentially ZIP archives containing several member files. While in general ZIP archives can be up to 16EiB (exbibyte) in size using [ZIP64](https://en.wikipedia.org/wiki/ZIP_(file_format)#ZIP64), [LibreOffice does not support ZIP64](https://bugs.documentfoundation.org/show_bug.cgi?id=128244), and so ODS files are de-facto limited to 4GiB (gibibyte). This limit applies to the size of the entire compressed archive, the compressed size of each member file, and the uncompressed size of each member file.
