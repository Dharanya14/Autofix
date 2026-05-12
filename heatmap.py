# heatmap.py

import os
import cv2
import numpy as np
from ultralytics import RTDETR

# Load the model once globally
model = RTDETR(r"D:\autofix\autofix\model\best.pt")

def generate_heatmap(image_path):
    # Predict Damaged Areas
    results = model.predict(source=image_path, save=False)

    # Load Original Image
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Initialize Heatmap (Zero Matrix)
    heatmap = np.zeros((height, width), dtype=np.float32)

    # Process Detected Objects and Generate Heatmap
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            confidence = box.conf[0].item()  # Confidence score (0 to 1)
            intensity = int(confidence * 255)
            cv2.rectangle(heatmap, (x1, y1), (x2, y2), intensity, thickness=-1)

    # Blur, Normalize, and Apply Colormap
    heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
    heatmap = np.uint8(255 * (heatmap / np.max(heatmap))) if np.max(heatmap) > 0 else np.zeros_like(heatmap, dtype=np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Overlay Heatmap on Original Image
    overlayed_image = cv2.addWeighted(image, 0.6, heatmap_colored, 0.4, 0)

    # Save to static folder
    output_folder = os.path.join("static", "heatmaps")
    os.makedirs(output_folder, exist_ok=True)
    output_filename = "heatmap.jpg"
    output_path = os.path.join(output_folder, output_filename)
    cv2.imwrite(output_path, overlayed_image)

    return output_filename




