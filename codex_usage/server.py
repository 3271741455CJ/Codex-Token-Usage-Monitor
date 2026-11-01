"""Loopback-only UI. Collection runs in a fresh guarded worker per refresh."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import mimetypes
import os
import secrets
import subprocess
import sys
import uuid
from .exports import FILES
from .safety import checked_local_path
from .runtime import collector_command

ALLOWED = {'latest.html', 'usage.json', *FILES}

def collect(home, output, official=False):
    folder=checked_local_path(output/('snapshot-'+uuid.uuid4().hex))
    folder.mkdir()
    command=collector_command(home,folder,official)
    result=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,timeout=300,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode or not all((folder/name).is_file() for name in ALLOWED):
        raise RuntimeError('report generation failed')
    return folder

def make_server(home, output, official=False, collector=collect):
    output.mkdir(exist_ok=True)
    current=collector(home,output,official)
    token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def handle(self):
            self.connection.settimeout(15)
            super().handle()
        def reply(self,code,body=b'',mime='text/plain; charset=utf-8',download=None):
            self.send_response(code); self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Referrer-Policy','no-referrer')
            if download: self.send_header('Content-Disposition','attachment; filename="'+download+'"')
            self.end_headers(); self.wfile.write(body)
        def authorized(self):
            return (self.headers.get('Host')==f'127.0.0.1:{self.server.server_port}'
                    and self.path.startswith('/'+token+'/'))
        def do_GET(self):
            if not self.authorized(): return self.reply(403)
            if self.headers.get('Origin') not in (None,f'http://127.0.0.1:{self.server.server_port}'):
                return self.reply(403)
            name=self.path[len(token)+2:] or 'latest.html'
            if name not in ALLOWED: return self.reply(404)
            try:
                body=checked_local_path(current/name).read_bytes()
                if name=='latest.html':
                    # The live script is fixed code and CSP-authorized separately.
                    import base64,hashlib
                    script=Path(__file__).with_name('live.js').read_text(encoding='utf-8')
                    digest=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
                    html=body.decode().replace("connect-src 'none'","connect-src 'self'",1)
                    html=html.replace('script-src ',"script-src 'sha256-"+digest+"' ",1)
                    body=html.replace('</body>','<script>'+script+'</script></body>').encode()
                self.reply(200,body,mimetypes.guess_type(name)[0] or 'application/octet-stream',name if name!='latest.html' else None)
            except Exception: self.reply(500,b'Local file unavailable')
        def do_POST(self):
            nonlocal current
            origin=f'http://127.0.0.1:{self.server.server_port}'
            if (not self.authorized() or self.path!='/'+token+'/refresh'
                or self.headers.get('Origin')!=origin or self.headers.get('X-Codex-Refresh')!='1'
                or self.headers.get('Content-Length','0')!='0'):
                return self.reply(403)
            try:
                candidate=collector(home,output,official)
                current=candidate  # Publish only a complete generation.
                self.reply(200,b'{"ok":true}','application/json')
            except Exception: self.reply(500,b'{"ok":false}','application/json')
    class LocalServer(HTTPServer):
        def handle_error(self,request,client_address):
            pass  # Never print request URLs, paths or raw exceptions.
    server=LocalServer(('127.0.0.1',0),Handler)
    server.local_url=f'http://127.0.0.1:{server.server_port}/{token}/'
    return server

def serve(home, output, official=False):
    server=make_server(home,output,official)
    import webbrowser
    webbrowser.open(server.local_url)
    print('本机交互报告已启动；关闭此窗口将停止页面更新。')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
