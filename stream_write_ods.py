from base64 import b64encode
from codecs import iterencode
from datetime import datetime, date
from xml.sax.saxutils import escape, quoteattr

from stream_zip import ZIP_32, NO_COMPRESSION_32, stream_zip


def stream_write_ods(sheets, chunk_size=65536):

    def files():
        modified_at = datetime.now()
        perms = 0o600
        to_cell = {
            type(False): lambda v: f'<table:table-cell office:value-type="boolean" office:boolean-value={quoteattr(str(v).lower())}><text:p>{escape(str(v).lower())}</text:p></table:table-cell>',
            type(date(1970, 1, 1)): lambda v: f'<table:table-cell office:value-type="date" office:date-value={quoteattr(v.isoformat())}><text:p>{escape(quoteattr(v.isoformat()))}</text:p></table:table-cell>',
            type(datetime(1970, 1, 1, 0, 0)): lambda v: f'<table:table-cell office:value-type="date" office:date-value={quoteattr(v.isoformat())}><text:p>{escape(quoteattr(v.isoformat()))}</text:p></table:table-cell>',
            type(0): lambda v: f'<table:table-cell office:value-type="float" office:value={quoteattr(str(v))}><text:p>{escape(str(v))}</text:p></table:table-cell>',
            type(0.0): lambda v: f'<table:table-cell office:value-type="float" office:value={quoteattr(str(v))}><text:p>{escape(str(v))}</text:p></table:table-cell>',
            type(''): lambda v: f'<table:table-cell office:value-type="string"><text:p>{escape(v)}</text:p></table:table-cell>',
            type(b''): lambda v: f'<table:table-cell office:value-type="string"><text:p>{escape(b64encode(v).decode())}</text:p></table:table-cell>',
            type(None): lambda v: f'<table:table-cell office:value-type="string"><text:p>#N/A</text:p></table:table-cell>',
        }

        # To validate, mimetype must be first
        yield 'mimetype', modified_at, perms, NO_COMPRESSION_32, (
            b'application/vnd.oasis.opendocument.spreadsheet',
        )

        yield 'META-INF/manifest.xml', modified_at, perms, ZIP_32, (
            b'<?xml version="1.0" encoding="UTF-8"?>' \
            b'<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">' \
                b'<manifest:file-entry manifest:full-path="/" manifest:version="1.2" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>' \
                b'<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>' \
            b'</manifest:manifest>',
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
                        yield to_cell[type(value)](value)
                    yield '</table:table-row>'
                yield '</table:table>'
            yield '</office:spreadsheet>'
            yield '</office:body>'
            yield '</office:document-content>'

        yield 'content.xml', modified_at, perms, ZIP_32, iterencode(content_xml(), 'utf-8')

    yield from stream_zip(files(), chunk_size=chunk_size)
