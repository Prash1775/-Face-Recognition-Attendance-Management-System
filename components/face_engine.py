import numpy as np
import streamlit as st

# === CONFIGURATION ===
# Cosine similarity threshold for face matching (range 0.0-1.0, higher = stricter)
TOLERANCE = 0.97

# =========================================================================
# FAST MediaPipe-based face mesh model (cached in RAM after first load)
# MediaPipe runs in ~10ms on any CPU. dlib ResNet takes 30-120s on Streamlit
# Cloud's throttled shared CPU. This cache ensures models load only ONCE.
# =========================================================================

@st.cache_resource
def _load_mediapipe_face_mesh():
    """Cache MediaPipe FaceMesh solution in RAM (loads once per container)."""
    from mediapipe.python.solutions import face_mesh  # noqa: PLC0415
    return face_mesh


@st.cache_resource
def _load_mediapipe_face_detection():
    """Cache MediaPipe FaceDetection solution in RAM (loads once per container)."""
    from mediapipe.python.solutions import face_detection  # noqa: PLC0415
    return face_detection


def _encode_with_mediapipe(image_array):
    """
    Internal helper: extract 936-d normalized landmark encoding via MediaPipe Face Mesh.
    Returns numpy array or None if no face / multiple faces detected.
    """
    # --- Extract precise landmarks with FaceMesh directly ---
    mp_face_mesh = _load_mediapipe_face_mesh()
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,       # Single image — no tracking
        max_num_faces=2,              # Detect up to 2 faces to verify uniqueness
        refine_landmarks=False,
        min_detection_confidence=0.1,  # Ultra-permissive confidence threshold for home lighting
    ) as face_mesh:
        results = face_mesh.process(image_array)

    if not results.multi_face_landmarks:
        return None

    if len(results.multi_face_landmarks) > 1:
        # Multiple faces detected — reject for security (prevent proxy attendance)
        return None

    landmarks = results.multi_face_landmarks[0]

    # Extract x, y coordinates for all 468 landmarks → 936-d vector
    coords = []
    for lm in landmarks.landmark:
        coords.extend([lm.x, lm.y])

    encoding = np.array(coords, dtype=np.float64)

    # Normalize: zero-mean and unit-std for pose/scale invariance
    encoding = (encoding - encoding.mean()) / (encoding.std() + 1e-8)
    return encoding


def extract_face_encoding(image_pil):
    """
    Extract face encoding from a PIL Image.

    Primary: MediaPipe Face Mesh — 936-d normalized landmark vector (~10ms).
    Fallback: Disabled on Streamlit Cloud (HOG hangs for minutes due to CPU limits).

    Args:
        image_pil: PIL Image object (any mode; converted to RGB internally)

    Returns:
        numpy.ndarray or None if no face detected
    """
    errors = []
    st.session_state["face_diagnostic_errors"] = errors
    try:
        # Force PIL to fully decode the image
        pil_rgb = image_pil.convert("RGB")
        pil_rgb.load()  # Forces actual JPEG/PNG decode into memory

        # Create a contiguous writable uint8 array (required by MediaPipe)
        image_array = np.ascontiguousarray(pil_rgb, dtype=np.uint8)

        # --- PRIMARY: MediaPipe (fast) ---
        try:
            encoding = _encode_with_mediapipe(image_array)
            if encoding is not None:
                return encoding
            else:
                errors.append("MediaPipe: No face detected or multiple faces found.")
        except Exception as mp_err:
            errors.append(f"MediaPipe failed: {mp_err}")

        # --- FALLBACK: dlib HOG (Disabled to prevent multi-minute CPU hangs) ---
        errors.append("dlib HOG fallback skipped (disabled on cloud to prevent container hang).")

        return None

    except Exception as e:
        errors.append(f"General encoding error: {e}")
        print(f"Error in extract_face_encoding: {e}")
        return None


