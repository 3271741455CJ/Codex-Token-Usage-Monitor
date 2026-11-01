import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

HAS_EXPORTS=all(importlib.util.find_spec(x) for x in ('docx','openpyxl','PIL','reportlab'))

@unittest.skipUnless(HAS_EXPORTS,'local export dependencies unavailable')
class ExportTests(unittest.TestCase):
    def test_formats_are_readable_and_private_fields_removed(self):
        from codex_usage.exports import write_exports, FILES
        from docx import Document
        from openpyxl import load_workbook
        from PIL import Image
        import zipfile
        data={'generated_at':'2026-10-30T00:00:00Z','account':{'email':'SECRET@example.invalid'},
              'totals':{'total_tokens':120},'turns':[{'id':'SECRET','session_id':'SECRET','title':'SECRET',
              'model':'=HYPERLINK("https://example.invalid")','total_tokens':120}],
              'official_usage':{'status':'ok','summary':{'lifetimeTokens':900},'daily':[{'date':'2026-10-30','tokens':900}]}}
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp); write_exports(data,out)
            self.assertTrue(all((out/name).stat().st_size for name in FILES))
            for name in ('report.docx','records.xlsx'):
                with zipfile.ZipFile(out/name) as z:
                    self.assertNotIn(b'SECRET',b''.join(z.read(x) for x in z.namelist()))
            self.assertTrue(Document(out/'report.docx').tables)
            book=load_workbook(out/'records.xlsx'); sheet=book['轮次']
            self.assertFalse(any(c.data_type=='f' for row in sheet for c in row))
            self.assertIn(120,[c.value for row in sheet for c in row])
            for ext in ('png','jpg','webp'):
                with Image.open(out/('overview.'+ext)) as im: self.assertEqual(im.size,(1400,980)); im.verify()
            self.assertTrue((out/'report.pdf').read_bytes().startswith(b'%PDF'))

