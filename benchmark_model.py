import os
import glob
from PIL import Image
from components.face_engine import verify_face, extract_face_encoding

def calculate_metrics(reference_image_path, positive_folder, negative_folder):
    print("Loading Baseline Reference Face...")
    try:
         ref_img = Image.open(reference_image_path)
         ref_encoding = extract_face_encoding(ref_img)
    except Exception as e:
         print(f"Could not load reference image: {e}")
         return

    if ref_encoding is None:
        print("ERROR: No face found in the standard reference image!")
        return

    # Confusion Matrix Trackers
    TP = 0 # True Positive (Correctly identified YOU)
    FN = 0 # False Negative (Failed to recognize YOU)
    TN = 0 # True Negative (Correctly rejected ANOTHER person)
    FP = 0 # False Positive (Incorrectly approved ANOTHER person)

    print(f"Scanning Positive Matches ('True' Dataset) from {positive_folder}...")
    for img_path in glob.glob(f"{positive_folder}/*.*"):
        try:
            img = Image.open(img_path)
            enc = extract_face_encoding(img)
            if enc is not None:
                match = verify_face(ref_encoding, enc)
                if match:
                    TP += 1
                else:
                    FN += 1
        except Exception:
            pass

    print(f"Scanning Negative Matches ('False' Dataset) from {negative_folder}...")
    for img_path in glob.glob(f"{negative_folder}/*.*"):
        try:
            img = Image.open(img_path)
            enc = extract_face_encoding(img)
            if enc is not None:
                match = verify_face(ref_encoding, enc)
                if not match:
                    TN += 1
                else:
                    FP += 1
        except Exception as e:
            pass

    # Safety Check
    total = TP + TN + FP + FN
    if total == 0:
         print("\n⚠️ No valid images were tested. Please add images to the positive and negative folders.")
         return

    # Mathematical Calcuations
    accuracy = (TP + TN) / total if total > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n" + "="*45)
    print("AI MODEL CONFUSION MATRIX & METRICS")
    print(f"Total Dataset Images Processed: {total}")
    print(f"True Positives (TP) : {TP}")
    print(f"True Negatives (TN) : {TN}")
    print(f"False Positives (FP): {FP} (CRITICAL ERROR)")
    print(f"False Negatives (FN): {FN}")
    print("-" * 45)
    print(f"Accuracy  : {accuracy * 100:.2f}%  (Overall correctness)")
    print(f"Precision : {precision * 100:.2f}%  (When it says 'Match', how right is it?)")
    print(f"Recall    : {recall * 100:.2f}%  (How many total true matches did it catch?)")
    print(f"F1 Score  : {f1_score * 100:.2f}%  (Harmonic Mean)")
    print("="*45)

if __name__ == "__main__":
    if not os.path.exists("dataset/positive"): os.makedirs("dataset/positive")
    if not os.path.exists("dataset/negative"): os.makedirs("dataset/negative")
    
    print("To test your system:")
    print("1. Place ONE clear picture of your face named 'reference.jpg' in this folder.")
    print("2. Put 10-20 different photos of your face in the 'dataset/positive' folder.")
    print("3. Put 10-20 photos of DIFFERENT people in the 'dataset/negative' folder.")
    print("4. Re-run this script!\n")
    
    if os.path.exists("reference.jpg"):
        calculate_metrics("reference.jpg", "dataset/positive", "dataset/negative")
    else:
        print("Waiting for reference.jpg...")