def verify_face(stored_encoding, capture_encoding, tolerance=TOLERANCE):
    """
    Verify if two face encodings belong to the same person using cosine similarity.

    Compatible with both MediaPipe (936-d) and dlib (128-d normalized) encodings.
    Cosine similarity: 1.0 = identical vectors, ~0.97+ = same person.

    Args:
        stored_encoding:  numpy array loaded from the database
        capture_encoding: numpy array from the current camera capture
        tolerance:        minimum similarity to accept as a match (default 0.97)

    Returns:
        bool: True if faces match, False otherwise
    """
    try:
        if stored_encoding is None or capture_encoding is None:
            return False

        stored = np.array(stored_encoding, dtype=np.float64)
        capture = np.array(capture_encoding, dtype=np.float64)

        # Dimension mismatch → encoding type changed (e.g. old dlib vs new MediaPipe)
        if stored.shape != capture.shape:
            print(
                f"Encoding dimension mismatch: "
                f"stored={stored.shape}, capture={capture.shape}. "
                "Student must re-register face."
            )
            return False

        # Cosine similarity
        dot = np.dot(stored, capture)
        norm_product = np.linalg.norm(stored) * np.linalg.norm(capture)
        similarity = dot / (norm_product + 1e-8)

        is_match = similarity >= tolerance

        print("-" * 45)
        print("FACE VERIFICATION METRICS")
        print(f"-> Engine: MediaPipe FaceMesh + Cosine Similarity")
        print(f"-> Similarity: {similarity:.4f}  (threshold: {tolerance})")
        print(f"-> Decision: {'APPROVED ✅' if is_match else 'REJECTED ❌'}")
        print("-" * 45)

        return is_match

    except Exception as e:
        print(f"Error in verify_face: {e}")
        return False


def compare_faces_batch(known_encodings, capture_encoding, tolerance=TOLERANCE):
    """
    Compare one face encoding against a list of known encodings.

    Args:
        known_encodings:  list of numpy arrays
        capture_encoding: numpy array
        tolerance:        cosine similarity threshold

    Returns:
        Tuple[list[bool], list[float]]: match results and distances (1 - similarity)
    """
    if not known_encodings or capture_encoding is None:
        return [], []

    capture = np.array(capture_encoding, dtype=np.float64)
    match_results = []
    distances = []

    for stored in known_encodings:
        try:
            s = np.array(stored, dtype=np.float64)
            if s.shape != capture.shape:
                match_results.append(False)
                distances.append(1.0)
                continue
            dot = np.dot(s, capture)
            norm_product = np.linalg.norm(s) * np.linalg.norm(capture)
            similarity = dot / (norm_product + 1e-8)
            match_results.append(similarity >= tolerance)
            distances.append(float(1.0 - similarity))
        except Exception:
            match_results.append(False)
            distances.append(1.0)

    return match_results, distances


def process_camera_frame(image_pil):
    """
    Detect faces in a camera frame and return encoding + metadata.

    Args:
        image_pil: PIL Image from st.camera_input()

    Returns:
        dict with keys: face_encoding, face_detected, num_faces, message
    """
    try:
        pil_rgb = image_pil.convert("RGB")
        pil_rgb.load()  # Force decode
        image_array = np.ascontiguousarray(pil_rgb, dtype=np.uint8)

        mp_face_detection = _load_mediapipe_face_detection()
        with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.2
        ) as face_detector:
            detection_results = face_detector.process(image_array)

        num_faces = (
            len(detection_results.detections) if detection_results.detections else 0
        )

        if num_faces == 0:
            return {
                "face_encoding": None,
                "face_detected": False,
                "num_faces": 0,
                "message": "No face detected. Please try again.",
            }

        if num_faces > 1:
            return {
                "face_encoding": None,
                "face_detected": False,
                "num_faces": num_faces,
                "message": f"Multiple faces detected ({num_faces}). Show only your face.",
            }

        # Single face — extract encoding
        encoding = extract_face_encoding(image_pil)
        if encoding is None:
            return {
                "face_encoding": None,
                "face_detected": False,
                "num_faces": 1,
                "message": "Face detected but encoding failed. Try again.",
            }

        return {
            "face_encoding": encoding,
            "face_detected": True,
            "num_faces": 1,
            "message": "Face captured successfully!",
        }

    except Exception as e:
        return {
            "face_encoding": None,
            "face_detected": False,
            "num_faces": 0,
            "message": f"Error: {e}",
        }
