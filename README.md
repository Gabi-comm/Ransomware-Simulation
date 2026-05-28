# Endpoint Extortion Ransomware

This program simulates a malicious host-lockdown screen that takes control of the display, blocks common system escape inputs, triggers distressing audio/visual indicators, and initiates an endpoint shutdown sequence upon timer expiration.


## Behavioral Mechanics Demonstrated

This script showcases several endpoint hijacking techniques commonly analyzed by Security Operations Center (SOC) teams:

* **Persistence & Input Suppression:** Utilizes lower-level hooks (`keyboard`) to trap critical administrative keys like `Tab`, `Left Windows`, and `Right Windows`, restricting user navigation away from the malicious interface.
* **Aggressive Audio/Visual Manipulation:** Speeds up and plays a continuous looping alarm (`pygame.mixer`) while simultaneously implementing an infinite async color-flash sequence (`tkinter.after()`) to induce user panic.
* **Perpetual Volumetric Control:** Directly interfaces with the Windows Core Audio API (`pycaw`) to actively poll the endpoint mixer, force-unmuting the device and steadily increasing the volume to maximum capacity if the user attempts to silence it.
* **Destructive Simulation (Automated Triage):** Simulates data destruction via an operational system command (`os.system("shutdown /s /t 0")`) executing exactly at the end of the 60-second countdown.

## Tech Stack & Dependencies

* **UI Framework:** Python `tkinter` (Native GUI)
* **Audio Layer:** `pygame`
* **Windows API Access:** `pycaw`, `comtypes`, `ctypes`
* **Input Hooking:** `keyboard`
* **Image Processing:** `Pillow` (PIL)

## Asset Requirements

To execute the user interface successfully, place the following assets in the root directory alongside your script:
* `alarm.mp3` - The underlying looping audio payload.
* `alarm.gif` - The flashing graphic displayed on the left pane.
* `qr.jpeg` - A mock InstaPay QR transaction graphic displayed on the right pane.

## Security Analyst Testing Notes
* **Emergency Exit Hook:** For testing purposes during live lab deployments, an administrative backdoor bind is hardcoded. Pressing **`Escape` + `0`** simultaneously will instantly destroy the root UI instance and terminate execution cleanly without triggering the system shutdown.
* **Virtual Environment Execution:** It is highly recommended to run this within your project virtual environment (`secai_gab_env`) to keep your host space clean of OS-level hooks.
