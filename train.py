from ultralytics import YOLO
from roboflow import Roboflow

if __name__ == '__main__':
    model = YOLO("yolov8n.pt")

    rf = Roboflow(api_key="JVjvj0TbGk9Sr2npNrr0")
    project = rf.workspace("gabriel-zisua").project("gcash-receipt-detect-srujc")
    version = project.version(2)
    dataset = version.download("yolov8")

    model.train(
        data=f"{dataset.location}/data.yaml",  
        epochs=100,                           
        imgsz=640,                            
        device=0,
        workers=0 
    )
    print("done")