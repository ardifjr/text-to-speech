import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from datetime import datetime
import pygame
from gtts import gTTS
import tempfile
from pydub import AudioSegment
from pydub.playback import play
import io

class ModernTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Text-to-Speech Indonesia")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Variables
        self.is_playing = False
        self.current_audio = None
        self.temp_files = []
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create modern GUI
        self.create_modern_widgets()
        
        # Center window
        self.center_window()
        
        # Apply modern styling
        self.apply_modern_style()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def apply_modern_style(self):
        """Apply modern dark theme styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Modern.TFrame', background='#16213e')
        style.configure('Modern.TLabel', background='#16213e', foreground='#ffffff')
        style.configure('Modern.TCombobox', fieldbackground='#0f3460', foreground='#ffffff')
        style.configure('Modern.TButton', background='#e94560', foreground='#ffffff')
        style.map('Modern.TButton', background=[('active', '#d63447')])
    
    def create_modern_widgets(self):
        """Create modern GUI widgets with gradient-like effects"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header section with gradient effect simulation
        header_frame = tk.Frame(main_container, bg='#16213e', relief='flat', bd=0)
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Add some visual depth with multiple frames
        header_shadow = tk.Frame(header_frame, bg='#0f1419', height=4)
        header_shadow.pack(fill='x', side='bottom')
        
        header_content = tk.Frame(header_frame, bg='#16213e', padx=30, pady=25)
        header_content.pack(fill='x')
        
        # Title with modern styling
        title_label = tk.Label(header_content, 
                              text="🎙️ Text-to-Speech Indonesia", 
                              font=("Segoe UI", 28, "bold"), 
                              fg='#ffffff', bg='#16213e')
        title_label.pack()
        
        subtitle_label = tk.Label(header_content, 
                                 text="Ubah teks menjadi suara Indonesia yang natural", 
                                 font=("Segoe UI", 12), 
                                 fg='#8892b0', bg='#16213e')
        subtitle_label.pack(pady=(5, 0))
        
        # Input section with modern card design
        input_card = tk.Frame(main_container, bg='#16213e', relief='flat', bd=0)
        input_card.pack(fill='both', expand=True, pady=(0, 20))
        
        # Card shadow effect
        input_shadow = tk.Frame(input_card, bg='#0f1419', height=3)
        input_shadow.pack(fill='x', side='bottom')
        
        input_content = tk.Frame(input_card, bg='#16213e', padx=25, pady=25)
        input_content.pack(fill='both', expand=True)
        
        # Input label
        input_label = tk.Label(input_content, text="📝 Masukkan Teks", 
                              font=("Segoe UI", 14, "bold"),
                              fg='#64ffda', bg='#16213e')
        input_label.pack(anchor='w', pady=(0, 15))
        
        # Text input with modern styling
        text_frame = tk.Frame(input_content, bg='#0f3460', relief='flat', bd=0)
        text_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Inner shadow effect for text area
        text_border = tk.Frame(text_frame, bg='#0a2647', height=2)
        text_border.pack(fill='x')
        
        self.text_entry = tk.Text(text_frame, height=10, 
                                 font=("Segoe UI", 12), wrap=tk.WORD,
                                 bg='#0f3460', fg='#ffffff',
                                 relief='flat', bd=0, padx=15, pady=15,
                                 insertbackground='#64ffda',
                                 selectbackground='#e94560')
        self.text_entry.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Placeholder
        self.setup_placeholder()
        
        # Settings section with modern cards
        settings_frame = tk.Frame(main_container, bg='#1a1a2e')
        settings_frame.pack(fill='x', pady=(0, 20))
        
        # Gender selection card
        gender_card = tk.Frame(settings_frame, bg='#16213e', relief='flat', bd=0)
        gender_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        gender_shadow = tk.Frame(gender_card, bg='#0f1419', height=2)
        gender_shadow.pack(fill='x', side='bottom')
        
        gender_content = tk.Frame(gender_card, bg='#16213e', padx=20, pady=20)
        gender_content.pack(fill='both', expand=True)
        
        tk.Label(gender_content, text="🗣️ Jenis Suara", 
                font=("Segoe UI", 12, "bold"),
                fg='#64ffda', bg='#16213e').pack(anchor='w', pady=(0, 10))
        
        self.gender_var = tk.StringVar(value="wanita")
        gender_frame = tk.Frame(gender_content, bg='#16213e')
        gender_frame.pack(fill='x')
        
        # Modern radio buttons
        wanita_rb = tk.Radiobutton(gender_frame, text="👩 Wanita", 
                                  variable=self.gender_var, value="wanita",
                                  font=("Segoe UI", 10), fg='#ffffff', bg='#16213e',
                                  selectcolor='#e94560', activebackground='#16213e',
                                  activeforeground='#ffffff')
        wanita_rb.pack(anchor='w', pady=2)
        
        pria_rb = tk.Radiobutton(gender_frame, text="👨 Pria", 
                               variable=self.gender_var, value="pria",
                               font=("Segoe UI", 10), fg='#ffffff', bg='#16213e',
                               selectcolor='#e94560', activebackground='#16213e',
                               activeforeground='#ffffff')
        pria_rb.pack(anchor='w', pady=2)
        
        # Speed selection card
        speed_card = tk.Frame(settings_frame, bg='#16213e', relief='flat', bd=0)
        speed_card.pack(side='left', fill='both', expand=True, padx=(5, 5))
        
        speed_shadow = tk.Frame(speed_card, bg='#0f1419', height=2)
        speed_shadow.pack(fill='x', side='bottom')
        
        speed_content = tk.Frame(speed_card, bg='#16213e', padx=20, pady=20)
        speed_content.pack(fill='both', expand=True)
        
        tk.Label(speed_content, text="⚡ Kecepatan", 
                font=("Segoe UI", 12, "bold"),
                fg='#64ffda', bg='#16213e').pack(anchor='w', pady=(0, 10))
        
        self.speed_var = tk.StringVar(value="normal")
        speed_options = [("🐌 Lambat", "slow"), ("🚶 Normal", "normal"), ("🏃 Cepat", "fast")]
        
        for text, value in speed_options:
            rb = tk.Radiobutton(speed_content, text=text, 
                               variable=self.speed_var, value=value,
                               font=("Segoe UI", 10), fg='#ffffff', bg='#16213e',
                               selectcolor='#e94560', activebackground='#16213e',
                               activeforeground='#ffffff')
            rb.pack(anchor='w', pady=2)
        
        # Format selection card
        format_card = tk.Frame(settings_frame, bg='#16213e', relief='flat', bd=0)
        format_card.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        format_shadow = tk.Frame(format_card, bg='#0f1419', height=2)
        format_shadow.pack(fill='x', side='bottom')
        
        format_content = tk.Frame(format_card, bg='#16213e', padx=20, pady=20)
        format_content.pack(fill='both', expand=True)
        
        tk.Label(format_content, text="💾 Format", 
                font=("Segoe UI", 12, "bold"),
                fg='#64ffda', bg='#16213e').pack(anchor='w', pady=(0, 10))
        
        self.format_var = tk.StringVar(value="mp3")
        format_options = [("🎵 MP3", "mp3"), ("🎶 WAV", "wav")]
        
        for text, value in format_options:
            rb = tk.Radiobutton(format_content, text=text, 
                               variable=self.format_var, value=value,
                               font=("Segoe UI", 10), fg='#ffffff', bg='#16213e',
                               selectcolor='#e94560', activebackground='#16213e',
                               activeforeground='#ffffff')
            rb.pack(anchor='w', pady=2)
        
        # Control buttons with modern design
        button_frame = tk.Frame(main_container, bg='#1a1a2e')
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Button container for centering
        button_container = tk.Frame(button_frame, bg='#1a1a2e')
        button_container.pack()
        
        # Modern buttons with hover effects
        self.play_btn = self.create_modern_button(button_container, "▶️ Putar", 
                                                 '#27ae60', self.play_text)
        self.play_btn.pack(side='left', padx=8)
        
        self.stop_btn = self.create_modern_button(button_container, "⏹️ Stop", 
                                                 '#e74c3c', self.stop_audio)
        self.stop_btn.pack(side='left', padx=8)
        self.stop_btn.config(state='disabled')
        
        self.save_btn = self.create_modern_button(button_container, "💾 Simpan", 
                                                 '#3498db', self.save_audio)
        self.save_btn.pack(side='left', padx=8)
        
        clear_btn = self.create_modern_button(button_container, "🗑️ Bersihkan", 
                                            '#95a5a6', self.clear_text)
        clear_btn.pack(side='left', padx=8)
        
        # Status section with modern design
        status_card = tk.Frame(main_container, bg='#16213e', relief='flat', bd=0)
        status_card.pack(fill='x')
        
        status_shadow = tk.Frame(status_card, bg='#0f1419', height=2)
        status_shadow.pack(fill='x', side='bottom')
        
        status_content = tk.Frame(status_card, bg='#16213e', padx=25, pady=15)
        status_content.pack(fill='x')
        
        self.status_label = tk.Label(status_content, text="📊 Status: Siap", 
                                    font=("Segoe UI", 11),
                                    fg='#64ffda', bg='#16213e')
        self.status_label.pack(side='left')
        
        # Modern progress bar
        self.progress = ttk.Progressbar(status_content, mode='indeterminate', length=200)
        self.progress.pack(side='right', padx=(10, 0))
    
    def create_modern_button(self, parent, text, color, command):
        """Create modern styled button with hover effects"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Segoe UI", 11, "bold"),
                       bg=color, fg='white', bd=0, relief='flat',
                       padx=25, pady=12, cursor='hand2')
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=self.darken_color(color))
        
        def on_leave(e):
            btn.config(bg=color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def darken_color(self, color):
        """Darken a hex color for hover effect"""
        color_map = {
            '#27ae60': '#229954',
            '#e74c3c': '#c0392b',
            '#3498db': '#2980b9',
            '#95a5a6': '#7f8c8d'
        }
        return color_map.get(color, color)
    
    def setup_placeholder(self):
        """Setup placeholder text functionality"""
        placeholder_text = "Ketikkan teks yang ingin diubah menjadi suara Indonesia di sini...\n\nContoh:\n- Halo, nama saya adalah asisten virtual\n- Hari ini cuaca sangat cerah\n- Satu, dua, tiga, empat, lima"
        
        self.text_entry.insert('1.0', placeholder_text)
        self.text_entry.config(fg='#8892b0')
        
        def on_focus_in(event):
            if self.text_entry.get('1.0', 'end-1c') == placeholder_text:
                self.text_entry.delete('1.0', tk.END)
                self.text_entry.config(fg='#ffffff')
        
        def on_focus_out(event):
            if not self.text_entry.get('1.0', 'end-1c').strip():
                self.text_entry.insert('1.0', placeholder_text)
                self.text_entry.config(fg='#8892b0')
        
        self.text_entry.bind('<FocusIn>', on_focus_in)
        self.text_entry.bind('<FocusOut>', on_focus_out)
    
    def get_text(self):
        """Get text from text entry"""
        text = self.text_entry.get('1.0', 'end-1c').strip()
        placeholder = "Ketikkan teks yang ingin diubah menjadi suara Indonesia di sini...\n\nContoh:\n- Halo, nama saya adalah asisten virtual\n- Hari ini cuaca sangat cerah\n- Satu, dua, tiga, empat, lima"
        if text == placeholder:
            return ""
        return text
    
    def update_status(self, message, color='#64ffda'):
        """Update status label"""
        self.status_label.config(text=f"📊 Status: {message}", fg=color)
        self.root.update()
    
    def play_text(self):
        """Play text as speech"""
        text = self.get_text()
        if not text:
            messagebox.showwarning("Peringatan", "Mohon masukkan teks terlebih dahulu!")
            return
        
        if self.is_playing:
            messagebox.showinfo("Info", "Audio sedang diputar. Tunggu hingga selesai atau tekan Stop.")
            return
        
        thread = threading.Thread(target=self._play_text_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _play_text_thread(self, text):
        """Thread function to play text"""
        temp_file_path = None
        try:
            self.is_playing = True
            self.play_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.update_status("Menghasilkan suara...", '#f39c12')
            self.progress.start()
            
            # Create temporary file path manually
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"tts_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
            
            # Generate and save audio
            self.generate_and_save_audio(text, temp_file_path)
            
            if os.path.exists(temp_file_path):
                self.update_status("Memutar audio...", '#f39c12')
                self.temp_files.append(temp_file_path)
                
                # Load and play with pygame
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy() and self.is_playing:
                    pygame.time.wait(100)
            else:
                raise Exception("Gagal membuat file audio")
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        finally:
            self.is_playing = False
            self.play_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.update_status("Siap")
            self.progress.stop()
            
            # Clean up temp file after a delay
            if temp_file_path and os.path.exists(temp_file_path):
                threading.Timer(2.0, self.cleanup_temp_file, args=[temp_file_path]).start()
    
    def generate_and_save_audio(self, text, output_path):
        """Generate audio and save directly to file"""
        try:
            # Use Indonesian language with appropriate speed
            slow_speech = (self.speed_var.get() == 'slow')
            tts = gTTS(text=text, lang='id', slow=slow_speech)
            
            # Save directly to file
            tts.save(output_path)
            
            # If we need to modify for gender or speed, load and process
            if self.gender_var.get() == "pria" or self.speed_var.get() == "fast":
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_mp3(output_path)
                    
                    # Adjust for male voice (lower pitch)
                    if self.gender_var.get() == "pria":
                        # Lower the pitch by reducing frame rate then restoring
                        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.85)})
                        audio = audio.set_frame_rate(22050)
                    
                    # Adjust speed for fast
                    if self.speed_var.get() == "fast" and not slow_speech:
                        audio = audio.speedup(playback_speed=1.25)
                    
                    # Save modified audio
                    audio.export(output_path, format='mp3')
                except ImportError:
                    # If pydub is not available, just use the basic gTTS output
                    pass
            
        except Exception as e:
            raise Exception(f"Gagal menghasilkan audio: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
        except Exception:
            pass
    
    def stop_audio(self):
        """Stop audio playback"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.update_status("Dihentikan", '#e74c3c')
            self.progress.stop()
        except Exception as e:
            messagebox.showerror("Error", f"Kesalahan saat menghentikan: {str(e)}")
    
    def save_audio(self):
        """Save text as audio file"""
        text = self.get_text()
        if not text:
            messagebox.showwarning("Peringatan", "Mohon masukkan teks terlebih dahulu!")
            return
        
        file_extension = self.format_var.get()
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{file_extension}",
            filetypes=[(f"{file_extension.upper()} files", f"*.{file_extension}"), 
                      ("All files", "*.*")],
            title="Simpan Audio"
        )
        
        if filename:
            thread = threading.Thread(target=self._save_audio_thread, args=(text, filename))
            thread.daemon = True
            thread.start()
    
    def _save_audio_thread(self, text, filename):
        """Thread function to save audio"""
        try:
            self.update_status("Menyimpan audio...", '#f39c12')
            self.progress.start()
            
            # Generate audio directly to the target file
            temp_path = filename.replace(f".{self.format_var.get()}", "_temp.mp3")
            self.generate_and_save_audio(text, temp_path)
            
            if os.path.exists(temp_path):
                # Convert to target format if needed
                if self.format_var.get() == "wav":
                    try:
                        from pydub import AudioSegment
                        audio = AudioSegment.from_mp3(temp_path)
                        audio.export(filename, format="wav")
                        os.remove(temp_path)  # Remove temp mp3 file
                    except ImportError:
                        # If pydub not available, just save as mp3
                        os.rename(temp_path, filename.replace(".wav", ".mp3"))
                        messagebox.showinfo("Info", "Pydub tidak tersedia, file disimpan sebagai MP3")
                else:
                    # Just rename the temp file
                    os.rename(temp_path, filename)
                
                self.update_status("Audio berhasil disimpan!", '#27ae60')
                messagebox.showinfo("Sukses", f"Audio berhasil disimpan sebagai:\n{filename}")
            else:
                raise Exception("Gagal membuat file audio")
        
        except Exception as e:
            messagebox.showerror("Error", f"Kesalahan saat menyimpan: {str(e)}")
            self.update_status("Gagal menyimpan", '#e74c3c')
        finally:
            self.progress.stop()
    
    def clear_text(self):
        """Clear text entry"""
        self.text_entry.delete('1.0', tk.END)
        placeholder_text = "Ketikkan teks yang ingin diubah menjadi suara Indonesia di sini...\n\nContoh:\n- Halo, nama saya adalah asisten virtual\n- Hari ini cuaca sangat cerah\n- Satu, dua, tiga, empat, lima"
        self.text_entry.insert('1.0', placeholder_text)
        self.text_entry.config(fg='#8892b0')
        self.update_status("Teks dibersihkan")
    
    def __del__(self):
        """Cleanup temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass

def main():
    root = tk.Tk()
    app = ModernTTSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()