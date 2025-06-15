from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import tempfile
import uuid
from urllib.parse import quote
import time
import cv2
import numpy as np
import base64
from string import ascii_uppercase
import operator
from keras.models import model_from_json
from spellchecker import SpellChecker
import threading
import io
from PIL import Image

app = Flask(__name__)

# Konfigurasi upload folder
UPLOAD_FOLDER = 'downloads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variables untuk ASL
latest_asl_text = ""
current_word = ""
asl_active = False
asl_models = {}
spell_checker = SpellChecker()

class ASLRecognizer:
    def __init__(self):
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        
        for i in ascii_uppercase:
            self.ct[i] = 0
            
        self.current_symbol = "Empty"
        self.word = ""
        self.sentence = ""
        
        # Load models
        self.load_models()
    
    def load_models(self):
        try:
            # Load main model
            with open("Models/model_new.json", "r") as json_file:
                model_json = json_file.read()
            self.loaded_model = model_from_json(model_json)
            self.loaded_model.load_weights("Models/model_new.h5")
            
            # Load DRU model
            with open("Models/model-bw_dru.json", "r") as json_file:
                model_json = json_file.read()
            self.loaded_model_dru = model_from_json(model_json)
            self.loaded_model_dru.load_weights("Models/model-bw_dru.h5")
            
            # Load TKDI model
            with open("Models/model-bw_tkdi.json", "r") as json_file:
                model_json = json_file.read()
            self.loaded_model_tkdi = model_from_json(model_json)
            self.loaded_model_tkdi.load_weights("Models/model-bw_tkdi.h5")
            
            # Load SMN model
            with open("Models/model-bw_smn.json", "r") as json_file:
                model_json = json_file.read()
            self.loaded_model_smn = model_from_json(model_json)
            self.loaded_model_smn.load_weights("Models/model-bw_smn.h5")
            
            print("ASL models loaded successfully")
            
        except Exception as e:
            print(f"Error loading ASL models: {e}")
            self.loaded_model = None
    
    def predict(self, test_image):
        if self.loaded_model is None:
            return
            
        try:
            test_image = cv2.resize(test_image, (128, 128))
            
            result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))
            result_dru = self.loaded_model_dru.predict(test_image.reshape(1, 128, 128, 1))
            result_tkdi = self.loaded_model_tkdi.predict(test_image.reshape(1, 128, 128, 1))
            result_smn = self.loaded_model_smn.predict(test_image.reshape(1, 128, 128, 1))
            
            prediction = {}
            prediction['blank'] = result[0][0]
            
            inde = 1
            for i in ascii_uppercase:
                prediction[i] = result[0][inde]
                inde += 1
            
            # LAYER 1
            prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
            self.current_symbol = prediction[0][0]
            
            # LAYER 2 - Refined predictions
            if self.current_symbol in ['D', 'R', 'U']:
                prediction = {}
                prediction['D'] = result_dru[0][0]
                prediction['R'] = result_dru[0][1]
                prediction['U'] = result_dru[0][2]
                prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
                self.current_symbol = prediction[0][0]
            
            if self.current_symbol in ['D', 'I', 'K', 'T']:
                prediction = {}
                prediction['D'] = result_tkdi[0][0]
                prediction['I'] = result_tkdi[0][1]
                prediction['K'] = result_tkdi[0][2]
                prediction['T'] = result_tkdi[0][3]
                prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
                self.current_symbol = prediction[0][0]
            
            if self.current_symbol in ['M', 'N', 'S']:
                prediction1 = {}
                prediction1['M'] = result_smn[0][0]
                prediction1['N'] = result_smn[0][1]
                prediction1['S'] = result_smn[0][2]
                prediction1 = sorted(prediction1.items(), key=operator.itemgetter(1), reverse=True)
                
                if prediction1[0][0] == 'S':
                    self.current_symbol = prediction1[0][0]
                else:
                    self.current_symbol = prediction[0][0]
            
            # Count predictions
            if self.current_symbol == 'blank':
                for i in ascii_uppercase:
                    self.ct[i] = 0
            
            self.ct[self.current_symbol] += 1
            
            # Check for stable prediction
            if self.ct[self.current_symbol] > 10:
                is_stable = True
                for i in ascii_uppercase:
                    if i == self.current_symbol:
                        continue
                    
                    tmp = abs(self.ct[self.current_symbol] - self.ct[i])
                    if tmp <= 5:
                        is_stable = False
                        break
                
                if not is_stable:
                    self.ct['blank'] = 0
                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return
                
                # Reset counter
                self.ct['blank'] = 0
                for i in ascii_uppercase:
                    self.ct[i] = 0
                
                # Process the recognized symbol
                if self.current_symbol == 'blank':
                    if self.blank_flag == 0:
                        self.blank_flag = 1
                        if len(self.sentence) > 0:
                            self.sentence += " "
                        self.sentence += self.word
                        self.word = ""
                else:
                    if len(self.sentence) > 50:  # Limit sentence length
                        self.sentence = ""
                    
                    self.blank_flag = 0
                    self.word += self.current_symbol
                    
                    # Update global variable
                    global current_word
                    current_word = self.word
                    
        except Exception as e:
            print(f"Error in ASL prediction: {e}")
    
    def get_current_text(self):
        return self.sentence + " " + self.word if self.word else self.sentence
    
    def get_word_suggestions(self):
        if self.word.strip():
            candidates = list(spell_checker.candidates(self.word.strip()))
            return sorted(candidates)[:3]
        return []

