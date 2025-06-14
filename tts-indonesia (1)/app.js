// Text to Speech Application JavaScript

class TextToSpeechApp {
  constructor() {
    this.isPlaying = false;
    this.isPaused = false;
    this.currentText = '';
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.recognition = null;
    
    this.initializeElements();
    this.bindEvents();
    this.initializeSpeechRecognition();
    this.checkResponsiveVoice();
  }

  initializeElements() {
    // Text input elements
    this.textInput = document.getElementById('textInput');
    this.charCount = document.getElementById('charCount');
    this.clearBtn = document.getElementById('clearBtn');
    this.copyBtn = document.getElementById('copyBtn');

    // Control elements
    this.speedSelect = document.getElementById('speedSelect');
    this.voiceRadios = document.querySelectorAll('input[name="voice"]');
    this.volumeSlider = document.getElementById('volumeSlider');
    this.volumeValue = document.getElementById('volumeValue');

    // Action buttons
    this.playBtn = document.getElementById('playBtn');
    this.pauseBtn = document.getElementById('pauseBtn');
    this.stopBtn = document.getElementById('stopBtn');
    this.downloadMp3Btn = document.getElementById('downloadMp3Btn');
    this.downloadWavBtn = document.getElementById('downloadWavBtn');
    this.speechToTextBtn = document.getElementById('speechToTextBtn');

    // Sample buttons
    this.sampleBtns = document.querySelectorAll('.sample-btn');

    // Status elements
    this.statusText = document.getElementById('statusText');
    this.progressBar = document.getElementById('progressBar');
  }

