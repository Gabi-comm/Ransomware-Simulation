import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests from your frontend

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
    app.run(host='0.0.0.0', port=5000, debug=True)