import face_recognition
import numpy as np
import cv2
from PIL import Image
import io

# === UPGRADED CONFIGURATION ===
# Face recognition tolerance (lower = stricter matching)
TOLERANCE = 0.5  # Upgraded from 0.6 to minimize false positives
MODEL = "hog"    # Reverted to "hog" to massively speed up cpu performance (CNN is too slow without a GPU)
NUM_JITTERS = 1  # Reverted to 1 pass to prevent processing delays

def enhance_lighting(image_array):
    """
    Enhance the lighting and contrast of the face image using CLAHE.
    This fixes issues with under-exposed or heavily shadowed cameras.
    """
    try:
        # Ensure image is uint8
        if image_array.dtype != np.uint8:
            image_array = image_array.astype(np.uint8)
            
        # Convert RGB to LAB color space
        lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l_channel)
        
        # Merge back
        merged = cv2.merge((cl, a_channel, b_channel))
        enhanced_rgb = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
        
        return enhanced_rgb
    except Exception as e:
        print(f"Warning: CLAHE enhancement failed: {e}")
        return image_array

def extract_face_encoding(image_pil):
    """
    Extract face encoding from PIL Image
    Returns face encoding as numpy array or None if no face detected
    
    Args:
        image_pil: PIL Image object
    
    Returns:
        numpy array (128-d face encoding) or None
    """
    try:
        # Convert PIL Image to numpy array
        image_array = np.array(image_pil)
        
        # Upgrade: Apply lighting normalization
        image_array = enhance_lighting(image_array)
        
        # Convert RGB to BGR if needed (PIL is RGB by default)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # Assume PIL Image is RGB, face_recognition expects RGB
            pass
        
        # Find faces in image
        face_locations = face_recognition.face_locations(image_array, model=MODEL)
        
        if len(face_locations) == 0:
            return None  # No face detected
        
        if len(face_locations) > 1:
            # Multiple faces - return None and let user know
            return None
        
        # Upgrade: Extract robust face encoding for the single face using num_jitters
        face_encodings = face_recognition.face_encodings(
            image_array, 
            face_locations, 
            num_jitters=NUM_JITTERS
        )
        
        if len(face_encodings) > 0:
            return face_encodings[0]  # Return first (and only) face encoding
        
        return None
    
    except Exception as e:
        print(f"Error extracting face encoding: {e}")
        return None

def verify_face(stored_encoding, capture_encoding, tolerance=TOLERANCE):
    """
    Verify if two face encodings match
    
    Args:
        stored_encoding: numpy array (face encoding from database)
        capture_encoding: numpy array (face encoding from current capture)
        tolerance: matching tolerance (lower = stricter)
    
    Returns:
        bool: True if faces match, False otherwise
    """
    try:
        if stored_encoding is None or capture_encoding is None:
            return False
        
        # Calculate face distance
        distance = face_recognition.face_distance([stored_encoding], capture_encoding)[0]
        
        # Mathematically map distance to a standard Percentage logic (0.0 to 100.0%)
        if distance > tolerance:
            accuracy_percent = (1.0 - distance) / (1.0 - tolerance) * 50.0
        else:
            accuracy_percent = 100.0 - (distance / tolerance) * 50.0
            
        # Hard limits
        accuracy = max(0.0, min(100.0, accuracy_percent))
        is_match = distance <= tolerance
        
        # Print to Terminal explicitly!
        print("-" * 45)
        print("ACTIVE AI MODEL METRICS")
        print(f"-> Engine Target: {MODEL.upper()}")
        print(f"-> Confidence Match: {accuracy:.2f}%")
        print(f"-> Action Taken: {'ATTENDANCE APPROVED [OK]' if is_match else 'ATTENDANCE REJECTED [X]'}")
        print("-" * 45)
        
        return is_match
    
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False

def compare_faces_batch(known_encodings, capture_encoding, tolerance=TOLERANCE):
    """
    Compare one face against multiple known faces
    
    Args:
        known_encodings: list of numpy arrays
        capture_encoding: numpy array
        tolerance: matching tolerance
    
    Returns:
        list of bools and distances
    """
    try:
        if not known_encodings or capture_encoding is None:
            return [], []
        
        results = face_recognition.compare_faces(known_encodings, capture_encoding, tolerance=tolerance)
        distances = face_recognition.face_distance(known_encodings, capture_encoding)
        
        return results, distances
    
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return [], []

def process_camera_frame(image_pil):
    """
    Process camera input for face detection
    
    Args:
        image_pil: PIL Image from st.camera_input()
    
    Returns:
        dict with face_encoding, face_detected, num_faces
    """
    try:
        image_array = np.array(image_pil)
        
        # Upgrade: Apply lighting normalization
        image_array = enhance_lighting(image_array)
        
        # Find all faces
        face_locations = face_recognition.face_locations(image_array, model=MODEL)
        
        num_faces = len(face_locations)
        
        if num_faces == 0:
            return {
                'face_encoding': None,
                'face_detected': False,
                'num_faces': 0,
                'message': 'No face detected. Please try again.'
            }
        
        if num_faces > 1:
            return {
                'face_encoding': None,
                'face_detected': False,
                'num_faces': num_faces,
                'message': f'Multiple faces detected ({num_faces}). Show only your face.'
            }
        
        # Upgrade: Extract robust encoding for verification
        face_encodings = face_recognition.face_encodings(
            image_array, 
            face_locations,
            num_jitters=NUM_JITTERS
        )
        
        if len(face_encodings) == 0:
            return {
                'face_encoding': None,
                'face_detected': False,
                'num_faces': 1,
                'message': 'Face detected but could not extract features. Try again.'
            }
        
        return {
            'face_encoding': face_encodings[0],
            'face_detected': True,
            'num_faces': 1,
            'message': 'Face captured successfully!'
        }
    
    except Exception as e:
        return {
            'face_encoding': None,
            'face_detected': False,
            'num_faces': 0,
            'message': f'Error processing image: {e}'
        }
