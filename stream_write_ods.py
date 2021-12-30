from datetime import datetime
from stream_zip import stream_zip


def stream_write_ods():
    modified_at = datetime.now()
    perms = 0o600

    manifest = \
        '<?xml version="1.0" encoding="UTF-8"?>' \
        '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">' \
            '<manifest:file-entry manifest:full-path="/" manifest:version="1.2" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>' \
            '<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>' \
        '</manifest:manifest>'
    mimetype = \
        'application/vnd.oasis.opendocument.spreadsheet'
    content = \
        '<?xml version="1.0" encoding="UTF-8"?>' \
        '<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.2">' \
            '<office:body>' \
                '<office:spreadsheet>' \
                    '<table:table table:name="Sheet1">' \
                        '<table:table-row>' \
                            '<table:table-cell office:value-type="string"><text:p>Col 1</text:p></table:table-cell>' \
                            '<table:table-cell office:value-type="string"><text:p>Col 2</text:p></table:table-cell>' \
                        '</table:table-row>' \
                    '</table:table>' \
                '</office:spreadsheet>' \
            '</office:body>' \
        '</office:document-content>'

    def files():
        yield 'META-INF/manifest.xml', modified_at, perms, (manifest.encode(),)
        yield 'mimetype', modified_at, perms, (mimetype.encode(),)
        yield 'content.xml', modified_at, perms, (content.encode(),)

    yield from stream_zip(files())
