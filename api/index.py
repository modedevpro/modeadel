# Developer: محمود عادل الغريب

from flask import Flask, request, Response
import requests
import base64
import urllib.parse

app = Flask(__name__)

def deco(text):
    decoded = urllib.parse.unquote(text)
    try:
        if base64.b64encode(base64.b64decode(decoded)).decode() == decoded:
            return base64.b64decode(decoded).decode()
    except:
        pass
    return decoded

def google_translate(text, target_lang="en"):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        translated_text = "".join([item[0] for item in result[0]])
        return translated_text
    except:
        return text

@app.route("/")
def generate():
    text = request.args.get("text")

    if not text:
        return "No text provided", 400

    try:
        text = deco(text)
        translated = google_translate(text, "en")

        url = "https://api.websim.com/api/v1/inference/run_image_generation"

        payload = {
            "project_id": "hcrvyemb62atnf29vvhr",
            "prompt": translated,
            "aspect_ratio": "1:1"
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=8)

        try:
            data = response.json()
        except:
            return "Invalid API response", 500

        if "url" in data:
            image_response = requests.get(data["url"], timeout=8)
            return Response(image_response.content, content_type="image/jpeg")

        return "No image returned"

    except Exception as e:
        return f"Server Error: {str(e)}", 500
