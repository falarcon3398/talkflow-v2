import sys
import os
import traceback
from os import listdir, path
import subprocess
import numpy as np
import cv2
import pickle
import torch
from tqdm import tqdm

# Import local face_detection (renamed to avoid conflict with pip package)
try:
    from face_detection_local import FaceAlignment as LocalFaceAlignment, LandmarksType as LocalLandmarksType
except ImportError:
    # Handle if called from parent directory
    try:
        from musetalk.utils.face_detection_local import FaceAlignment as LocalFaceAlignment, LandmarksType as LocalLandmarksType
    except ImportError:
        LocalFaceAlignment = None
        # print("Warning: Local face_detection_local not found.")

# Import pip face-alignment for landmarks using an alias
try:
    import face_alignment as fa_pkg
except ImportError:
    fa_pkg = None

# Import insightface as a fallback detector
try:
    import insightface
    from insightface.app import FaceAnalysis
except ImportError:
    insightface = None

# Global detector instances
fa_det = None
fa_landmarks = None
app_insight = None

def init_detectors():
    global fa_det, fa_landmarks, app_insight
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if fa_det is None and LocalFaceAlignment is not None:
        try:
            fa_det = LocalFaceAlignment(LocalLandmarksType._2D, flip_input=False, device=device)
        except Exception as e:
            print(f"Error initializing local face detector: {e}")

    if fa_landmarks is None and fa_pkg is not None:
        try:
            print("Initializing face-alignment landmark detector...")
            # Use proper LandmarkType from the package
            fa_landmarks = fa_pkg.FaceAlignment(fa_pkg.LandmarksType.TWO_D, flip_input=False, device=device)
        except Exception as e:
            print(f"Error initializing landmark detector: {e}")
            
    if app_insight is None and insightface is not None:
        try:
            print("Initializing insightface detector...")
            app_insight = FaceAnalysis(name='buffalov2', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            app_insight.prepare(ctx_id=0, det_size=(640, 640))
        except Exception as e:
            print(f"Error initializing insightface: {e}")

# maker if the bbox is not sufficient 
coord_placeholder = (0.0,0.0,0.0,0.0)

def resize_landmark(landmark, w, h, new_w, new_h):
    w_ratio = new_w / w
    h_ratio = new_h / h
    landmark_norm = landmark / [w, h]
    landmark_resized = landmark_norm * [new_w, new_h]
    return landmark_resized

def read_imgs(img_list):
    frames = []
    print('reading images...')
    for img_path in tqdm(img_list):
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Warning: could not read image {img_path}")
            continue
        frames.append(frame)
    return frames

def get_landmark_and_bbox(img_list, upperbondrange=0):
    global fa_landmarks, fa_det, app_insight
    init_detectors()
    
    frames = read_imgs(img_list)
    if not frames:
        return [], []
        
    batch_size_fa = 1
    batches = [frames[i:i + batch_size_fa] for i in range(0, len(frames), batch_size_fa)]
    coords_list = []
    
    if upperbondrange != 0:
        print('get key_landmark and face bounding boxes with the bbox_shift:', upperbondrange)
    else:
        print('get key_landmark and face bounding boxes with the default value')
        
    average_range_minus = []
    average_range_plus = []
    
    for fb in tqdm(batches):
        face_land_mark = None
        bbox = None
        img_bgr = fb[0]
        h, w = img_bgr.shape[:2]
        
        # 1. Try Landmarks (using pip face-alignment)
        if fa_landmarks is not None:
            try:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                preds = fa_landmarks.get_landmarks(img_rgb)
                if preds and len(preds) > 0:
                    face_land_mark = preds[0].astype(np.int32)
            except Exception:
                face_land_mark = None
        
        # 2. Try Bounding Boxes (local detector)
        if fa_det is not None:
            try:
                det_res = fa_det.get_detections_for_batch(np.asarray([img_bgr]))
                if det_res and det_res[0] is not None:
                    # fa_det returns a list of tuples, take the first one
                    bbox = det_res[0] 
            except Exception:
                pass
        
        # 3. Fallback to InsightFace if needed
        if (face_land_mark is None or bbox is None) and app_insight is not None:
            try:
                faces = app_insight.get(img_bgr)
                if faces:
                    face = faces[0]
                    if bbox is None:
                        x1, y1, x2, y2 = face.bbox.astype(int)
                        bbox = (x1, y1, x2, y2)
                    if face_land_mark is None:
                        # Insightface has 5 landmarks, we need 68 for the loop logic below.
                        # We'll just use the bbox to provide a dummy landmark for calculation if needed,
                        # OR we try harder. For now, let's just use the bbox.
                        kps = face.kps.astype(int)
                        # Create a mock 68-point set using bbox
                        x1, y1, x2, y2 = bbox
                        face_land_mark = np.zeros((68, 2), dtype=np.int32)
                        # We'll put something in indices 28, 29, 30 for the range logic
                        face_land_mark[28] = [ (x1+x2)//2, y1 + (y2-y1)//3 ]
                        face_land_mark[29] = [ (x1+x2)//2, y1 + (y2-y1)//2 ]
                        face_land_mark[30] = [ (x1+x2)//2, y1 + 2*(y2-y1)//3 ]
                        # Also bounds
                        face_land_mark[0] = [x1, y1]
                        face_land_mark[16] = [x2, y1]
                        face_land_mark[8] = [(x1+x2)//2, y2]
            except Exception as e:
                print(f"Insightface error: {e}")

        # Final Fallback: Entire image or Placeholder
        if bbox is None and face_land_mark is not None:
            x1, y1 = np.min(face_land_mark, axis=0)
            x2, y2 = np.max(face_land_mark, axis=0)
            bbox = (int(x1), int(y1), int(x2), int(y2))
        
        if bbox is None or face_land_mark is None:
            print("Warning: No face detected in frame. Using entire image as fallback.")
            bbox = (0, 0, w, h)
            face_land_mark = np.zeros((68, 2), dtype=np.int32)
            face_land_mark[28] = [w//2, h//3]
            face_land_mark[29] = [w//2, h//2]
            face_land_mark[30] = [w//2, 2*h//3]
            # Dummy bounds for landmarks
            face_land_mark[:, 0] = np.clip(face_land_mark[:, 0], 0, w)
            face_land_mark[:, 1] = np.clip(face_land_mark[:, 1], 0, h)

        # Proceed with MuseTalk range logic
        try:
            half_face_coord = face_land_mark[29].copy()
            range_minus = (face_land_mark[30] - face_land_mark[29])[1]
            range_plus = (face_land_mark[29] - face_land_mark[28])[1]
            average_range_minus.append(range_minus)
            average_range_plus.append(range_plus)
            
            if upperbondrange != 0:
                half_face_coord[1] = upperbondrange + half_face_coord[1]
                
            half_face_dist = np.max(face_land_mark[:, 1]) - half_face_coord[1]
            min_upper_bond = 0
            upper_bond = max(min_upper_bond, half_face_coord[1] - half_face_dist)
            
            f_landmark = (
                max(0, np.min(face_land_mark[:, 0])), 
                int(max(0, upper_bond)), 
                min(w, np.max(face_land_mark[:, 0])), 
                min(h, np.max(face_land_mark[:, 1]))
            )
            x1, y1, x2, y2 = f_landmark
            
            if y2 - y1 <= 10 or x2 - x1 <= 10: 
                coords_list += [bbox]
            else:
                coords_list += [f_landmark]
        except Exception as e:
            print(f"Error in range logic: {e}")
            coords_list += [bbox]
    
    print("********************************************bbox_shift parameter adjustment**********************************************************")
    if average_range_minus and average_range_plus:
        print(f"Total frame:「{len(frames)}」 Manually adjust range : [ -{int(sum(average_range_minus) / len(average_range_minus))}~{int(sum(average_range_plus) / len(average_range_plus))} ] , the current value: {upperbondrange}")
    else:
        print(f"Total frame:「{len(frames)}」 No faces detected for range adjustment analysis.")
    print("*************************************************************************************************************************************")
    return coords_list, frames

if __name__ == "__main__":
    img_list = ["./results/lyria/00000.png","./results/lyria/00001.png","./results/lyria/00002.png","./results/lyria/00003.png"]
    crop_coord_path = "./coord_face.pkl"
    coords_list, full_frames = get_landmark_and_bbox(img_list)
    with open(crop_coord_path, 'wb') as f:
        pickle.dump(coords_list, f)
    print(coords_list)
