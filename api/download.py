import yt_dlp
import os
import uuid
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        url = data.get("url")
        if not url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"No URL"}')
            return

        unique_id = str(uuid.uuid4())
        output_path = f"/tmp/{unique_id}.mp4"

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_path,
            'quiet': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()

            with open(output_path, "rb") as f:
                self.wfile.write(f.read())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
