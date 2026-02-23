from flask import Flask, request, jsonify, render_template
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/get-video', methods=['POST'])
def get_video():
    try:
        data = request.json
        video_url = data.get('url')
        if not video_url:
            return jsonify({"status": "error", "message": "Link yok"}), 400

      # Gelen linke göre motorun vitesini (formatını) belirliyoruz
        if 'vk.com' in url:
            # VK için senin o özel HEVC ayarın (eski kodunda ne yazıyorsa tam onu buraya koyabilirsin)
            # Örnek bir HEVC destekli format:
            secilen_format = 'bestvideo[vcodec~="^hev|^h265"]+bestaudio/best'
        else:
            # YouTube ve diğer tüm siteler için takılmayan, esnek ayarımız
            secilen_format = 'best[ext=mp4]/best'

        # Motorun Ana Ayarları
        ydl_opts = {
            'format': secilen_format,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({"status": "success", "url": info.get('url'), "title": info.get('title', 'video')})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/update-cookies', methods=['POST'])
def update_cookies():
    try:
        data = request.json
        secret = data.get('secret')
        # Güvenlik: Sadece bu şifreyi bilen ajan çerez güncelleyebilir!
        if secret != "ALPEREN_GIZLI_ANAHTAR_1919":
            return jsonify({"status": "error", "message": "Yetkisiz erişim!"}), 401
        
        cookies_text = data.get('cookies')
        if cookies_text:
            # Gelen taze çerezleri cookies.txt dosyasına yaz
            with open('cookies.txt', 'w', encoding='utf-8') as f:
                f.write(cookies_text)
            return jsonify({"status": "success", "message": "Cerezler basariyla guncellendi!"})
        
        return jsonify({"status": "error", "message": "Cerez verisi bos!"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


