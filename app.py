from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
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

    # VK için özel HEVC mantığı, ancak '+' (ayrı ayrı indir) yerine tek parça ('best') istiyoruz
    if 'vk.com' in video_url:
        secilen_format = 'best[vcodec~="^hev|^h265"]/best'
    else:
        secilen_format = 'best' # Diğer siteler için de en iyi tek parça format

    ydl_opts = {
        'format': secilen_format, # Özel kuralımızı nihayet buraya bağladık!
        'cookiefile': 'cookies.txt',
        'quiet': True,
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        
        # Linki almayı garanti altına alıyoruz
        extracted_url = info.get('url')
        
        # Eğer hala direkt URL yoksa, formatların içine girip birleşik videoyu buluyoruz
        if not extracted_url and 'formats' in info:
            for f in reversed(info['formats']): # En kaliteliler genelde sondayken
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    extracted_url = f.get('url')
                    break
        
        # Eğer her şeye rağmen link bulunamadıysa, null göndermek yerine hata fırlat
        if not extracted_url:
            return jsonify({'status': 'error', 'message': 'Video gizli veya indirme linki çözülemedi.'})

        return jsonify({
            'status': 'success',
            'title': info.get('title', 'Video'),
            'url': extracted_url
        })

        except Exception as e:
# ... geri kalanı aynı
        return jsonify({'status': 'error', 'message': str(e)})
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












