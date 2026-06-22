import subprocess
import time
import urllib.request
import urllib.error
import os

def test_server():
    print("Starting test...")
    # Clean up old qr.png if exists
    if os.path.exists("qr.png"):
        os.remove("qr.png")
        print("Removed old qr.png")

    # Free up port 5000 if in use
    try:
        output = subprocess.check_output("netstat -ano | findstr :5000", shell=True).decode()
        for line in output.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f"Killing process {pid} using port 5000...")
                subprocess.run(f"taskkill /PID {pid} /F", shell=True)
                time.sleep(1)
    except Exception as e:
        print("Port 5000 is clean.")

    # Start Flask app using python from virtual environment
    print("Running Flask app...")
    python_bin = os.path.join(".venv", "Scripts", "python.exe")
    process = subprocess.Popen([python_bin, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait a moment for server to start (including YOLO model load time)
    time.sleep(15)
    
    # Check if qr.png was generated
    if os.path.exists("qr.png"):
        print("PASS: qr.png was generated successfully!")
    else:
        print("FAIL: qr.png was NOT generated!")
    
    # Hit /cancel-shutdown
    try:
        req = urllib.request.Request("http://127.0.0.1:5000/cancel-shutdown", method="POST")
        with urllib.request.urlopen(req) as response:
            print(f"Response from /cancel-shutdown: {response.read().decode()}")
    except urllib.error.URLError as e:
        print(f"Error hitting /cancel-shutdown: {e}")
        process.terminate()
        stdout, stderr = process.communicate()
        print("--- SERVER STDOUT ---")
        print(stdout)
        print("--- SERVER STDERR ---")
        print(stderr)
        return

    # Check if server is still running (it should be)
    poll = process.poll()
    if poll is not None:
        print(f"FAIL: Server exited prematurely with code {poll}")
        stdout, stderr = process.communicate()
        print("--- SERVER STDOUT ---")
        print(stdout)
        print("--- SERVER STDERR ---")
        print(stderr)
        return
    else:
        print("PASS: Server is running active.")

    # Hit /request-shutdown
    try:
        req = urllib.request.Request("http://127.0.0.1:5000/request-shutdown", method="POST")
        with urllib.request.urlopen(req) as response:
            print(f"Response from /request-shutdown: {response.read().decode()}")
    except urllib.error.URLError as e:
        print(f"Error hitting /request-shutdown: {e}")
        process.terminate()
        return

    # Wait 6 seconds and check if server stopped automatically
    print("Waiting 6 seconds for server to auto-shutdown...")
    time.sleep(6)
    
    poll = process.poll()
    if poll is not None:
        print("PASS: Server auto-shutdown worked correctly!")
        stdout, stderr = process.communicate()
        print("--- SERVER STDOUT ---")
        print(stdout)
        print("--- SERVER STDERR ---")
        print(stderr)
    else:
        print("FAIL: Server is still running after request-shutdown + timeout!")
        process.terminate()

if __name__ == "__main__":
    test_server()
