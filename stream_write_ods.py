from datetime import datetime
from stream_zip import ZIP, NO_COMPRESSION, stream_zip


def stream_write_ods():
    modified_at = datetime.now()
    perms = 0o600

    mimetype = \
        'application/vnd.oasis.opendocument.spreadsheet'
    manifest = \
        '<?xml version="1.0" encoding="UTF-8"?>' \
        '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">' \
            '<manifest:file-entry manifest:full-path="/" manifest:version="1.2" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>' \
            '<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>' \
        '</manifest:manifest>'
    content = \
        '<?xml version="1.0" encoding="UTF-8"?>' \
        '<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.2">' \
            '<office:body>' \
                '<office:spreadsheet>' \
                    '<table:table table:name="Sheet 1">' \
                        '<table:table-column table:number-columns-repeated="2"/>' \
                        '<table:table-row>' \
                            '<table:table-cell office:value-type="string"><text:p>Col 1</text:p></table:table-cell>' \
                            '<table:table-cell office:value-type="string"><text:p>Col 2</text:p></table:table-cell>' \
                        '</table:table-row>' \
                        '<table:table-row>' \
                            '<table:table-cell office:value-type="string"><text:p>Value 1</text:p></table:table-cell>' \
                            '<table:table-cell office:value-type="string"><text:p>Value 2</text:p></table:table-cell>' \
                        '</table:table-row>' \
                    '</table:table>' \
                '</office:spreadsheet>' \
            '</office:body>' \
        '</office:document-content>'

    def files():
        # To validate, mimetype must be first
        yield 'mimetype', modified_at, perms, NO_COMPRESSION, (mimetype.encode(),)
        yield 'META-INF/manifest.xml', modified_at, perms, ZIP, (manifest.encode(),)
        yield 'content.xml', modified_at, perms, ZIP, (content.encode(),)

    yield from stream_zip(files())
