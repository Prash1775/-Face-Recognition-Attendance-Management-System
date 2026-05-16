import glob
from PIL import Image
from components.face_engine import verify_face, extract_face_encoding
import json

def get_metrics():
    try:
        ref_img = Image.open('reference.jpg')
        ref_encoding = extract_face_encoding(ref_img)
    except:
        return {"error": "Missing or corrupt reference.jpg"}

    TP, FN, TN, FP = 0, 0, 0, 0

    for idx, path in enumerate(glob.glob("dataset/positive/*.*")):
        try:
            enc = extract_face_encoding(Image.open(path))
            if enc is not None:
                if verify_face(ref_encoding, enc):
                    TP += 1
                else:
                    FN += 1
        except: pass

    for idx, path in enumerate(glob.glob("dataset/negative/*.*")):
        try:
            enc = extract_face_encoding(Image.open(path))
            if enc is not None:
                if not verify_face(ref_encoding, enc):
                    TN += 1
                else:
                    FP += 1
        except: pass

    total = TP + TN + FP + FN
    acc = (TP + TN) / total if total > 0 else 0
    prec = TP / (TP + FP) if (TP + FP) > 0 else 0
    rec = TP / (TP + FN) if (TP + FN) > 0 else 0
    
    print(json.dumps({
        "TP": TP, "TN": TN, "FP": FP, "FN": FN, "Total": total,
        "Accuracy": round(acc*100, 2), "Precision": round(prec*100, 2), "Recall": round(rec*100, 2)
    }))

get_metrics()
