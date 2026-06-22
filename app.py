import os
import socket
import urllib.request
import urllib.parse
import threading
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests from your frontend

# Global variables for auto-shutdown mechanism
shutdown_timer = None

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public server (doesn't send actual packets)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generate_qr_code(url, filename="qr.png"):
    print(f"Generating QR code for: {url}")
    encoded_url = urllib.parse.quote(url)
    api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}"
    
    try:
        urllib.request.urlretrieve(api_url, filename)
        print(f"QR code successfully generated and saved to: {os.path.abspath(filename)}")
        print("✅ QR code ready for rand.py to display")
    except Exception as e:
        print(f"Failed to generate QR code via API: {e}. Trying offline generation...")
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            print(f"QR code successfully generated offline and saved to: {os.path.abspath(filename)}")
            print("✅ QR code ready for rand.py to display")
        except ImportError:
            print("To generate QR code offline, please run: pip install qrcode pillow")

@app.route('/request-shutdown', methods=['POST'])
def request_shutdown():
    global shutdown_timer
    if shutdown_timer is not None:
        shutdown_timer.cancel()
        
    def perform_shutdown():
        print("No active client page open. Shutting down Flask server...")
        os._exit(0)
        
    shutdown_timer = threading.Timer(4.0, perform_shutdown)
    shutdown_timer.start()
    return jsonify({'success': True, 'message': 'Shutdown scheduled in 4 seconds.'})

@app.route('/cancel-shutdown', methods=['POST'])
def cancel_shutdown():
    global shutdown_timer
    if shutdown_timer is not None:
        shutdown_timer.cancel()
        shutdown_timer = None
        print("Shutdown cancelled - client connection active.")
    return jsonify({'success': True, 'message': 'Shutdown cancelled.'})

# Load your custom YOLO model
MODEL_PATH = r'runs/detect/train-7/weights/best.pt'
model = YOLO(MODEL_PATH)

@app.route('/')
def index():
    # If index.html is placed inside a folder named 'templates'
    return render_template('index.html')

@app.route('/verify-receipt', methods=['POST'])
def verify_receipt():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    try:
        # Save file temporarily to pass to the model
        temp_path = "temp_upload.jpg"
        file.save(temp_path)

        # Run inference
        results = model(temp_path)
        
        is_valid_receipt = False
        highest_conf = 0.0

        for result in results:
            for box in result.boxes:
                confidence = box.conf.item()
                if confidence > highest_conf:
                    highest_conf = confidence
                
                # Check condition: 30% to 100% accuracy (0.30 to 1.0)
                if 0.30 <= confidence <= 1.0:
                    is_valid_receipt = True

        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if is_valid_receipt:
            return jsonify({
                'success': True, 
                'message': 'Valid GCash Receipt Verified.', 
                'confidence': f"{highest_conf * 100:.2f}%"
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Verification failed. Confidence ({highest_conf * 100:.2f}%) outside acceptable range (30%-100%).'
            })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    server_url = f"http://{local_ip}:{port}/"
    
    # Avoid generating/opening QR code twice when Werkzeug restarts in debug mode
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "="*50)
        print(f"Server is starting on: {server_url}")
        print("="*50 + "\n")
        generate_qr_code(server_url)
        
    app.run(host='0.0.0.0', port=port, debug=True)