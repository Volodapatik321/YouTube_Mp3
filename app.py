from flask import Flask, request, send_file, render_template_string, abort
import subprocess, tempfile, os, pathlib

app = Flask(__name__)

HTML = """
<!doctype html>
<title>YT → MP3</title>
<h2>Встав URL YouTube і натисни Download</h2>
<form action="/download" method="post">
  <input name="url" style="width:60%;" placeholder="https://youtu.be/...">
  <button type="submit">Download</button>
</form>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    if not url:
        return abort(400, "No URL provided")

    tmpdir = tempfile.mkdtemp()
    out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp", "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", out_template,
        url
    ]

    try:
        subprocess.run(cmd, check=True, cwd=tmpdir, timeout=300)
    except Exception as e:
        return f"Error: {e}", 500

    files = list(pathlib.Path(tmpdir).glob("*.mp3"))
    if not files:
        return "No mp3 found", 500

    return send_file(str(files[0]), as_attachment=True,
                     download_name=os.path.basename(files[0]))
