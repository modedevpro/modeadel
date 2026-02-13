from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route("/download")
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    if not os.path.exists("cookies.txt"):
        return jsonify({"error": "cookies.txt not found"}), 500

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': '18/22/best',
        'cookiefile': 'cookies.txt',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return jsonify({
                "title": info.get("title"),
                "download_url": info.get("url")
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
