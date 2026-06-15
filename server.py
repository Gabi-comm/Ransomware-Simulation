from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import io
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = YOLO('runs/detect/train-7/weights/best.pt')

@app.post("/verify-receipt")
async def verify_receipt(file: UploadFile = File(...)):
    print(f"📥 Received file for verification: {file.filename}")
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # Run inference
    results = model(image)
    is_receipt = False
    
    for result in results:
        box_count = len(result.boxes)
        print(f"🔍 YOLO found {box_count} bounding boxes in this image.")
        if box_count > 0:
            is_receipt = True
            break
            
    print(f"📤 Sending response back to browser: {is_receipt}")
    return {"is_receipt": is_receipt}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)