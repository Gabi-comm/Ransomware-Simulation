import cv2
from ultralytics import YOLO

if __name__ == '__main__':
    # 1. Load your newly trained model weights
    # YOLOv8 saves your best weights automatically in runs/detect/train/weights/best.pt
    # We will point to 'train-4' or 'train' depending on your latest run folder
    try:
        model = YOLO("runs/detect/train-7/weights/best.pt")
    except:
        model = YOLO("runs/detect/train-7/weights/best.pt")

    # 2. Open the webcam (0 is usually the default built-in camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Press 'q' to quit the camera view.")

    # 3. Stream the live feed and run object detection
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Run inference on the frame using your GPU (device=0)
        results = model(frame, stream=True, device=0)

        # Visualize the results on the frame
        for r in results:
            annotated_frame = r.plot()

        # Display the live annotated stream
        cv2.imshow("GCash Receipt Detection - Live Test", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release everything when done
    cap.release()
    cv2.destroyAllWindows()