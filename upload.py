from ultralytics import YOLO

model = YOLO(r'runs/detect/train-7/weights/best.pt')
results=model("sample.jpeg")

for result in results:
    for box in result.boxes:
        confidence = box.conf.item()
        print(f"Accuracy: {confidence * 100:.2f}%")