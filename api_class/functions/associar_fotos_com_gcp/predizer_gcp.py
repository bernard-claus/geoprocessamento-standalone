import cv2
import numpy as np
import os


# -------------------------------------------------------------
# Helpers
# -------------------------------------------------------------

orb = cv2.ORB_create(4000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)


def extract_template(img, point, size=100):
    """Extract square patch around a clicked point."""
    x, y = point
    x = int(x)
    y = int(y)
    return img[y-size:y+size, x-size:x+size]


def get_features(img):
    """Compute ORB features for an image."""
    return orb.detectAndCompute(img, None)


def refine_match(img, template, predicted, window=120):
    """Refine predicted location using template matching."""
    x, y = int(predicted[0]), int(predicted[1])
    h, w = template.shape[:2]

    y1 = max(0, y - window)
    y2 = min(img.shape[0], y + window + h)
    x1 = max(0, x - window)
    x2 = min(img.shape[1], x + window + w)

    search = img[y1:y2, x1:x2]
    if search.size == 0:
        return None

    # Check if search region is large enough for template matching
    search_h, search_w = search.shape[:2]
    if search_h < h or search_w < w:
        print(f"Search region ({search_w}x{search_h}) is smaller than template ({w}x{h}), skipping refinement")
        return None

    result = cv2.matchTemplate(search, template, cv2.TM_CCORR_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    fx = x1 + max_loc[0] + w // 2
    fy = y1 + max_loc[1] + h // 2

    return (fx, fy, float(max_val))  # include match score


# -------------------------------------------------------------
# Main function (your signature)
# -------------------------------------------------------------

def predizer_gcp(fotos, caminho, pto_controle_nome, relative_positions, fotos_referencia):
    """
    fotos: list of all filenames to process (JPG, PNG…)
    caminho: folder path containing all files
    pto_controle_nome: string, name of the control point
    relative_positions: dict { 'IMG_A.JPG': (x, y), ... }
    fotos_referencia: list of filenames that have user-clicked points
    """

    print(f"Processing control point: {pto_controle_nome}")
    print("Reference images:", fotos_referencia)

    # ---------------------------------------------------------
    # Load reference images + features + templates
    # ---------------------------------------------------------
    referencia_data = []  # each = dict with {img, kp, des, template, filename}

    for ref_file in fotos_referencia:
        path = os.path.join(caminho, ref_file)
        img = cv2.imread(path)

        if img is None:
            print("Could not load:", path)
            continue

        if ref_file not in relative_positions:
            print(f"Missing relative position for {ref_file}")
            continue

        click_pt = (relative_positions[ref_file]['relX'], relative_positions[ref_file]['relY'])

        kp, des = get_features(img)
        template = extract_template(img, click_pt)

        referencia_data.append({
            "filename": ref_file,
            "img": img,
            "kp": kp,
            "des": des,
            "template": template,
            "point": click_pt
        })

    if len(referencia_data) == 0:
        print("No valid reference images provided.")
        return {}

    # ---------------------------------------------------------
    # Process all target images
    # ---------------------------------------------------------
    results = {}

    for foto in fotos:
        img_path = os.path.join(caminho, foto)
        img = cv2.imread(img_path)

        if img is None:
            print("Could not load:", img_path)
            continue

        best_candidate = None
        best_score = -1

        # -----------------------------------------------------
        # Try matching against every reference image
        # -----------------------------------------------------
        for ref in referencia_data:
            kp1, des1 = ref["kp"], ref["des"]
            template = ref["template"]
            ref_point = ref["point"]

            kp2, des2 = get_features(img)

            if des2 is None or des1 is None:
                continue

            matches = bf.match(des1, des2)
            if len(matches) < 10:
                continue

            matches = sorted(matches, key=lambda x: x.distance)
            src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

            H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)
            if H is None:
                continue

            # Predict point location
            ref_pt_arr = np.array([[ref_point]], dtype="float32")
            predicted = cv2.perspectiveTransform(ref_pt_arr, H)[0][0]

            # Refine using template matching
            refined = refine_match(img, template, predicted)
            if refined is None:
                continue

            (fx, fy, score) = refined

            if score > best_score:
                best_score = score
                best_candidate = (fx, fy)

        results[foto] = {
            "bestPoint": best_candidate,
            "score": best_score
        }

    return results
