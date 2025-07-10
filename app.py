from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    video_info = None

    if request.method == 'POST':
        url = request.form['url']
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = []
            for f in info.get("formats", []):
                fid = f.get("format_id")
                ext = f.get("ext")
                if not fid or not ext:
                    continue
                resolution = f.get("resolution") or f.get("height") or "audio"
                filesize = f.get('filesize') or f.get('filesize_approx') or 0
                size_mb = int(filesize / (1024 * 1024)) if filesize else '?'
                label = f"{fid} - {ext} - {resolution} - {size_mb} MB"
                formats.append({
                    'id': fid,
                    'label': label
                })

            video_info = {
                'title': info.get('title'),
                'url': url,
                'formats': formats
            }

        except Exception as e:
            error = str(e)

    return render_template("index.html", video_info=video_info, error=error)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format_id']

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    ydl_opts = {
        'format': format_id,
        'ffmpeg_location': 'C:\\ffmpeg\\bin\\ffmpeg.exe',  # change if needed
        'outtmpl': filepath,
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return f"Download failed: {str(e)}", 500

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    app.run(debug=True)
