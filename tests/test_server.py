import http.client
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from codex_usage.server import make_server

class ServerTests(unittest.TestCase):
    def test_origin_host_routes_and_failure_keep_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); calls=[]
            def collect(home,out,official):
                calls.append(1)
                if len(calls)==3: raise RuntimeError('PRIVATE exception')
                folder=root/str(len(calls)); folder.mkdir()
                (folder/'usage.json').write_text(str(len(calls)))
                from codex_usage.report import render_html
                (folder/'latest.html').write_text(render_html({}),encoding='utf-8')
                return folder
            server=make_server(root,root/'output',collector=collect)
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            parsed=urlsplit(server.local_url); base=parsed.path
            def request(method,path,headers=None):
                con=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=5)
                con.request(method,path,headers=headers or {}); response=con.getresponse()
                result=response.status,response.read(); con.close(); return result
            try:
                self.assertEqual(request('GET',base+'usage.json'),(200,b'1'))
                import re,hashlib,base64
                status,body=request('GET',base+'latest.html')
                self.assertEqual(status,200)
                html=body.decode().replace('\r\n','\n')
                self.assertIn("connect-src 'self'",html)
                for script in re.findall(r'<script[^>]*>(.*?)</script>',html,re.S):
                    digest=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
                    self.assertIn(digest,html)
                self.assertEqual(request('GET','/usage.json')[0],403)
                self.assertEqual(request('GET',base+'../auth.json')[0],404)
                self.assertEqual(request('GET',base+'usage.json',{'Host':'evil.invalid'})[0],403)
                self.assertEqual(request('POST',base+'refresh',{'Origin':'https://evil.invalid'})[0],403)
                headers={'Origin':f'http://127.0.0.1:{server.server_port}','X-Codex-Refresh':'1'}
                self.assertEqual(request('POST',base+'refresh',headers)[0],200)
                self.assertEqual(request('GET',base+'usage.json'),(200,b'2'))
                status,body=request('POST',base+'refresh',headers)
                self.assertEqual(status,500); self.assertNotIn(b'PRIVATE',body)
                self.assertEqual(request('GET',base+'usage.json'),(200,b'2'))
            finally: server.shutdown(); server.server_close(); thread.join()
