#!/usr/bin/env python3
"""Serve the generated questionnaire locally so answers.json is saved beside it.

Run this while the user fills out the questionnaire, then open the printed URL in a
browser. When the user clicks "save" in the page, the answers are POSTed here and
written to answers.json in the same directory as questionnaire.html.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HTML_NAME = "questionnaire.html"
ANSWERS_NAME = "answers.json"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # keep console quiet
        pass

    def _send(self, code: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/" + HTML_NAME):
            body = self.server.html_path.read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif self.path == "/health":
            self._send(200, b'{"ok": true}')
        else:
            self._send(404, b'{"error": "not found"}')

    def do_POST(self) -> None:
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send(400, b'{"error": "invalid JSON"}')
                return
            out = self.server.directory / ANSWERS_NAME
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self._send(200, json.dumps({"ok": True, "path": str(out)}).encode("utf-8"))
        elif self.path == "/shutdown":
            self._send(200, b'{"ok": true}')
            threading.Timer(0.2, self.server.shutdown).start()
        else:
            self._send(404, b'{"error": "not found"}')


class Server(ThreadingHTTPServer):
    def __init__(self, address: tuple, directory: Path, html_path: Path) -> None:
        self.directory = directory
        self.html_path = html_path
        super().__init__(address, Handler)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="本地提供问卷页面，并把答案保存到问卷同目录。")
    parser.add_argument("--directory", default=".", help="问卷所在目录（默认当前目录）")
    parser.add_argument("--port", type=int, default=8765, help="监听端口（默认 8765）")
    parser.add_argument("--pid-file", help="可选：把进程 PID 写入该文件，便于之后停止服务")
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    html_path = directory / HTML_NAME
    if not html_path.exists():
        sys.exit(f"未找到 {html_path}")

    if args.pid_file:
        pid_file = Path(args.pid_file)
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()), encoding="utf-8")

    server = Server(("127.0.0.1", args.port), directory, html_path)
    print(f"问卷地址: http://127.0.0.1:{args.port}/{HTML_NAME}")
    print(f"答案将保存到: {directory / ANSWERS_NAME}")
    print("按 Ctrl+C 停止服务。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