# Initialize ASL recognizer
asl_recognizer = ASLRecognizer()

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

@app.route('/asl-text', methods=['GET'])
def get_asl_text():
    global latest_asl_text
    return jsonify({
        'text': asl_recognizer.get_current_text(),
        'current_word': current_word,
        'suggestions': asl_recognizer.get_word_suggestions(),
        'current_symbol': asl_recognizer.current_symbol
    })

@app.route('/process-asl-frame', methods=['POST'])
def process_asl_frame():
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Convert to OpenCV format
        image = Image.open(io.BytesIO(image_bytes))
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Extract hand region (similar to GUI version)
        height, width = cv_image.shape[:2]
        x1 = int(0.5 * width)
        y1 = 10
        x2 = width - 10
        y2 = int(0.5 * width)
        
        # Crop the hand region
        hand_region = cv_image[y1:y2, x1:x2]
        
        # Preprocess image
        gray = cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 2)
        th3 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        ret, processed_image = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Make prediction
        asl_recognizer.predict(processed_image)
        
        return jsonify({
            'success': True,
            'current_symbol': asl_recognizer.current_symbol,
            'current_word': asl_recognizer.word,
            'sentence': asl_recognizer.sentence,
            'suggestions': asl_recognizer.get_word_suggestions()
        })
        
    except Exception as e:
        print(f"Error processing ASL frame: {e}")
        return jsonify({'error': f'Error processing frame: {str(e)}'}), 500

@app.route('/reset-asl', methods=['POST'])
def reset_asl():
    try:
        asl_recognizer.word = ""
        asl_recognizer.sentence = ""
        asl_recognizer.current_symbol = "Empty"
        
        # Reset counters
        asl_recognizer.ct['blank'] = 0
        for i in ascii_uppercase:
            asl_recognizer.ct[i] = 0
            
        return jsonify({'success': True, 'message': 'ASL session reset'})
    except Exception as e:
        return jsonify({'error': f'Error resetting ASL: {str(e)}'}), 500

@app.route('/use-suggestion', methods=['POST'])
def use_suggestion():
    try:
        data = request.json
        suggestion = data.get('suggestion', '')
        
        if suggestion:
            if asl_recognizer.sentence and not asl_recognizer.sentence.endswith(' '):
                asl_recognizer.sentence += ' '
            asl_recognizer.sentence += suggestion
            asl_recognizer.word = ""
            
            return jsonify({
                'success': True,
                'sentence': asl_recognizer.sentence,
                'current_word': asl_recognizer.word
            })
        else:
            return jsonify({'error': 'No suggestion provided'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error using suggestion: {str(e)}'}), 500

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

if __name__ == '__main__':
    print("Starting TTS + ASL Application...")
    app.run(debug=True, host='0.0.0.0', port=5000)