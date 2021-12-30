from datetime import datetime
from stream_zip import ZIP, NO_COMPRESSION, stream_zip


def stream_write_ods():

    def files():
        modified_at = datetime.now()
        perms = 0o600

        # To validate, mimetype must be first
        yield 'mimetype', modified_at, perms, NO_COMPRESSION, (
            b'application/vnd.oasis.opendocument.spreadsheet',
        )

        yield 'META-INF/manifest.xml', modified_at, perms, ZIP, (
            b'<?xml version="1.0" encoding="UTF-8"?>' \
            b'<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">' \
                b'<manifest:file-entry manifest:full-path="/" manifest:version="1.2" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>' \
                b'<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>' \
            b'</manifest:manifest>',
        )

        def content_xml():
            yield b'<?xml version="1.0" encoding="UTF-8"?>'
            yield b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.2">'
            yield b'<office:body>'
            yield b'<office:spreadsheet>'
            yield b'<table:table table:name="Sheet 1">'
            yield b'<table:table-column table:number-columns-repeated="2"/>'
            yield b'<table:table-header-rows>'
            yield b'<table:table-row>'
            yield b'<table:table-cell office:value-type="string"><text:p>Col 1</text:p></table:table-cell>'
            yield b'<table:table-cell office:value-type="string"><text:p>Col 2</text:p></table:table-cell>'
            yield b'</table:table-row>'
            yield b'</table:table-header-rows>'
            yield b'<table:table-row>'
            yield b'<table:table-cell office:value-type="string"><text:p>Value 1</text:p></table:table-cell>'
            yield b'<table:table-cell office:value-type="string"><text:p>Value 2</text:p></table:table-cell>'
            yield b'</table:table-row>'
            yield b'</table:table>'
            yield b'</office:spreadsheet>'
            yield b'</office:body>'
            yield b'</office:document-content>'

        yield 'content.xml', modified_at, perms, ZIP, content_xml()

    yield from stream_zip(files())
