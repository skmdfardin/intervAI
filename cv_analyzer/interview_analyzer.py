import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
import logging

@dataclass
class InterviewMetrics:
    shoulder_alignment: float  # 0-10
    back_straightness: float  # 0-10
    head_stability: float    # 0-10
    eye_level: float        # 0-10
    fidget_score: float     # 0-10
    overall_stability: float # 0-10
    hand_gesture_score: float # 0-10
    leaning_score: float    # 0-10
    
    def get_total_score(self):
        weights = {
            'shoulder_alignment': 1.0,
            'back_straightness': 1.5,
            'head_stability': 1.25,
            'eye_level': 1.25,
            'fidget_score': 1.0,
            'overall_stability': 1.5,
            'hand_gesture_score': 1.0,
            'leaning_score': 1.5
        }
        
        total = sum(getattr(self, metric) * weight 
                   for metric, weight in weights.items())
        return (total / sum(weights.values())) * 10  # Scale to 0-100

class InterviewAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.frame_count = 0
        self.posture_scores = []
        
    def analyze_frame(self, frame):
        results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            metrics = self._calculate_posture_metrics(results.pose_landmarks)
            self.posture_scores.append(metrics)
            return self._draw_landmarks(frame, results), metrics
        return frame, None
    
    def _calculate_posture_metrics(self, landmarks):
        # Calculate shoulder alignment
        left_shoulder = np.array([landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                                landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y])
        right_shoulder = np.array([landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                                 landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y])
        shoulder_alignment = abs(left_shoulder[1] - right_shoulder[1]) * 100
        
        # Add more metrics calculations here
        
        return PostureMetrics(
            shoulder_alignment=shoulder_alignment,
            head_position=0.0,  # Implement head position calculation
            overall_stability=0.0  # Implement stability calculation
        )
    
    def _draw_landmarks(self, frame, results):
        mp.solutions.drawing_utils.draw_landmarks(
            frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return frame
    
    def get_overall_score(self):
        if not self.posture_scores:
            return 0
        avg_shoulder = np.mean([m.shoulder_alignment for m in self.posture_scores])
        # Calculate other metrics
        return max(0, 100 - avg_shoulder * 10)  # Simple scoring example
