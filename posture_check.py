import cv2
import mediapipe as mp
import numpy as np

class PostureAnalyzer:
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Models
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5)

    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Process all models
        pose_results = self.pose.process(image)
        face_results = self.face_mesh.process(image)
        hand_results = self.hands.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        feedback_list = []
        color = (0, 255, 0) # Green default

        # 1. POSTURE CHECK
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            left_s = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            right_s = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
            
            if abs(left_s - right_s) > 0.05:
                feedback_list.append("Sit Straight!")
                color = (0, 0, 255)

        # 2. EYE CONTACT (Head Orientation)
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                h, w, _ = image.shape
                # Nose tip (4) vs Left Ear (234) vs Right Ear (454)
                nose = face_landmarks.landmark[4]
                left_ear = face_landmarks.landmark[234]
                right_ear = face_landmarks.landmark[454]
                
                # Simple logic: If nose is too close to one ear, head is turned
                dist_left = abs(nose.x - left_ear.x)
                dist_right = abs(nose.x - right_ear.x)
                
                if abs(dist_left - dist_right) > 0.15: # Threshold
                    feedback_list.append("Look at Camera")
                    color = (0, 165, 255) # Orange

        # 3. FIDGETING (Hand touching Face)
        if hand_results.multi_hand_landmarks and face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            # Get bounding box of face
            x_vals = [l.x for l in face_landmarks.landmark]
            y_vals = [l.y for l in face_landmarks.landmark]
            min_x, max_x = min(x_vals), max(x_vals)
            min_y, max_y = min(y_vals), max(y_vals)

            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Check if any finger tip is inside face box
                for point in hand_landmarks.landmark:
                    if min_x < point.x < max_x and min_y < point.y < max_y:
                        feedback_list.append("Don't Touch Face")
                        color = (0, 0, 255)
                        break

        # Draw Output
        status_text = " | ".join(feedback_list) if feedback_list else "Perfect Body Language ✅"
        cv2.putText(image, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return image, status_text