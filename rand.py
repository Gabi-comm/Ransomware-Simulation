import tkinter as tk
from pygame import mixer
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities
import keyboard
from PIL import Image, ImageTk

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

def start_countdown(count):
    timer_label.config(text=str(count))
    if count <= 0:
        on_closing()
    else:
        root.after(1000, start_countdown, count - 1)

image = tk.PhotoImage(file="alarm.gif")
label = tk.Label(root, image=image, bg="red")
label.pack(pady=(50, 10))

timer_label = tk.Label(root, text="10", font=("Helvetica", 72, "bold"), fg="white", bg="red")
timer_label.pack(pady=20)

image = tk.PhotoImage("alarm.gif")
label = tk.Label(root, image=image)
label.pack()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.config(bg= "red",cursor="none")
togglecol()
alarm()
enforce_unmute()
root.bind('<Escape>', lambda event: root.destroy())
root.bind("<F1>", lambda e: "break")
root.mainloop() 