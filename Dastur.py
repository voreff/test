from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import logging
import re

app = Flask(__name__)
CORS(app)

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_youtube_music(query):
    """
    YouTube'dan musiqani qidirish
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'noplaylist': True,
        'default_search': 'ytsearch10'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            if 'entries' in info:
                # Ko'p natijalar
                results = []
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'title': entry.get('title', 'Noma\'lum'),
                            'url': entry.get('webpage_url', ''),
                            'duration': entry.get('duration', 0),
                            'thumbnail': entry.get('thumbnail', ''),
                            'channel': entry.get('uploader', 'Noma\'lum')
                        })
                return results[:5]  # Faqat 5 ta natija
            else:
                # Bitta natija
                return [{
                    'title': info.get('title', 'Noma\'lum'),
                    'url': info.get('webpage_url', ''),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'channel': info.get('uploader', 'Noma\'lum')
                }]

    except Exception as e:
        logger.error(f"Xatolik: {str(e)}")
        return []


@app.route('/search', methods=['GET'])
def search_music():
    """
    Musiqa qidirish endpoint'i
    """
    query = request.args.get('q', '')

    if not query:
        return jsonify({'error': 'Qidiruv so\'rovini kiriting'}), 400

    logger.info(f"Qidiruv so'rovi: {query}")

    results = search_youtube_music(query)

    if not results:
        return jsonify({'error': 'Hech narsa topilmadi'}), 404

    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })


@app.route('/download', methods=['GET'])
def get_download_info():
    """
    Yuklab olish uchun ma'lumot olish
    """
    url = request.args.get('url', '')

    if not url:
        return jsonify({'error': 'URL kiriting'}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return jsonify({
                'title': info.get('title', ''),
                'url': info.get('webpage_url', ''),
                'audio_url': info.get('url', ''),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'channel': info.get('uploader', '')
            })

    except Exception as e:
        logger.error(f"Yuklab olish xatosi: {str(e)}")
        return jsonify({'error': 'Yuklab olishda xatolik'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    API holatini tekshirish
    """
    return jsonify({'status': 'OK', 'message': 'API ishlamoqda'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)