#!/usr/bin/env python3
"""Standalone app entry. A double-click starts the local interactive report."""
import sys
sys.dont_write_bytecode = True
from run import main


if __name__ == '__main__':
    args = sys.argv[1:]
    worker = bool(args and args[0] == '--worker')
    if worker:
        args = [*args[1:], '--no-update-check']
    code = main(args if args else ['--serve'])
    if code and not worker:
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk(); root.withdraw()
            messagebox.showerror('Codex 用量查看器',
                '无法生成报告。请确认本机已有 Codex 数据，或使用 --codex-home 指定本地数据目录。', parent=root)
            root.destroy()
        except Exception:
            pass
    raise SystemExit(code)
