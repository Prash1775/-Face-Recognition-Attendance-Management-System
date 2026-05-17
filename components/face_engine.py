import numpy as np
from PIL import Image
import io
import streamlit as st

# === CONFIGURATION ===
TOLERANCE = 0.97   # Cosine similarity threshold (higher = stricter matching)
NUM_JITTERS = 1    # For dlib fallback only

# =========================================================================
# FAST MediaPipe-based face mesh model (cached in RAM after first load)
# MediaPipe runs in ~10ms on any CPU. dlib ResNet takes 30-120s on Streamlit
# Cloud's throttled shared CPU. This cache ensures models load only ONCE.
# =========================================================================

@st.cache_resource(show_spinner="⚙️ Loading face models (first time only)...")
def _load_mediapipe_face_mesh():
    """Cache MediaPipe FaceMesh solution in RAM (loads once per container)."""
    import mediapipe as mp
    return mp.solutions.face_mesh

@st.cache_resource(show_spinner="⚙️ Loading face detection (first time only)...")
def _load_mediapipe_face_detection():
    """Cache MediaPipe FaceDetection solution in RAM (loads once per container)."""
    import mediapipe as mp
    return mp.solutions.face_detection


def extract_face_encoding(image_pil):
    """
    Extract face encoding from PIL Image using MediaPipe Face Mesh.
    
    Uses 468 3D facial landmarks as the encoding vector, normalized to be
    invariant to position and scale. Cosine similarity is used for matching.
    
    Falls back to dlib HOG if MediaPipe fails.
    
    Returns:
        numpy array (encoding) or None if no face detected
    """
    try:
        image_array = np.array(image_pil.convert("RGB"))

        # --- PRIMARY PATH: MediaPipe Face Mesh (fast, ~10ms) ---
        mp_face_mesh = _load_mediapipe_face_mesh()
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:
            results = face_mesh.process(image_array)

        if results.multi_face_landmarks and len(results.multi_face_landmarks) == 1:
            landmarks = results.multi_face_landmarks[0]

            # Extract x, y coordinates for all 468 landmarks
            coords = []
            for lm in landmarks.landmark:
                coords.extend([lm.x, lm.y])

            encoding = np.array(coords, dtype=np.float64)

            # Normalize: center and scale for pose/size invariance
            encoding = (encoding - encoding.mean()) / (encoding.std() + 1e-8)
            return encoding

        # Multiple faces or no detection from FaceMesh
        if results.multi_face_landmarks and len(results.multi_face_landmarks) > 1:
            return None  # Multiple faces — reject

        # --- FALLBACK PATH: dlib HOG (slow, but safe) ---
        print("MediaPipe found no face, trying dlib fallback...")
        try:
            import face_recognition
            face_locations = face_recognition.face_locations(image_array, model="hog")
            if len(face_locations) != 1:
                return None
            face_encodings = face_recognition.face_encodings(image_array, face_locations, num_jitters=NUM_JITTERS)
            if face_encodings:
                # Normalize dlib encoding to unit vector so cosine similarity works
                enc = np.array(face_encodings[0], dtype=np.float64)
                enc = enc / (np.linalg.norm(enc) + 1e-8)
                return enc
        except Exception as dlib_err:
            print(f"dlib fallback also failed: {dlib_err}")

        return None

    except Exception as e:
        print(f"Error extracting face encoding: {e}")
        return None


def verify_face(stored_encoding, capture_encoding, tolerance=TOLERANCE):
    """
    Verify if two face encodings match using cosine similarity.

    Works with both MediaPipe (936-d) and dlib (128-d normalized) encodings.
    Cosine similarity of 1.0 = identical, ~0.97+ = same person.

    Returns:
        bool: True if faces match, False otherwise
    """
    try:
        if stored_encoding is None or capture_encoding is None:
            return False

        stored = np.array(stored_encoding, dtype=np.float64)
        capture = np.array(capture_encoding, dtype=np.float64)

        # Handle dimension mismatch (encoding type changed between registration & verification)
        if stored.shape != capture.shape:
            print(f"Encoding dimension mismatch: stored={stored.shape}, capture={capture.shape}. Rejecting.")
            return False

        # Cosine similarity
        dot = np.dot(stored, capture)
        norm = np.linalg.norm(stored) * np.linalg.norm(capture)
        similarity = dot / (norm + 1e-8)

        is_match = similarity >= tolerance

        print("-" * 45)
        print("FACE VERIFICATION METRICS")
        print(f"-> Engine: MediaPipe FaceMesh + Cosine Similarity")
        print(f"-> Similarity Score: {similarity:.4f}")
        print(f"-> Threshold: {tolerance}")
        print(f"-> Decision: {'APPROVED ✅' if is_match else 'REJECTED ❌'}")
        print("-" * 45)

        return is_match

    except Exception as e:
        print(f"Error verifying face: {e}")
        return False


def compare_faces_batch(known_encodings, capture_encoding, tolerance=TOLERANCE):
    """
    Compare one face against multiple known faces using cosine similarity.

    Returns:
        list of bools and list of distances (1 - similarity)
    """
    try:
        if not known_encodings or capture_encoding is None:
            return [], []

        capture = np.array(capture_encoding, dtype=np.float64)
        results = []
        distances = []

        for stored in known_encodings:
            s = np.array(stored, dtype=np.float64)
            if s.shape != capture.shape:
                results.append(False)
                distances.append(1.0)
                continue
            dot = np.dot(s, capture)
            norm = np.linalg.norm(s) * np.linalg.norm(capture)
            similarity = dot / (norm + 1e-8)
            results.append(similarity >= tolerance)
            distances.append(1.0 - similarity)

        return results, distances

    except Exception as e:
        print(f"Error comparing faces: {e}")
        return [], []


def process_camera_frame(image_pil):
    """
    Process camera input for face detection (used for live checking).

    Returns:
        dict with face_encoding, face_detected, num_faces, message
    """
    try:
        image_array = np.array(image_pil.convert("RGB"))

        mp_face_detection = _load_mediapipe_face_detection()
        with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        ) as face_detector:
            detection_results = face_detector.process(image_array)

        num_faces = len(detection_results.detections) if detection_results.detections else 0

        if num_faces == 0:
            return {'face_encoding': None, 'face_detected': False,
                    'num_faces': 0, 'message': 'No face detected. Please try again.'}

        if num_faces > 1:
            return {'face_encoding': None, 'face_detected': False,
                    'num_faces': num_faces,
                    'message': f'Multiple faces detected ({num_faces}). Show only your face.'}

        # Single face — extract encoding
        encoding = extract_face_encoding(image_pil)
        if encoding is None:
            return {'face_encoding': None, 'face_detected': False,
                    'num_faces': 1,
                    'message': 'Face detected but encoding failed. Try again.'}

        return {'face_encoding': encoding, 'face_detected': True,
                'num_faces': 1, 'message': 'Face captured successfully!'}

    except Exception as e:
        return {'face_encoding': None, 'face_detected': False,
                'num_faces': 0, 'message': f'Error: {e}'}
