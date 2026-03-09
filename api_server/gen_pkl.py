import cv2
import pickle
import sys
import os

def generate_synthetic_pkl(image_path, output_pkl_path):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error loading {image_path}")
        return False
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Load Haar cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        print(f"No faces found in {image_path}. Using fallback.")
        h, w = img.shape[:2]
        s = min(w, h) // 2
        x1, y1 = (w - s) // 2, (h - s) // 2
        faces = [[x1, y1, s, s]]
        
    x, y, w, h = faces[0]
    
    # Expand box slightly
    expand = 0.2
    x1 = max(0, int(x - w * expand))
    y1 = max(0, int(y - h * expand))
    x2 = min(img.shape[1], int(x + w * (1 + expand)))
    y2 = min(img.shape[0], int(y + h * (1 + expand)))
    
    bbox = [x1, y1, x2, y2]
    print(f"Detected expanded bbox: {bbox}")
    
    coord_list = [bbox]
    
    with open(output_pkl_path, 'wb') as f:
        pickle.dump(coord_list, f)
        
    print(f"Saved to {output_pkl_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gen_pkl.py <input_img> <output_pkl>")
        sys.exit(1)
    
    generate_synthetic_pkl(sys.argv[1], sys.argv[2])
