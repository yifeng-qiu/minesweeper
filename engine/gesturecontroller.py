import cv2
import mediapipe as mp
from collections import deque, Counter
import threading
import csv
import numpy as np

from .models import KeyPointClassifier, PointHistoryClassifier, keypointCSV, pointhistoryCSV


class GestureController:
    pointHistoryLength = 16
    def __init__(self, debug=False) -> None:
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, 
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5)
        self.handGestureClassifier = KeyPointClassifier()
        self.fingerGestureClassifier = PointHistoryClassifier()
        self.handGestureLabels = self.readHandGestureLabels()
        self.fingerGestureLabels = self.readFingerGestureLabels()
        self.stop = False
        self.cameraImageSize = None
        self.debug = debug
        self.fingerpointHistory = deque(maxlen=self.pointHistoryLength)
        self.fingerGestureHistory = deque(maxlen=self.pointHistoryLength)
        self.handGestureBuffer = deque(maxlen=self.pointHistoryLength)
        self.lastPointerLocation = [0, 0]
        self.currentCommand = 'None'
    
    def readHandGestureLabels(self):
        with open(keypointCSV, encoding='utf-8-sig') as f:
            handGestureLabels = csv.reader(f)
            handGestureLabels = [
                row[0] for row in handGestureLabels
            ]
            
        return handGestureLabels

    def readFingerGestureLabels(self):
        with open(pointhistoryCSV, encoding='utf-8-sig') as f:
            fingerGestureLabels = csv.reader(f)
            fingerGestureLabels = [
                row[0] for row in fingerGestureLabels
            ]
        return fingerGestureLabels      

    def gestureRecognition(self, image):
        if self.cameraImageSize is None:
            self.cameraImageSize = [image.shape[1], image.shape[0]]

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True

        handSignID, fingerGestureID = None, None
        if results.multi_hand_landmarks:
            handLandmarks = results.multi_hand_landmarks[0]
            landmarkArray = self.getLandmarkArray(handLandmarks)
            vectorizedLandmarkArray = self.vectorizeLandmarkArray(landmarkArray)
            handSignID = self.handGestureClassifier(vectorizedLandmarkArray)
            if self.handGestureLabels[handSignID] == 'Pointer':  
                # if the hand gesture is Pointer
                self.fingerpointHistory.append(landmarkArray[8,:].tolist())  # Record the landmark values of the index finger

                # only infer the finger gesture in the Pointer mode
                fingerGestureID = 0
                if len(self.fingerpointHistory) == self.pointHistoryLength:
                    vectorizedFingerpointHistoryArray = self.vectorizePointHistory(self.fingerpointHistory)
                    fingerGestureID = self.fingerGestureClassifier(vectorizedFingerpointHistoryArray)

                # Infer the most probable finger gesture and push it into queue
                self.fingerGestureHistory.append(fingerGestureID)

            else:
                # Otherwise, just record 0. In other words, point_history will grow in size every cycle 
                # regardless whether the hand gesture is Pointer. 
                self.fingerpointHistory.append([0.0, 0.0]) 

        detectedHandGesture = self.handGestureLabels[handSignID] if handSignID is not None else 'undetected'
        return detectedHandGesture

    def __detectorThread(self):
        cap = cv2.VideoCapture(0)
        unsuccessfulReadout = 0
        while cap.isOpened() and self.stop == False:
            success, image = cap.read()
            if not success:
                if unsuccessfulReadout < 10:
                    unsuccessfulReadout += 1
                    cv2.waitKey(100)
                    continue
                else:
                    break
            handGesture = self.gestureRecognition(image)
            self.handGestureBuffer.append(handGesture)
            self.processCommand()
        cap.release()

    def processCommand(self):
        if len(self.handGestureBuffer) == self.pointHistoryLength:
            if self.handGestureBuffer.count('Open') == self.pointHistoryLength:
                self.currentCommand = 'click'
            elif self.handGestureBuffer.count('Close') == self.pointHistoryLength:
                self.currentCommand = 'flag'
            elif self.handGestureBuffer.count('Pointer') == self.pointHistoryLength:
            # elif self.handGestureBuffer[-1] == 'Pointer':
                # fingerGesture = Counter(self.fingerGestureHistory).most_common()[0][0]
                # if self.fingerGestureLabels[fingerGesture] == 'Move':
                self.lastPointerLocation = np.mean(np.array(self.fingerpointHistory).reshape(-1,2), axis=0).tolist()
                self.currentCommand = 'move'
            else:
                self.currentCommand = 'None'

    def startController(self):
        t = threading.Thread(target=self.__detectorThread)
        t.start()

    def close(self):
        self.stop = True
    
    def getCurrentCommand(self):
        return self.currentCommand
    
    def getLandmarkArray(self, landmarks) -> np.array:
        arr = np.array([(lm.x, lm.y) for lm in landmarks.landmark]).astype(np.float32)
        return arr

    def getAbsLandmarkArray(self, norm_landmarks_array:np.array) -> np.array:
        # the output of this function is used by the drawing functions
        image_shape = np.array(self.cameraImageSize).astype(np.int32)

        abs_landmark_array = np.int32(norm_landmarks_array * image_shape)
        abs_landmark_array = np.where(abs_landmark_array < image_shape - 1, abs_landmark_array, image_shape - 1)

        return abs_landmark_array

    def calcBoundingRect(self, abs_landmarks_array:np.array):
        x, y, w, h = cv2.boundingRect(abs_landmarks_array)
        return [x, y, x + w, y + h]

    def vectorizeLandmarkArray(self, landmarks_array:np.array) -> list[float]:
        """
        The hand gesture ML model works with normalized landmark values. Therefore we just need to 
        move their origin to the first landmark and vectorize the array. 
        In some cases, the normalized landmark values from Mediapipe can be greater than 1. It is unclear whether
        we need to normalize the array again to 1.
        
        """
        # Shift the origin of landmark coordinates to the first record
        relative_landmarks_array = landmarks_array - landmarks_array[0,:] 
        # Reshape to a vector and normalize to unity
        relative_landmarks_array = relative_landmarks_array.ravel() 
        maxVal = np.max(np.abs(relative_landmarks_array)) 
        relative_landmarks_array = relative_landmarks_array / maxVal
        
        return relative_landmarks_array

    def vectorizePointHistory(self, point_history:list[list[float]]) -> list[float]:
        point_history_array = np.array(point_history)
        point_history_array = point_history_array - point_history_array[0,:]
        point_history_array = point_history_array.ravel()

        return point_history_array

    def getAbsPointHistory(self, point_history:list[list[float]]) -> np.array:
        image_shape = np.array(self.cameraImageSize).astype(np.int32)
        abs_point_history = np.int32(np.array(point_history) * image_shape)
        abs_point_history = np.where(abs_point_history < image_shape - 1, abs_point_history, image_shape - 1)
        return abs_point_history




