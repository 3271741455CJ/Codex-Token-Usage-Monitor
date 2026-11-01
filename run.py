#!/usr/bin/env python3
"""Guarded collection, optional local exports and loopback-only live reports."""
import sys
sys.dont_write_bytecode = True
import argparse
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from codex_usage.safety import checked_local_path, install_guard, validate_output


def main():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'): stream.reconfigure(encoding='utf-8',errors='replace')
    if sys.version_info < (3, 11):
        print('需要本机 Python 3.11 或以上版本；本程序不会下载安装任何依赖。',file=sys.stderr)
        return 1
    parser=argparse.ArgumentParser(description='Codex 用量查看器（源文件只读、默认离线、Python 3.11+）')
    parser.add_argument('--codex-home',help='Codex 数据目录；默认 CODEX_HOME 或 ~/.codex')
    parser.add_argument('--output',default=str(Path(__file__).parent/'.reports'),help='独立报告输出目录')
    parser.add_argument('--json',action='store_true',help='额外生成去标识的 usage.json；仅供本地使用')
    parser.add_argument('--all-formats',action='store_true',help='生成 Word、Excel、PDF 和 PNG/JPEG/WebP/SVG 概览；需要本机导出依赖')
    parser.add_argument('--serve',action='store_true',help='打开仅本机可访问的交互报告，支持更新整套文件')
    parser.add_argument('--sync-official',action='store_true',help='显式通过已安装官方客户端同步账号用量与额度；需要联网，不上传本地日志')
    parser.add_argument('--show-api-key',action='store_true',help='仅显示本地查看指引，不再输出 API Key 或其片段')
    args=parser.parse_args()
    if args.sync_official and args.show_api_key:
        parser.error('--sync-official 不能与 --show-api-key 同时使用。')
    try:
        home=checked_local_path(args.codex_home or os.environ.get('CODEX_HOME') or Path.home()/'.codex')
        protected=[Path.home()/'.codex']
        if os.name=='nt':
            protected += [Path(os.environ.get('LOCALAPPDATA',Path.home()))/'OpenAI'/'Codex',Path(os.environ.get('ProgramFiles','C:/Program Files'))/'WindowsApps']
        output=validate_output(Path(args.output),home,protected)
        if not home.is_dir(): raise ValueError('Codex 数据目录不存在；请用 --codex-home 指定本地目录。')
        if args.show_api_key and (args.serve or args.all_formats):
            raise ValueError('查看指引不能与服务模式组合。')
        if args.serve:
            from codex_usage.server import serve
            serve(home,output,args.sync_official)
            return 0
        if args.all_formats:
            # Preload libraries before the audit hook; no automatic downloads.
            import docx, openpyxl, PIL.Image, PIL.ImageFont, reportlab.pdfgen.canvas
            import tempfile
            output.mkdir(exist_ok=True)
            tempfile.tempdir=str(output)
        # No write is possible until the boundary is installed.
        from codex_usage.official import make_launch, fetch_official, unavailable, SyncError
        plan = None
        sync_status = 'offline'
        if args.sync_official:
            try:
                plan = make_launch(output)
            except (OSError, ValueError, SyncError):
                sync_status = 'client_unavailable'
        launch = install_guard(output, official_launch=plan)
        if args.show_api_key:
            from codex_usage.privacy import LOCAL_GUIDE, GUIDES
            print(GUIDES['auth'] + GUIDES['config'] + LOCAL_GUIDE)
            return 0
        output.mkdir(exist_ok=True)
        print('正在只读扫描本机文件；' + ('将尝试官方账号用量同步。' if args.sync_official else '网络和子进程已禁止。'),flush=True)
        from codex_usage.report import build_report,write_report
        reader = (lambda account: fetch_official(home, output, plan, launch, expected_account=account.get('account_id'))) if plan else (lambda account: unavailable(sync_status))
        report=build_report(home,output,official_reader=reader)
        if args.all_formats:
            from codex_usage.exports import FILES
            report['export_formats']=list(FILES)
        path=write_report(report,output,export_json=args.json)
        if args.all_formats:
            from codex_usage.exports import write_exports
            write_exports(report,output)
        print('完成。请在所选输出目录打开 latest.html；默认输出目录是项目内的 .reports。')
        print('报告仅供本机使用；敏感原文请按页面指引自行查看本地源文件。')
        return 0
    except Exception as exc:
        print(f'无法生成报告（{type(exc).__name__}）。请在本机检查目录、文件及权限；错误原文不输出。',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
