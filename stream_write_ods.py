from base64 import b64encode
from codecs import iterencode
from datetime import datetime, date
from xml.sax.saxutils import escape, quoteattr

from stream_zip import ZIP_32, NO_COMPRESSION_32, stream_zip


def stream_write_ods(sheets, encoders=(
    (type(False), ('boolean', 'office:boolean-value', None, lambda v: str(v).lower())),
    (type(date(1970, 1, 1)), ('date', 'office:date-value', 'date', lambda v: v.isoformat())),
    (type(datetime(1970, 1, 1, 0, 0)), ('date', 'office:date-value', None, lambda v: v.isoformat())),
    (type(0), ('float', 'office:value', None, str)),
    (type(0.0), ('float', 'office:value', None, str)),
    (type(''), ('string', None, None, str)),
    (type(b''), ('string', None, None, lambda v: b64encode(v).decode())),
    (type(None), (None, None, None, lambda _: None)),
), get_modified_at=lambda: datetime.now(), chunk_size=65536):
    encoders = dict(encoders)
    modified_at = get_modified_at()
    perms = 0o600

    def files():
        yield 'mimetype', modified_at, perms, NO_COMPRESSION_32, (
            b'application/vnd.oasis.opendocument.spreadsheet',
        )

        yield 'META-INF/manifest.xml', modified_at, perms, ZIP_32, (
            b'<?xml version="1.0" encoding="UTF-8"?>' \
            b'<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">' \
                b'<manifest:file-entry manifest:full-path="/" manifest:version="1.2" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>' \
                b'<manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>' \
                b'<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>' \
            b'</manifest:manifest>',
        )

        yield 'styles.xml', modified_at, perms, ZIP_32, (
            b'<?xml version="1.0" encoding="UTF-8"?><office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" office:version="1.2">'
            b'<office:styles>'
            b'<number:date-style style:name="data-date">'
            b'<number:year number:style="long"/>'
            b'<number:text>-</number:text>'
            b'<number:month number:style="long"/>'
            b'<number:text>-</number:text>'
            b'<number:day number:style="long"/>'
            b'</number:date-style>'
            b'<style:style style:name="date" style:family="table-cell" style:data-style-name="data-date"/>'
            b'</office:styles>'
            b'</office:document-styles>',
        )

        def content_xml():
            yield '<?xml version="1.0" encoding="UTF-8"?>'
            yield '<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.2">'
            yield '<office:body>'
            yield '<office:spreadsheet>'
            for name, columns, rows in sheets:
                yield f'<table:table table:name={quoteattr(name)}>'
                yield f'<table:table-column table:number-columns-repeated={quoteattr(str(len(columns)))}/>'
                yield '<table:table-header-rows>'
                yield '<table:table-row>'
                for column in columns:
                    yield f'<table:table-cell office:value-type="string"><text:p>{escape(column)}</text:p></table:table-cell>'
                yield '</table:table-row>'
                yield '</table:table-header-rows>'
                for row in rows:
                    yield '<table:table-row>'
                    for value in row:
                        value_type, value_attr, style_name, encoder = encoders[type(value)]
                        encoded = encoder(value)
                        yield '<table:table-cell'
                        if value_type is None:
                            yield '/>'
                        else:
                            yield f' office:value-type="{value_type}"'
                            if value_attr is not None:
                                yield f' {value_attr}={quoteattr(encoded)}'
                            if style_name is not None:
                                yield f' table:style-name={quoteattr(style_name)}'
                            yield f'><text:p>{escape(encoded)}</text:p>'
                            yield '</table:table-cell>'
                    yield '</table:table-row>'
                yield '</table:table>'
            yield '</office:spreadsheet>'
            yield '</office:body>'
            yield '</office:document-content>'

        yield 'content.xml', modified_at, perms, ZIP_32, iterencode(content_xml(), 'utf-8')

    yield from stream_zip(files(), chunk_size=chunk_size)
