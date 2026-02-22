from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Sunucu Calisiyor!"

@app.route('/get-video', methods=['POST'])
def get_video():
    try:
        data = request.json
        video_url = data.get('url')
        if not video_url:
            return jsonify({"status": "error", "message": "Link yok"}), 400

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Android MP4 sever, zorla MP4 bul.
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True, # Coğrafi engelleri aş.
            # 'cookiefile': 'cookies.txt', # İleride Instagram/X tam kilitlenirse başındaki # işaretini kaldırıp çerezleri devreye sokacağız.
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({"status": "success", "url": info.get('url'), "title": info.get('title', 'video')})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

