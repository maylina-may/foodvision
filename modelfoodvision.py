from ultralytics import YOLO
import cv2
import numpy as np

# ==========================================
# LOAD MODEL YOLO
# ==========================================

model = YOLO("best.pt")

MIN_CONFIDENCE = 0.85

# ==========================================
# 10 KELAS MAKANAN 
# ==========================================
ALLOWED_CLASSES = {
    "ayam goreng",
    "mie ayam",
    "nasi putih",
    "pempek",
    "rendang",
    "sambal",
    "sate",
    "soto",
    "tahu goreng",
    "tempe goreng",
}


# ==========================================
# DETEKSI MAKANAN
# ==========================================

def detect_food(image):

    # agar warna tidak tertukar dan deteksi akurat.
    if image.ndim == 3 and image.shape[2] == 3:
        # Konversi RGB -> BGR agar YOLO menerima warna yang benar.
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = image

    # Predict dengan confidence sesuai default
    results = model.predict(
        source=image_bgr,
        conf=MIN_CONFIDENCE,
        imgsz=640,
        verbose=False
    )

    result = results[0]

    detected_objects = []

    # Gambar salinan dari gambar input (BGR) sebagai kanvas hasil deteksi
    output_image = image_bgr.copy()

    if result.boxes is not None:

        for box in result.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            class_id = int(box.cls[0])

            confidence = float(box.conf[0])

            food_name = model.names[class_id].strip()

            # ==========================================
            # FILTER 10 KELAS 
            # ==========================================
            
            if food_name not in ALLOWED_CLASSES:
                continue

            area = (x2 - x1) * (y2 - y1)

            detected_objects.append({

                "Nama": food_name,

                "Confidence": round(confidence, 4),

                "Confidence (%)": round(confidence * 100, 1),

                "Bounding Box": [x1, y1, x2, y2],

                "Luas (px²)": area

            })

            # ==========================================
            # GAMBAR BOUNDING BOX & LABEL
            # ==========================================

            # Warna box (pink tua) yang selaras dengan tema aplikasi
            box_color = (232, 93, 133)   # BGR untuk pink #E85D85
            text_color = (255, 255, 255)

            cv2.rectangle(
                output_image,
                (x1, y1),
                (x2, y2),
                box_color,
                thickness=3
            )

            # Label kelas + confidence
            label = f"{food_name} {confidence*100:.1f}%"

            # Ukuran teks untuk menentukan tinggi background label
            (tw, th), base = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )

            # Koordinat background label (di atas box)
            ty = y1 - th - 8
            if ty < 0:
                ty = y1 + 8

            cv2.rectangle(
                output_image,
                (x1, ty),
                (x1 + tw + 8, ty + th + 8),
                box_color,
                thickness=-1
            )

            cv2.putText(
                output_image,
                label,
                (x1 + 4, ty + th + 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                text_color,
                2,
                cv2.LINE_AA
            )

    # Urutkan dari confidence tertinggi ke terendah
    detected_objects.sort(
        key=lambda x: x["Confidence"],
        reverse=True
    )

    return output_image, detected_objects
