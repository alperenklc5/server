from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
from flask import Response, stream_with_context
import requests
print("Mevcut klasör içeriği:", os.listdir())
if os.path.exists('templates'):
    print("Templates klasörü içeriği:", os.listdir('templates'))

app = Flask(__name__)

# Mevcut home() kısmını bununla değiştir
import time # Dosyanın en başına ekle

@app.route('/')
def index():
    # Tarayıcıya her seferinde yeni bir 'versiyon' numarası gönderiyoruz
    return render_template('index.html', v=time.time())

@app.route('/get-video', methods=['POST'])
def get_video():
    try:
        data = request.json
        video_url = data.get('url')

        if not video_url:
            return jsonify({'status': 'error', 'message': 'Lütfen geçerli bir link girin.'})

       
        if 'vk.com' in video_url:
            secilen_format = 'best[vcodec~="^hev|^h265"]/best'
        else:
            secilen_format = 'best'

        ydl_opts = {
            'format': secilen_format,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
           
            extracted_url = info.get('url')
            
           
            if not extracted_url and 'formats' in info:
                for f in reversed(info['formats']): # En kaliteliler genelde sondayken
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        extracted_url = f.get('url')
                        break
            
            # 3. Hala bulamadıysa, null göndermek yerine hata veriyoruz
            if not extracted_url:
                return jsonify({'status': 'error', 'message': 'Video gizli veya indirme linki çözülemedi.'})

            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Video'),
                'url': extracted_url
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
@app.route('/proxy-download', methods=['GET'])
def proxy_download():
    target_url = request.args.get('url')
    if not target_url:
        return "URL bulunamadı", 400
    
    try:
        # 1. Sunucu (Coolify) kendi kimliğiyle Twitter'dan videoyu çekmeye başlar
        req = requests.get(target_url, stream=True, timeout=15)
        
        # 2. Videoyu anında parçalar halinde (stream) kullanıcıya aktarırız
        headers = {
            'Content-Disposition': 'attachment; filename="VD_PRO_Video.mp4"',
            'Content-Type': req.headers.get('content-type', 'video/mp4')
        }
        return Response(stream_with_context(req.iter_content(chunk_size=8192)), headers=headers)
    except Exception as e:
        return f"İndirme köprüsü çöktü: {str(e)}", 500
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















