import cv2
from engine import GestureController


if __name__ == '__main__':
    gc = GestureController(debug=True)
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        key = cv2.waitKey(10)
        if key == 27:
            break
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        debugImage = cv2.flip(image.copy(), 1)
        handID = gc.gestureRecognition(image)
        gc.handGestureBuffer.append(handID)
        gc.processCommand()
        command=gc.getCurrentCommand()
        cv2.putText(debugImage, f'hand gesture detected: {command}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        1, (255, 255, 255), 2, cv2.LINE_AA)

        lastPointLocation = gc.lastPointerLocation
        cv2.putText(debugImage, f'Last point location: {lastPointLocation}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
        1, (255, 255, 255), 2, cv2.LINE_AA)
        
        cv2.imshow('debug window', debugImage)
    cap.release()
    cv2.destroyAllWindows()

