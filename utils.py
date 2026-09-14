import math
import cv2
import numpy as np

LOCATIONS = {
    "SVIST Campus (Tiruvuru)": {"lat": 17.1185, "lon": 80.6078},
    "Bhattuvarigudem Spot (Eluru Dist)": {"lat": 17.1725, "lon": 80.9850}
}

ALLOWED_RADIUS_METERS = 150.0

def calculate_haversine_distance(user_lat: float, user_lon: float, target_lat: float, target_lon: float) -> float:
    R = 6371000.0
    phi1 = math.radians(target_lat)
    phi2 = math.radians(user_lat)
    delta_phi = math.radians(user_lat - target_lat)
    delta_lambda = math.radians(user_lon - target_lon)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def verify_location_range(user_lat: float, user_lon: float, selected_location: str = None) -> tuple[bool, float, str]:
    if selected_location and selected_location in LOCATIONS:
        target = LOCATIONS[selected_location]
        dist = calculate_haversine_distance(user_lat, user_lon, target["lat"], target["lon"])
        if dist <= ALLOWED_RADIUS_METERS:
            return True, dist, selected_location
    
    for name, coords in LOCATIONS.items():
        dist = calculate_haversine_distance(user_lat, user_lon, coords["lat"], coords["lon"])
        if dist <= ALLOWED_RADIUS_METERS:
            return True, dist, name
            
    d_campus = calculate_haversine_distance(user_lat, user_lon, LOCATIONS["SVIST Campus (Tiruvuru)"]["lat"], LOCATIONS["SVIST Campus (Tiruvuru)"]["lon"])
    d_bhattu = calculate_haversine_distance(user_lat, user_lon, LOCATIONS["Bhattuvarigudem Spot (Eluru Dist)"]["lat"], LOCATIONS["Bhattuvarigudem Spot (Eluru Dist)"]["lon"])
    
    if d_bhattu <= d_campus:
        return False, d_bhattu, "Bhattuvarigudem Spot (Eluru Dist)"
    else:
        return False, d_campus, "SVIST Campus (Tiruvuru)"

def extract_face_histogram(img_bytes):
    if img_bytes is None:
        return None
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Safe Cascade Classifier Loading
    if hasattr(cv2, 'CascadeClassifier'):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            return None
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
    else:
        face_roi = gray

    hist = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return hist

def compare_faces(registered_img_bytes, live_img_bytes, match_threshold=0.60) -> tuple[bool, str]:
    if registered_img_bytes is None or live_img_bytes is None:
        return False, "Missing image source for verification."

    reg_hist = extract_face_histogram(registered_img_bytes)
    live_hist = extract_face_histogram(live_img_bytes)

    if reg_hist is None or live_hist is None:
        return False, "Clear face not detected in camera feed."

    similarity = cv2.compareHist(reg_hist, live_hist, cv2.HISTCMP_CORREL)

    if similarity >= match_threshold:
        return True, f"Face Matched ({similarity*100:.1f}% Match Confidence)"
    else:
        return False, f"Face Mismatch ({similarity*100:.1f}% Confidence)"