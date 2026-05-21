import sys
import os
from PIL import Image

# Add root folder to python path
sys.path.append(os.path.abspath("."))

from components import face_engine

def run_test():
    print("Starting face engine test...")
    ref_path = "reference.jpg"
    if not os.path.exists(ref_path):
        print(f"Error: {ref_path} not found.")
        return

    try:
        img = Image.open(ref_path)
        print(f"Loaded image: {img.size}, format: {img.format}")
        
        # Test extract_face_encoding
        encoding = face_engine.extract_face_encoding(img)
        
        if encoding is not None:
            print("SUCCESS! Face encoding extracted successfully.")
            print(f"Encoding shape: {encoding.shape}")
            print(f"First 10 values: {encoding[:10]}")
        else:
            print("FAILURE: face_engine returned None.")
            try:
                errs = face_engine.st.session_state.get("face_diagnostic_errors", [])
                print("Diagnostic Errors:", errs)
            except Exception as se:
                print("Could not fetch session state errors:", se)
            
    except Exception as e:
        print(f"Exception during test: {e}")

if __name__ == "__main__":
    run_test()
