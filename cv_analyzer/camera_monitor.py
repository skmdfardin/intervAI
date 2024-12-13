import cv2
import mediapipe as mp
import time
from threading import Thread

class CameraMonitor:
    def __init__(self, cheating_callback):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.is_running = False
        self.cheating_start_time = None
        self.cheating_callback = cheating_callback
        self.current_frame = None
        
    def start(self):
        self.is_running = True
        Thread(target=self._monitor_feed, daemon=True).start()
        
    def stop(self):
        self.is_running = False
        self.cap.release()
        
    def get_frame(self):
        return self.current_frame
        
    def _monitor_feed(self):
        while self.is_running:
            success, image = self.cap.read()
            if not success:
                continue
                
            # Convert to RGB for processing
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_image)
            
            # Draw face detection boxes
            if results.detections:
                for detection in results.detections:
                    self._draw_detection(image, detection)
                
            face_count = len(results.detections) if results.detections else 0
            
            # Cheating detection logic
            if face_count > 1:
                if self.cheating_start_time is None:
                    self.cheating_start_time = time.time()
                elif time.time() - self.cheating_start_time > 3:
                    self.cheating_callback()
                    break
            else:
                self.cheating_start_time = None
                
            self.current_frame = image