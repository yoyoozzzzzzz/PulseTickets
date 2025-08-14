from flask import Flask, request, jsonify
import requests
import base64
import os
from datetime import datetime

app = Flask(__name__)

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

@app.route('/', methods=['GET'])
def home():
    return "Transcript GitHub Uploader is running!"

@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    file = request.files.get('file')
    if not file:
        return jsonify({"success": False, "error": "No file provided"}), 400

    filename = file.filename
    file_content = file.read()
    b64_content = base64.b64encode(file_content).decode('utf-8')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    commit_msg = f"Add transcript {filename} ({now})"

    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/transcripts/{filename}"

    payload = {
        "message": commit_msg,
        "content": b64_content,
        "branch": GITHUB_BRANCH
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    resp = requests.put(api_url, json=payload, headers=headers)
    if resp.status_code in (201, 200):
        content = resp.json()["content"]
        html_url = content["html_url"]  # blob in repo
        raw_url = content["download_url"]  # direct raw file URL
        return jsonify({"success": True, "url": raw_url, "html_url": html_url})
    else:
        try:
            error_detail = resp.json()
        except Exception:
            error_detail = resp.text
        return jsonify({"success": False, "error": error_detail}), resp.status_code

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
