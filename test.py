import cv2
from ultralytics import YOLO

if __name__ == '__main__':
    try:
        model = YOLO("runs/detect/train-7/weights/best.pt")
    except:
        model = YOLO("runs/detect/train-7/weights/best.pt")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Press 'q' to quit the camera view.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        results = model(frame, stream=True, device=0)


        for r in results:
            annotated_frame = r.plot()

        cv2.imshow("GCash Receipt Detection - Live Test", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()