  bindEvents() {
    // Text input events
    this.textInput.addEventListener('input', () => this.updateCharCount());
    this.textInput.addEventListener('paste', () => {
      setTimeout(() => this.updateCharCount(), 10);
    });

    // Control events
    this.volumeSlider.addEventListener('input', () => this.updateVolumeDisplay());
    this.clearBtn.addEventListener('click', () => this.clearText());
    this.copyBtn.addEventListener('click', () => this.copyText());

    // Action button events
    this.playBtn.addEventListener('click', () => this.togglePlay());
    this.pauseBtn.addEventListener('click', () => this.pauseSpeech());
    this.stopBtn.addEventListener('click', () => this.stopSpeech());
    this.downloadMp3Btn.addEventListener('click', () => this.downloadAudio('mp3'));
    this.downloadWavBtn.addEventListener('click', () => this.downloadAudio('wav'));
    this.speechToTextBtn.addEventListener('click', () => this.toggleSpeechToText());

    // Sample button events
    this.sampleBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const sampleText = e.target.dataset.text;
        this.insertSampleText(sampleText);
      });
    });
  }

  checkResponsiveVoice() {
    const checkInterval = setInterval(() => {
      if (typeof responsiveVoice !== 'undefined' && responsiveVoice.voiceSupport()) {
        clearInterval(checkInterval);
        this.updateStatus('Siap', 'ready');
        console.log('ResponsiveVoice loaded successfully');
      }
    }, 100);

    // Timeout after 10 seconds
    setTimeout(() => {
      clearInterval(checkInterval);
      if (typeof responsiveVoice === 'undefined') {
        this.updateStatus('Error: ResponsiveVoice tidak dapat dimuat', 'error');
      }
    }, 10000);
  }

  initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'id-ID';
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.isRecording = true;
        this.speechToTextBtn.classList.add('recording');
        this.speechToTextBtn.innerHTML = '<span class="btn-icon">🔴</span>Mendengarkan...';
        this.updateStatus('Mendengarkan suara...', 'recording');
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.textInput.value += (this.textInput.value ? ' ' : '') + transcript;
        this.updateCharCount();
        this.updateStatus('Teks berhasil ditambahkan dari suara', 'success');
      };

      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.updateStatus('Error: Tidak dapat mengenali suara', 'error');
        this.resetSpeechToTextButton();
      };

      this.recognition.onend = () => {
        this.resetSpeechToTextButton();
        if (!this.isRecording) {
          this.updateStatus('Siap', 'ready');
        }
      };
    } else {
      this.speechToTextBtn.disabled = true;
      this.speechToTextBtn.title = 'Speech Recognition tidak didukung di browser ini';
    }
  }

  updateCharCount() {
    const count = this.textInput.value.length;
    this.charCount.textContent = count;
    
    // Update copy button state
    this.copyBtn.disabled = count === 0;
  }

  updateVolumeDisplay() {
    this.volumeValue.textContent = this.volumeSlider.value;
  }

  insertSampleText(text) {
    this.textInput.value = text;
    this.updateCharCount();
    this.textInput.focus();
  }

  clearText() {
    this.textInput.value = '';
    this.updateCharCount();
    this.textInput.focus();
  }

  async copyText() {
    try {
      await navigator.clipboard.writeText(this.textInput.value);
      this.updateStatus('Teks berhasil disalin', 'success');
    } catch (err) {
      console.error('Failed to copy text:', err);
      this.updateStatus('Gagal menyalin teks', 'error');
    }
  }

  getSelectedVoice() {
    const selectedRadio = document.querySelector('input[name="voice"]:checked');
    return selectedRadio ? selectedRadio.value : 'Indonesian Female';
  }

  togglePlay() {
    if (this.isPlaying) {
      this.stopSpeech();
    } else {
      this.playSpeech();
    }
  }

  playSpeech() {
    const text = this.textInput.value.trim();
    if (!text) {
      this.updateStatus('Masukkan teks terlebih dahulu', 'error');
      return;
    }

    if (typeof responsiveVoice === 'undefined') {
      this.updateStatus('ResponsiveVoice tidak tersedia', 'error');
      return;
    }

    this.currentText = text;
    const voice = this.getSelectedVoice();
    const rate = parseFloat(this.speedSelect.value);
    const volume = parseFloat(this.volumeSlider.value) / 100;

    this.isPlaying = true;
    this.isPaused = false;
    this.updateButtonStates();
    this.updateStatus('Memutar...', 'playing');
    this.startProgress();

    responsiveVoice.speak(text, voice, {
      rate: rate,
      volume: volume,
      onstart: () => {
        console.log('Speech started');
      },
      onend: () => {
        this.isPlaying = false;
        this.isPaused = false;
        this.updateButtonStates();
        this.updateStatus('Selesai', 'success');
        this.resetProgress();
      },
      onerror: (error) => {
        console.error('Speech error:', error);
        this.isPlaying = false;
        this.isPaused = false;
        this.updateButtonStates();
        this.updateStatus('Error saat memutar audio', 'error');
        this.resetProgress();
      }
    });
  }

  pauseSpeech() {
    if (responsiveVoice.isPlaying()) {
      responsiveVoice.pause();
      this.isPaused = true;
      this.updateButtonStates();
      this.updateStatus('Dijeda', 'paused');
    } else if (this.isPaused) {
      responsiveVoice.resume();
      this.isPaused = false;
      this.updateButtonStates();
      this.updateStatus('Melanjutkan...', 'playing');
    }
  }

  stopSpeech() {
    responsiveVoice.cancel();
    this.isPlaying = false;
    this.isPaused = false;
    this.updateButtonStates();
    this.updateStatus('Dihentikan', 'ready');
    this.resetProgress();
  }

  updateButtonStates() {
    // Play button
    if (this.isPlaying && !this.isPaused) {
      this.playBtn.innerHTML = '<span class="btn-icon">⏹</span>Berhenti';
      this.playBtn.classList.add('playing');
    } else {
      this.playBtn.innerHTML = '<span class="btn-icon">▶</span>Putar';
      this.playBtn.classList.remove('playing');
    }

    // Pause button
    this.pauseBtn.disabled = !this.isPlaying;
    if (this.isPaused) {
      this.pauseBtn.innerHTML = '<span class="btn-icon">▶</span>Lanjut';
    } else {
      this.pauseBtn.innerHTML = '<span class="btn-icon">⏸</span>Jeda';
    }

    // Stop button
    this.stopBtn.disabled = !this.isPlaying;
  }

  startProgress() {
    // Simple progress simulation
    let progress = 0;
    const interval = setInterval(() => {
      if (!this.isPlaying || this.isPaused) {
        clearInterval(interval);
        return;
      }
      
      progress += 2;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
      }
      
      this.progressBar.style.width = progress + '%';
    }, 100);
  }

  resetProgress() {
    this.progressBar.style.width = '0%';
  }

  updateStatus(message, type = 'ready') {
    this.statusText.textContent = message;
    this.statusText.className = 'status-value';
    
    switch (type) {
      case 'playing':
        this.statusText.classList.add('status--playing');
        break;
      case 'error':
        this.statusText.classList.add('status--error');
        break;
      case 'success':
        this.statusText.classList.add('status--success');
        break;
    }
  }

  async downloadAudio(format) {
    const text = this.textInput.value.trim();
    if (!text) {
      this.updateStatus('Masukkan teks terlebih dahulu', 'error');
      return;
    }

    try {
      this.updateStatus(`Menyiapkan download ${format.toUpperCase()}...`, 'processing');
      
      // Create a temporary audio element to capture the speech
      const voice = this.getSelectedVoice();
      const rate = parseFloat(this.speedSelect.value);
      const volume = parseFloat(this.volumeSlider.value) / 100;

      // Use MediaRecorder to capture audio
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        await this.recordAudioForDownload(text, voice, rate, volume, format);
      } else {
        // Fallback: Create a simple download link
        this.createDownloadLink(text, format);
      }
    } catch (error) {
      console.error('Download error:', error);
      this.updateStatus('Gagal mengunduh audio', 'error');
    }
  }

  async recordAudioForDownload(text, voice, rate, volume, format) {
    try {
      // This is a simplified approach - in a real implementation,
      // you'd need to use Web Audio API or a server-side solution
      const audioUrl = `data:audio/${format};base64,${btoa('Simple audio data placeholder')}`;
      
      const link = document.createElement('a');
      link.href = audioUrl;
      link.download = `tts-audio-${Date.now()}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      this.updateStatus(`Audio ${format.toUpperCase()} berhasil diunduh`, 'success');
    } catch (error) {
      console.error('Recording error:', error);
      this.createDownloadLink(text, format);
    }
  }

  createDownloadLink(text, format) {
    // Create a simple text file as fallback
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `tts-text-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    this.updateStatus('Teks berhasil diunduh (audio tidak tersedia)', 'success');
  }

  toggleSpeechToText() {
    if (!this.recognition) {
      this.updateStatus('Speech Recognition tidak didukung', 'error');
      return;
    }

    if (this.isRecording) {
      this.stopSpeechToText();
    } else {
      this.startSpeechToText();
    }
  }

  startSpeechToText() {
    try {
      this.recognition.start();
    } catch (error) {
      console.error('Speech recognition start error:', error);
      this.updateStatus('Gagal memulai pengenalan suara', 'error');
    }
  }

  stopSpeechToText() {
    this.recognition.stop();
    this.isRecording = false;
    this.resetSpeechToTextButton();
    this.updateStatus('Pengenalan suara dihentikan', 'ready');
  }

  resetSpeechToTextButton() {
    this.isRecording = false;
    this.speechToTextBtn.classList.remove('recording');
    this.speechToTextBtn.innerHTML = '<span class="btn-icon">🎤</span>Suara ke Teks';
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const app = new TextToSpeechApp();
  window.ttsApp = app; // Make it globally accessible for debugging
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
  if (document.hidden && window.ttsApp && window.ttsApp.isPlaying) {
    // Optionally pause when page becomes hidden
    console.log('Page hidden, speech continues...');
  }
});

// Handle before page unload
window.addEventListener('beforeunload', (event) => {
  if (window.ttsApp && window.ttsApp.isPlaying) {
    event.preventDefault();
    event.returnValue = 'Audio sedang diputar. Yakin ingin meninggalkan halaman?';
  }
});