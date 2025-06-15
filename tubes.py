from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import tempfile
import uuid
from urllib.parse import quote
import time

app = Flask(__name__)

# Konfigurasi upload folder
UPLOAD_FOLDER = 'downloads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'Indonesian Female')
        rate = data.get('rate', 1.0)
        audio_format = data.get('format', 'mp3')
        
        # Validasi input
        if not text.strip():
            return jsonify({'error': 'Teks tidak boleh kosong'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Teks terlalu panjang (maksimal 1000 karakter)'}), 400
        
        # Menggunakan Google Translate TTS API sebagai alternatif
        # Ini adalah endpoint publik yang bisa digunakan
        
        # Encode text untuk URL
        encoded_text = quote(text)
        
        # Google Translate TTS URL
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=id&client=tw-ob&ttsspeed={rate}"
        
        # Headers untuk menghindari blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Mengirim request ke Google TTS
        response = requests.get(tts_url, headers=headers, timeout=30)
        
        if response.status_code == 200 and response.content:
            # Generate unique filename
            unique_id = str(uuid.uuid4())[:8]
            audio_filename = f"tts_audio_{unique_id}.{audio_format}"
            audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
            
            # Menyimpan audio ke file
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            # Verifikasi file berhasil dibuat
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                return jsonify({
                    'success': True,
                    'audio_url': f'/download/{audio_filename}',
                    'message': 'Audio berhasil dibuat!',
                    'filename': audio_filename
                })
            else:
                return jsonify({'error': 'Gagal menyimpan file audio'}), 500
        else:
            return jsonify({'error': 'Gagal mengambil audio dari server TTS'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout - Coba lagi dengan teks yang lebih pendek'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Kesalahan jaringan: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return "File tidak ditemukan", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

# Route untuk membersihkan file lama (opsional)
@app.route('/cleanup')
def cleanup_old_files():
    try:
        current_time = time.time()
        cleaned_count = 0
        
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            # Hapus file yang lebih dari 1 jam
            if os.path.isfile(file_path) and (current_time - os.path.getctime(file_path)) > 3600:
                os.remove(file_path)
                cleaned_count += 1
        
        return jsonify({'message': f'Berhasil membersihkan {cleaned_count} file lama'})
    except Exception as e:
        return jsonify({'error': f'Gagal membersihkan: {str(e)}'}), 500

latest_asl_text = ""

@app.route('/asl-text', methods=['GET'])
def get_asl_text():
    global latest_asl_text
    return jsonify({'text': latest_asl_text})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)