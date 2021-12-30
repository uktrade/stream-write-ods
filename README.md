# stream-write-ods [![CircleCI](https://circleci.com/gh/uktrade/stream-write-ods.svg?style=shield)](https://circleci.com/gh/uktrade/stream-write-ods) [![Test Coverage](https://api.codeclimate.com/v1/badges/1a894f9bd9860544b409/test_coverage)](https://codeclimate.com/github/uktrade/stream-write-ods/test_coverage)

Python function to construct an ODS spreadsheet on the fly - without having to store the entire file in memory or disk


## Installation

```bash
pip install stream-write-ods
```


## Usage

```python
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
| NoneType    | string - as #NA               |


## Limitations

ODS spreadsheets are essentially ZIP files containing several member files. While in general ZIP files can be up to 16EiB (exbibyte) in size using [ZIP64](https://en.wikipedia.org/wiki/ZIP_(file_format)#ZIP64), [LibreOffice does not support ZIP64](https://bugs.documentfoundation.org/show_bug.cgi?id=128244), and so ODS files are de-facto limited to 4GiB (gibibyte). These limits apply to the size of the entire compressed archive, the compressed size of each member file, and uncompressed size of each member file.
