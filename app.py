from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
import http.cookiejar
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
        'no_warnings': True,
        # --- INSTAGRAM KAMUFLAJI BURADA BAŞLIYOR ---
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Sec-Fetch-Mode': 'navigate'
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
        # 1. TikTok ve Instagram CDN'lerini kandırmak için GERÇEK bir tarayıcı kimliği
        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "*/*",
            "Referer": "https://www.tiktok.com/" # Çoğu güvenlik duvarı nereden gelindiğine bakar
        }
        
        # 2. Ajanımızın fırından yeni çıkardığı çerezleri köprüye dahil edelim
        cj = None
        if os.path.exists('cookies.txt'):
            try:
                cj = http.cookiejar.MozillaCookieJar('cookies.txt')
                cj.load(ignore_discard=True, ignore_expires=True)
            except Exception as ce:
                print(f"Proxy çerez yükleme uyarısı: {ce}")

        # 3. Sunucu (Coolify) kimliğini gizleyerek videoyu çeker
        req = requests.get(target_url, stream=True, timeout=15, headers=req_headers, cookies=cj)
        
        # 4. Videoyu anında parçalar halinde (stream) kullanıcıya aktarırız
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



















