from .keypoint_classifier.keypoint_classifier import KeyPointClassifier
from .point_history_classifier.point_history_classifier import PointHistoryClassifier

import os

__folder = os.path.dirname(os.path.abspath(__file__))
keypointCSV = os.path.join(__folder, 'keypoint_classifier/keypoint_classifier_label.csv')
pointhistoryCSV = os.path.join(__folder, 'point_history_classifier/point_history_classifier_label.csv')
