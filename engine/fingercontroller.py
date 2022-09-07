import cv2
import mediapipe as mp
from collections import deque
import threading
import time


class FingerController:
    def __init__(self) -> None:
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.stop = False
        self.buffer = Buffer()
        self.image = None

    def __capture_finger_location(self):
        self.stop = False
        cap = cv2.VideoCapture(0)
        with self.mp_hands.Hands(model_complexity=0,
                                 min_detection_confidence=0.5,
                                 min_tracking_confidence=0.5) as hands:
            while cap.isOpened() and not self.stop:
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                # self.image = image.copy()
                results = hands.process(image)
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    index_finger_tip = [hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x,
                                        hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y,
                                        hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].z,
                                        ]
                    self.buffer.add_point(*index_finger_tip)
        cap.release()

    def start_controller(self):
        t = threading.Thread(target=self.__capture_finger_location, daemon=True)
        t.start()

    def close(self):
        self.stop = True
    
    def get_finger_pos(self):
        return self.buffer.get_point()
    
    def get_image(self):
        return self.image


class Buffer:
    def __init__(self, bufferLen=10) -> None:
        self._buffer_x = deque(maxlen=bufferLen)
        self._buffer_y = deque(maxlen=bufferLen)
        self._buffer_z = deque(maxlen=bufferLen)

    def add_point(self, x, y, z):
        self._buffer_x.append(x)
        self._buffer_y.append(y)
        self._buffer_z.append(z)
    
    def get_point(self):
        if len(self._buffer_x) == 0:
            return (0, 0, 0)
        x = sum(self._buffer_x) / len(self._buffer_x)
        y = sum(self._buffer_y) / len(self._buffer_y)
        z = sum(self._buffer_z) / len(self._buffer_z)
        return (x, y, z)


