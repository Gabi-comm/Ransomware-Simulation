from ultralytics import YOLO
from roboflow import Roboflow

if __name__ == '__main__':
    # 1. Initialize YOLO model
    model = YOLO("yolov8n.pt")
    
    # 2. Download dataset from Roboflow
    rf = Roboflow(api_key="JVjvj0TbGk9Sr2npNrr0")
    project = rf.workspace("gabriel-zisua").project("gcash-receipt-detect-srujc")
    version = project.version(2)
    dataset = version.download("yolov8")
                
    # 3. Train the model using your GPU
    model.train(
        data=f"{dataset.location}/data.yaml",  
        epochs=100,                           
        imgsz=640,                            
        device=0,
        workers=0  # <--- Crucial for Windows! Prevents recursive process spawning crashes.
    )

    print("done")