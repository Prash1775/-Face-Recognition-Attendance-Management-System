import cv2
import numpy as np
mp_hands = None
hands_detector = None

def _get_hands_detector():
    global mp_hands, hands_detector
    if hands_detector is None:
        import mediapipe as mp
        mp_hands = mp.solutions.hands
        hands_detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
    return hands_detector, mp_hands

def generate_liveness_challenge():
    import random
    """Generates a random finger count challenge (1 to 4 fingers)"""
    return random.randint(1, 4)

def count_fingers(image_array):
    """
    Uses MediaPipe to count the number of raised main fingers in the image.
    Ignoring the thumb for simplicity to avoid handedness bugs.
    Returns the finger count (0 to 4), or -1 if no hand detected.
    """
    # Ensure image is in RGB format for MediaPipe
    if image_array.dtype != np.uint8:
        image_array = image_array.astype(np.uint8)
        
    detector, mp_h = _get_hands_detector()
    results = detector.process(image_array)

    if not results.multi_hand_landmarks:
        return -1  # No hand found in the image

    hand_landmarks = results.multi_hand_landmarks[0]
    
    fingers = []

    # Core fingers: Index, Middle, Ring, Pinky
    tip_ids = [
        mp_h.HandLandmark.INDEX_FINGER_TIP,
        mp_h.HandLandmark.MIDDLE_FINGER_TIP,
        mp_h.HandLandmark.RING_FINGER_TIP,
        mp_h.HandLandmark.PINKY_TIP
    ]
    
    compare_ids = [
        mp_h.HandLandmark.INDEX_FINGER_PIP,
        mp_h.HandLandmark.MIDDLE_FINGER_PIP,
        mp_h.HandLandmark.RING_FINGER_PIP,
        mp_h.HandLandmark.PINKY_PIP
    ]
    
    # For standard fingers, if the Tip y-coordinate is lower than the PIP y-coordinate,
    # it means the finger is extended upwards. (Y goes down in image coordinates)
    for i in range(4):
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[compare_ids[i]].y:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return sum(fingers)
