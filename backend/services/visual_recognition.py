import cv2
import numpy as np
import os
import glob

# Directory where we store pre-computed descriptors
DESCRIPTOR_DIR = "media/descriptors"

def ensure_descriptor_dir():
    if not os.path.exists(DESCRIPTOR_DIR):
        os.makedirs(DESCRIPTOR_DIR)

def extract_and_save_features(image_bytes: bytes, capsule_id: int):
    """
    Extracts ORB features from an image and saves them to disk.
    """
    try:
        ensure_descriptor_dir()
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return False

        # Initialize ORB detector
        orb = cv2.ORB_create(nfeatures=500)
        
        # Find the keypoints and descriptors
        kp, des = orb.detectAndCompute(img, None)
        
        if des is not None:
            # Save descriptors as .npy file
            save_path = os.path.join(DESCRIPTOR_DIR, f"{capsule_id}.npy")
            np.save(save_path, des)
            return True
    except Exception as e:
        print(f"Feature extraction failed: {e}")
    return False

def find_best_match(query_image_bytes: bytes):
    """
    Matches the query image against all stored descriptors using ORB.
    Returns the capsule_id of the best match, or None if no good match found.
    """
    try:
        # Convert query bytes to image
        nparr = np.frombuffer(query_image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return None

        # Extract features from query image
        orb = cv2.ORB_create(nfeatures=500)
        kp_q, des_q = orb.detectAndCompute(img, None)
        
        if des_q is None:
            return None

        # BFMatcher with Hamming distance
        # crossCheck=True is incompatible with knnMatch
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        
        best_match_id = None
        max_matches = 0
        
        # Iterate over all stored descriptor files
        descriptor_files = glob.glob(os.path.join(DESCRIPTOR_DIR, "*.npy"))
        
        for file_path in descriptor_files:
            try:
                # Load stored descriptors
                des_db = np.load(file_path)
                
                if des_db is None or len(des_db) < 2:
                    continue
                
                # Match descriptors
                # Use KNN matching for ratio test
                matches_knn = bf.knnMatch(des_q, des_db, k=2)
                
                good_matches = []
                for m_n in matches_knn:
                    if len(m_n) == 2:
                        m, n = m_n
                        if m.distance < 0.75 * n.distance:
                            good_matches.append(m)
                
                num_good_matches = len(good_matches)
                
                # Threshold for considering it a "match" (adjust based on testing)
                # Increased threshold to avoid false positives (e.g. unknown numbers)
                if num_good_matches > 15 and num_good_matches > max_matches:
                    max_matches = num_good_matches
                    # Filename is capsule_id.npy
                    best_match_id = int(os.path.basename(file_path).split('.')[0])
            except:
                continue
                
        return best_match_id

    except Exception as e:
        print(f"Matching failed: {e}")
        return None
