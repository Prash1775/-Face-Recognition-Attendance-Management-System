import numpy as np
import av
from PIL import Image
from streamlit_webrtc import VideoProcessorBase
from components import liveness

class AttendanceProcessor(VideoProcessorBase):
    def __init__(self):
        self.target_face_encoding = None
        self.challenge_num = 0
        self.verified = False
        self.status_message = "Initializing..."
        self.box_color = (0, 0, 255) # Red by default
        self.frame_count = 0

    def recv(self, frame):
        import cv2
        # Convert the frame from the WebRTC protocol to a standard OpenCV BGR image array
        img = frame.to_ndarray(format="bgr24")
        
        self.frame_count += 1
        
        # If we already passed verification, freeze the frame visually so the user sees "VERIFIED"
        if self.verified:
            cv2.putText(img, "VERIFIED! Processing Attendance...", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            return av.VideoFrame.from_ndarray(img, format="bgr24")
           
        if self.target_face_encoding is None or self.challenge_num == 0:
             self.status_message = "Waiting for setup data..."
             self.box_color = (0, 255, 255) # Yellow
        elif self.frame_count % 4 == 0:
             # Convert BGR to RGB for ML libraries (MediaPipe and Face_Recognition expect RGB)
             rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
             
             # 1. Detect Hand and Count Fingers
             fingers = liveness.count_fingers(rgb_img)
             if fingers == -1:
                 self.status_message = "No hand detected. Show fingers!"
                 self.box_color = (0, 0, 255)
             elif fingers != self.challenge_num:
                 self.status_message = f"Hold {self.challenge_num} fingers! (Detected {fingers})"
                 self.box_color = (0, 165, 255) # Orange
             else:
                 self.status_message = "Hand Good. Scanning Face..."
                 self.box_color = (255, 255, 0) # Cyan
                 
                 # 2. Hand challenge passed, now locate and scan the face!
                 from components import face_engine
                 face_enc = face_engine.extract_face_encoding(Image.fromarray(rgb_img))
                 
                 if face_enc is None:
                     self.status_message = "Face not found! Look straight."
                     self.box_color = (0, 0, 255)
                 else:
                     match = face_engine.verify_face(self.target_face_encoding, face_enc)
                     if match:
                         self.status_message = "FACE MATCHED!"
                         self.box_color = (0, 255, 0)
                         # Set the crucial flag that will automatically trigger Streamlit to shut down the camera!
                         self.verified = True 
                     else:
                         self.status_message = "FACE NOT MATCHED. Incorrect Person."
                         self.box_color = (0, 0, 255)
                         
        # Draw status directly onto the top-left of the live video using OpenCV Text
        cv2.putText(img, self.status_message, (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.box_color, 2, cv2.LINE_AA)
                    
        return av.VideoFrame.from_ndarray(img, format="bgr24")
