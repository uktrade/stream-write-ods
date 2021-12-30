# stream-write-ods [![CircleCI](https://circleci.com/gh/uktrade/stream-write-ods.svg?style=shield)](https://circleci.com/gh/uktrade/stream-write-ods) [![Test Coverage](https://api.codeclimate.com/v1/badges/1a894f9bd9860544b409/test_coverage)](https://codeclimate.com/github/uktrade/stream-write-ods/test_coverage)

Python function to construct an ODS spreadsheet on the fly - without having to store the entire file in memory or disk

> Work in progress. This README serves as a rough design spec.


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

    yield 'Sheet 1 name', ('col_1_name', 'col_2_name') get_rows_of_sheet_1()

    def get_rows_of_sheet_2():
        yield 'col_1_value',

    yield 'Sheet 2 name', (('col_1_name')), get_rows_of_sheet_2()

ods_chunks = stream_write_ods(get_sheets())
```


## Types

There are [8 possible data types in an Open Document Spreadsheet](https://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#attribute-office_value-type): boolean, currency, date, float, percentage, string, time and void. 5 of these can be output by stream-write-ods, chosen automatically according to the below table

| Python type | ODS type |
|-------------|----------|
| boolean     | boolean  |
| date        | date     |
| datetime    | date     |
| int         | float    |
| float       | float    |
| str         | string   |
| NoneType    | void     |
