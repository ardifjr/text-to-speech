from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import base64
from io import BytesIO
import tempfile

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
        
        # Validasi input
        if not text.strip():
            return jsonify({'error': 'Teks tidak boleh kosong'}), 400
        
        # ResponsiveVoice API endpoint
        api_url = "https://responsivevoice.org/responsivevoice/getvoice.php"
        
        # Parameter untuk API
        params = {
            't': text,
            'tl': 'id',  # Indonesian language
            'sv': voice,
            'vn': '',
            'pitch': 0.5,
            'rate': rate,
            'vol': 1,
            'gender': 'female' if 'Female' in voice else 'male'
        }
        
        # Mengirim request ke ResponsiveVoice API
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            # Menyimpan audio ke file sementara
            audio_filename = f"tts_audio_{hash(text + voice + str(rate))}.mp3"
            audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
            
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            return jsonify({
                'success': True,
                'audio_url': f'/download/{audio_filename}',
                'message': 'Audio berhasil dibuat!'
            })
        else:
            return jsonify({'error': 'Gagal membuat audio'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File tidak ditemukan", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)