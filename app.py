import streamlit as st
import pandas as pd
from database import USERS, ACTIVE_DRIVES, ATTENDANCE_LOGS, APPLICATIONS_LOG, BRANCH_OPTIONS
from utils import verify_location_range, LOCATIONS, ALLOWED_RADIUS_METERS, compare_faces
from streamlit_js_eval import get_geolocation
import numpy as np
import cv2
import hashlib
import base64
from datetime import datetime


# =============================================================================
# FACE RECOGNITION SETUP - InsightFace Professional FRS
# =============================================================================

# Try to import InsightFace for professional face recognition
try:
    import insightface
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    FACE_RECOGNITION_AVAILABLE = True
except Exception as e:
    FACE_RECOGNITION_AVAILABLE = False
    print(f"Face recognition not available: {e}")


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="SVIST | Placement & Smart Biometric Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# OPTIMIZED CSS STYLING - NO BRIGHTNESS FLICKER, SIDEBAR WHITE TEXT
# =============================================================================
st.markdown("""
    <style>
        /* Main App Background - Royal Blue Gradient */
        .stApp {
            background: linear-gradient(135deg, #020617 0%, #0b192c 40%, #1e3a8a 100%);
            color: #ffffff;
        }

        /* Header Banner - Subtle Animation (No Flicker) */
        .royal-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            background: linear-gradient(90deg, #1e3a8a 0%, #0369a1 50%, #1e3a8a 100%);
            border: 2px solid #38bdf8;
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.4);
            padding: 20px 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            animation: gentle-glow 4s ease-in-out infinite alternate;
        }

        @keyframes gentle-glow {
            0% { box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3); }
            100% { box-shadow: 0 4px 25px rgba(56, 189, 248, 0.5); }
        }

        /* College Logo - Gentle Float Animation */
        .college-logo-img {
            width: 85px;
            height: 85px;
            border-radius: 50%;
            border: 3px solid #38bdf8;
            background-color: #ffffff;
            padding: 4px;
            object-fit: contain;
            animation: gentle-float 4s ease-in-out infinite;
        }

        @keyframes gentle-float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-3px); }
        }

        /* Header Text Styling */
        .header-title-text {
            color: #ffffff !important;
            font-size: 26px;
            font-weight: 800;
            margin: 0;
            text-shadow: 0 0 10px rgba(255,255,255,0.5);
            letter-spacing: 0.8px;
        }

        .header-sub-text {
            color: #7dd3fc !important;
            font-size: 14px;
            margin-top: 5px;
            font-weight: 500;
        }

        /* Placement Card - Smooth Hover */
        .placement-card {
            background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
            border: 1.5px solid #0284c7;
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .placement-card:hover {
            transform: translateY(-5px);
            border-color: #38bdf8;
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5);
        }

        /* Student Image Frame */
        .student-img-frame {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 3px solid #38bdf8;
            object-fit: cover;
            margin: 0 auto 10px auto;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }

        .student-name-text {
            font-size: 17px;
            font-weight: 700;
            color: #ffffff !important;
            margin-top: 6px;
        }

        .roll-text {
            font-size: 12px;
            color: #94a3b8 !important;
        }

        .company-badge {
            font-size: 14px;
            font-weight: 700;
            color: #38bdf8 !important;
            margin-top: 6px;
        }

        .package-badge {
            font-size: 13px;
            color: #4ade80 !important;
            font-weight: 700;
            margin-top: 2px;
        }

        /* Statistics Card */
        .stat-card {
            background: linear-gradient(135deg, #1e3a8a 0%, #0369a1 100%);
            border: 1px solid #38bdf8;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            color: white;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
        }

        /* =================================================================
        SIDEBAR STYLING - WHITE TEXT ON DARK BACKGROUND
        ================================================================= */
        .stSidebar {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff !important;
        }
        
        .stSidebar * {
            color: #ffffff !important;
        }
        
        .stSidebar label {
            color: #ffffff !important;
        }
        
        .stSidebar p {
            color: #ffffff !important;
        }
        
        .stSidebar span {
            color: #ffffff !important;
        }
        
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #ffffff !important;
        }
        
        .stCheckbox label {
            color: #ffffff !important;
        }
        
        .stSlider label {
            color: #ffffff !important;
        }
        
        .stButton > label {
            color: #ffffff !important;
        }

        /* Global Text Color */
        p, span, label, h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }

        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #1e3a8a 0%, #0369a1 100%);
            color: #ffffff !important;
            border: 1px solid #38bdf8;
        }

        /* Input Fields */
        .stTextInput > div > div > input {
            background-color: #1e293b;
            color: #ffffff !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "role" not in st.session_state:
    st.session_state.role = None

if "last_face_hash" not in st.session_state:
    st.session_state.last_face_hash = None

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0


# =============================================================================
# IMAGE PREPROCESSING FOR LIGHTING COMPENSATION
# =============================================================================
def preprocess_image_for_fr(image_bytes):
    """
    Preprocess image to handle lighting variations.
    Applies histogram equalization and gamma correction.
    """
    # Convert bytes to OpenCV image
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    if img is None:
        return None
    
    # Convert to YUV color space for better lighting handling
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to Y channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
    
    # Convert back to BGR
    img_enhanced = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    
    # Apply gamma correction for low light
    gamma = 1.2
    invGamma = 1.0 / gamma
    img_enhanced = np.array([((v / 255.0) ** (1.0 / invGamma) * 255)
        if v > 0 else 0 for v in img_enhanced.flatten().astype("float")]).astype("uint8")
    img_enhanced = img_enhanced.reshape(img.shape)
    
    # Convert back to bytes
    _, buffer = cv2.imencode('.jpg', img_enhanced)
    return buffer.tobytes()


# =============================================================================
# FACE RECOGNITION UTILITY FUNCTION
# =============================================================================
def verify_face_match(registered_face_bytes, live_face_bytes, threshold=0.6):
    """
    Professional Face Recognition System using InsightFace.
    Analyzes facial features: eyes, nose, face shape, jawline, etc.
    Returns: (is_matched: bool, confidence: float, message: str)
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Demo mode - strict verification using hash comparison
        reg_hash = hashlib.md5(registered_face_bytes).hexdigest()
        live_hash = hashlib.md5(live_face_bytes).hexdigest()
        
        if reg_hash == live_hash:
            return True, 0.95, "Exact match (Demo Mode)"
        else:
            return False, 0.3, "Different photos detected (Demo Mode)"
    
    try:
        # Preprocess images for lighting compensation
        reg_processed = preprocess_image_for_fr(registered_face_bytes)
        live_processed = preprocess_image_for_fr(live_face_bytes)
        
        if reg_processed is None or live_processed is None:
            return False, 0.0, "Image processing failed"
        
        # Convert bytes to OpenCV images
        reg_array = np.frombuffer(reg_processed, np.uint8)
        reg_img = cv2.imdecode(reg_array, cv2.IMREAD_COLOR)
        
        live_array = np.frombuffer(live_processed, np.uint8)
        live_img = cv2.imdecode(live_array, cv2.IMREAD_COLOR)
        
        # Detect faces in registered image
        reg_faces = app.get(reg_img)
        if len(reg_faces) == 0:
            return False, 0.0, "No face detected in registered photo"
        
        # Detect faces in live image
        live_faces = app.get(live_img)
        if len(live_faces) == 0:
            return False, 0.0, "No face detected in live photo"
        
        # Get face embeddings (512-dimensional feature vector)
        reg_embedding = reg_faces[0].embedding
        live_embedding = live_faces[0].embedding
        
        # Calculate cosine similarity between embeddings
        from numpy.linalg import norm
        cosine_sim = np.dot(reg_embedding, live_embedding) / (norm(reg_embedding) * norm(live_embedding))
        
        # Convert to confidence score (0-1)
        confidence = float(cosine_sim)
        
        # Threshold check (0.6 = 60% similarity required)
        is_matched = confidence >= threshold
        
        if is_matched:
            return True, confidence, f"Match confirmed! Confidence: {confidence:.2%}"
        else:
            return False, confidence, f"Face mismatch. Confidence: {confidence:.2%} (Required: {threshold:.0%})"
    
    except Exception as e:
        return False, 0.0, f"Face recognition error: {str(e)}"


# =============================================================================
# TOP HEADER WITH LOGO
# =============================================================================
st.markdown("""
    <div class="royal-header">
        <img class="college-logo-img" src="https://www.campusoption.com/images/colleges/logos/06_09_17_100825_Logo.jpg" alt="SVIST Official Logo" />
        <div>
            <h1 class="header-title-text">SREE VAHINI INSTITUTE OF SCIENCE & TECHNOLOGY</h1>
            <div class="header-sub-text">Tiruvuru, NTR District, Andhra Pradesh | Approved by AICTE, Affiliated to JNTUK</div>
        </div>
    </div>
""", unsafe_allow_html=True)


# =============================================================================
# SVIST CAMPUS IMAGES - OFFICIAL WEBSITE
# =============================================================================
SVIST_CAMPUS_IMAGES = {
    "main_building": "https://www.campusoption.com/images/colleges/logos/06_09_17_100825_Logo.jpg",
    "campus_view": "https://content.jdmagicbox.com/comp/krishna/i7/9999p8676.8676.170921222703.y8i7/catalogue/sree-vahini-institute-of-science-and-technology-krishna-educational-institutes-yiulkugpqc.jpg",
    "library": "https://sreevahini.edu.in/images/gallery/library.jpg",
    "computer_lab": "https://sreevahini.edu.in/images/gallery/computer-lab.jpg",
    "auditorium": "https://sreevahini.edu.in/images/gallery/auditorium.jpg"
}


# =============================================================================
# PLACEMENT DATA - AI IMAGES (Always Work, Fast Loading)
# =============================================================================
OFFICIAL_SVIST_PLACEMENTS = [
    {
        "roll_no": "20MG1A0501",
        "name": "K. Sai Kumar",
        "branch": "CSE",
        "company": "TCS (Digital)",
        "package": "4.5 LPA",
        "image": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0512",
        "name": "M. Bhavani",
        "branch": "CSE",
        "company": "Genpact",
        "package": "3.8 LPA",
        "image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0405",
        "name": "P. Rajesh",
        "branch": "ECE",
        "company": "Q Spiders",
        "package": "4.2 LPA",
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0208",
        "name": "T. Anusha",
        "branch": "EEE",
        "company": "Schneider Electric India",
        "package": "5.5 LPA",
        "image": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0588",
        "name": "V. Sai Teja",
        "branch": "CSE",
        "company": "Tata Electronics",
        "package": "4.8 LPA",
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0315",
        "name": "Ch. Naveen",
        "branch": "MECH",
        "company": "Renault Nissan",
        "package": "4.0 LPA",
        "image": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0540",
        "name": "D. Divya Vani",
        "branch": "CSE",
        "company": "All Digi Tech",
        "package": "3.5 LPA",
        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop&q=80"
    },
    {
        "roll_no": "20MG1A0104",
        "name": "G. Suresh",
        "branch": "CIVIL",
        "company": "Devis Labs",
        "package": "3.2 LPA",
        "image": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80"
    }
]


# =============================================================================
# 1. LOGIN & HOMEPAGE LANDING PAGE
# =============================================================================
if not st.session_state.authenticated:
    # Show warning if face recognition not available
    if not FACE_RECOGNITION_AVAILABLE:
        st.warning("⚠️ Running in **Demo Mode**. Install with: `pip install insightface onnxruntime`")
    
    # Create two columns for layout
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    # Left Column - Welcome Message & Campus Images
    with col1:
        st.markdown("<h3 style='color:#38bdf8 !important;'>✨ SVIST Training & Placement Portal</h3>", unsafe_allow_html=True)
        st.write("Welcome to the official Training, Placement & Biometric Attendance Portal of SVIST.")
        
        # Campus Main Building Image
        st.image(
            "https://content.jdmagicbox.com/comp/krishna/i7/9999p8676.8676.170921222703.y8i7/catalogue/sree-vahini-institute-of-science-and-technology-krishna-educational-institutes-yiulkugpqc.jpg",
            caption="Sree Vahini Institute of Science & Technology Campus Building - Tiruvuru",
            use_container_width=True
        )
        
        # Campus Infrastructure Gallery
        st.markdown("<h4 style='color:#7dd3fc !important; margin-top: 20px;'>🏛️ Campus Infrastructure</h4>", unsafe_allow_html=True)
        infra_col1, infra_col2, infra_col3 = st.columns(3)
        
        with infra_col1:
            st.image(
                "https://sreevahini.edu.in/images/gallery/library.jpg", 
                caption="Central Library", 
                use_container_width=True
            )
        
        with infra_col2:
            st.image(
                "https://sreevahini.edu.in/images/gallery/computer-lab.jpg", 
                caption="Computer Laboratory", 
                use_container_width=True
            )
        
        with infra_col3:
            st.image(
                "https://sreevahini.edu.in/images/gallery/auditorium.jpg", 
                caption="Auditorium", 
                use_container_width=True
            )


    # Right Column - Login Form
    with col2:
        st.markdown("<h3 style='color:#38bdf8 !important;'>🔑 Sign In</h3>", unsafe_allow_html=True)
        user_input = st.text_input("User ID / Roll Number:", key="login_userid").strip().upper()
        pass_input = st.text_input("Password:", type="password", key="login_pass").strip()
        
        if st.button("Sign In to Portal", use_container_width=True, key="login_btn"):
            if not user_input:
                st.error("Please enter your User ID or Roll Number.")
            elif not pass_input:
                st.error("Please enter your password.")
            elif user_input in USERS:
                if USERS[user_input]["password"] == pass_input:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_input
                    st.session_state.role = USERS[user_input]["role"]
                    st.success("✅ Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Password. Please try again.")
            else:
                st.error("❌ User ID not found in database. Contact admin.")
                
        st.markdown("""
            ---
            **Quick Access Credentials:**
            * **Student:** `23MG1A0001` (Password: `pass`)
            * **Faculty:** `FCTCSEA1` (Password: `pass`)
            * **TPO Admin:** `TPO1` (Password: `pass`)
        """)


    # Placement Records Gallery Section
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #38bdf8 !important;'>🌟 Campus Placement Records Gallery</h2>", unsafe_allow_html=True)
    st.write("")


    # Placement Statistics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="stat-card"><h3>5.5 LPA</h3><p>Highest Package</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="stat-card"><h3>306+</h3><p>Total Offers</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="stat-card"><h3>13+</h3><p>Companies</p></div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="stat-card"><h3>72%</h3><p>Placement %</p></div>', unsafe_allow_html=True)


    st.write("")
    st.markdown("<h3 style='color:#38bdf8 !important;'>🎓 Placed Students</h3>", unsafe_allow_html=True)
    
    # Display placement cards in 4 columns
    p_cols = st.columns(4)
    for index, student in enumerate(OFFICIAL_SVIST_PLACEMENTS):
        with p_cols[index % 4]:
            st.markdown(f"""
                <div class="placement-card">
                    <img class="student-img-frame" src="{student['image']}" alt="{student['name']}" />
                    <div class="student-name-text">{student['name']}</div>
                    <div class="roll-text">Roll: <b>{student['roll_no']}</b> | {student['branch']}</div>
                    <div class="company-badge">{student['company']}</div>
                    <div class="package-badge">Package: {student['package']}</div>
                </div>
            """, unsafe_allow_html=True)


# =============================================================================
# 2. LOGGED-IN DASHBOARD
# =============================================================================
else:
    user_info = USERS[st.session_state.user_id]
    
    # Sidebar User Information
    st.sidebar.markdown(f"### 👤 User: `{user_info['name']}`")
    st.sidebar.write(f"**ID:** `{st.session_state.user_id}`")
    st.sidebar.write(f"**Role:** `{st.session_state.role}`")
    
    # Face Recognition Status
    if FACE_RECOGNITION_AVAILABLE:
        st.sidebar.success("✅ FRS Active")
    else:
        st.sidebar.warning("⚠️ Demo Mode")
    
    # Developer Options
    dev_mode = st.sidebar.checkbox("🛠️ Dev Mode", value=False)
    test_threshold = st.sidebar.slider("Threshold", 0.4, 0.8, 0.6, 0.05)
    
    # Logout Button
    if st.sidebar.button("Log Out", use_container_width=True, key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.role = None
        st.rerun()


    # Student Role Dashboard
    if st.session_state.role == "Student":
        st.markdown(f"## Welcome, {user_info['name']}")
        
        # Create tabs for different sections
        tab_att, tab_drive, tab_prof = st.tabs(["📸 Attendance", "💼 Drives", "⚙️ Profile"])
        
        # Attendance Verification Tab
        with tab_att:
            st.markdown("### 📸 Biometric Attendance System")
            st.info("ℹ️ **FRS:** Analyzes eyes, nose, face shape. **Lighting compensation enabled.**")
            
            # Location Selection
            selected_loc = st.selectbox("📍 Location:", options=list(LOCATIONS.keys()), key="location_select")
            
            # Face Registration
            if user_info.get("registered_face") is None:
                st.warning("⚠️ Register your face first.")
                reg_photo = st.camera_input("Capture Photo", key="reg_cam_input")
                
                if reg_photo:
                    try:
                        if FACE_RECOGNITION_AVAILABLE:
                            reg_array = np.frombuffer(reg_photo.getvalue(), np.uint8)
                            reg_img = cv2.imdecode(reg_array, cv2.IMREAD_COLOR)
                            faces = app.get(reg_img)
                            if len(faces) == 0:
                                st.error("❌ No face detected.")
                                st.stop()
                        
                        USERS[st.session_state.user_id]["registered_face"] = reg_photo.getvalue()
                        st.success("✅ Face registered!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.info("✅ Face Profile Active.")
                if st.button("🔄 Reset", key="reset_face_btn"):
                    USERS[st.session_state.user_id]["registered_face"] = None
                    st.rerun()

                st.markdown("---")
                
                # GPS Location Verification
                loc = get_geolocation()
                
                if not loc:
                    st.warning("⚠️ GPS permission pending.")
                    if st.button("🔄 Refresh GPS", key="refresh_gps"):
                        st.rerun()
                elif isinstance(loc, dict) and ("coords" in loc or "latitude" in loc):
                    coords = loc.get("coords", loc)
                    u_lat = coords.get("latitude")
                    u_lon = coords.get("longitude")
                    
                    if u_lat and u_lon:
                        in_range, distance, loc_name = verify_location_range(u_lat, u_lon, selected_loc)
                        st.write(f"**📍 Spot:** `{loc_name}` | **📏 Distance:** `{distance:.1f}m`")
                        
                        if in_range or dev_mode:
                            st.success("✅ Within geofenced area!")
                            
                            # Live Face Scan
                            live_photo = st.camera_input("Scan Face", key="live_att_cam")
                            
                            if live_photo:
                                live_hash = hashlib.md5(live_photo.getvalue()).hexdigest()
                                if st.session_state.last_face_hash == live_hash:
                                    st.warning("⚠️ Same photo. Capture new one.")
                                    st.stop()
                                st.session_state.last_face_hash = live_hash
                                
                                with st.spinner("🔍 Verifying..."):
                                    is_matched, confidence, match_msg = verify_face_match(
                                        user_info["registered_face"], 
                                        live_photo.getvalue(),
                                        threshold=test_threshold
                                    )
                                    
                                    if is_matched:
                                        st.success(f"✅ {match_msg}")
                                        
                                        if st.button("Submit Attendance", use_container_width=True, key="submit_attend"):
                                            ATTENDANCE_LOGS.append({
                                                "Student_ID": st.session_state.user_id,
                                                "Name": user_info["name"],
                                                "Branch": user_info.get("branch", "N/A"),
                                                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                "Location": loc_name if not dev_mode else "Dev",
                                                "Distance_Meters": round(distance, 2),
                                                "Face_Confidence": f"{confidence:.2%}",
                                                "Status": "Verified"
                                            })
                                            st.success("🎉 Logged!")
                                            st.balloons()
                                    else:
                                        st.error(f"❌ {match_msg}")
                        else:
                            st.error(f"❌ Out of Area: {distance:.1f}m from {loc_name}.")
                else:
                    st.error("❌ GPS error.")


        # Active Recruitment Drives Tab
        with tab_drive:
            st.markdown("### 💼 Active Drives")
            if ACTIVE_DRIVES:
                for drive in ACTIVE_DRIVES:
                    ca, cb = st.columns([3, 1])
                    with ca:
                        st.markdown(f"#### {drive['Company']} - {drive['Role']}")
                        st.write(f"**Package:** {drive['Package']} | **Branches:** {', '.join(drive['Branches'])}")
                    with cb:
                        s_cgpa = user_info.get("cgpa", 0.0)
                        s_backlogs = user_info.get("backlogs", 0)
                        s_branch = user_info.get("branch", "")
                        eligible = (s_cgpa >= drive["Min_CGPA"]) and (s_backlogs <= drive["Max_Backlogs"]) and (s_branch in drive["Branches"])
                        if eligible:
                            if st.button("Apply", key=f"app_{drive['Drive_ID']}"):
                                APPLICATIONS_LOG.append({
                                    "Drive_ID": drive["Drive_ID"],
                                    "Company": drive["Company"],
                                    "Student_ID": st.session_state.user_id,
                                    "Name": user_info["name"],
                                    "Branch": s_branch,
                                    "CGPA": s_cgpa,
                                    "Email": user_info.get("email", "")
                                })
                                st.success("✅ Applied!")
                        else:
                            st.error("❌ Not Eligible")
            else:
                st.info("ℹ️ No active drives.")


        # Profile Settings Tab
        with tab_prof:
            st.markdown("### 📝 Profile")
            up_email = st.text_input("Email:", value=user_info.get("email", ""), key="prof_email")
            up_phone = st.text_input("Phone:", value=user_info.get("phone", ""), key="prof_phone")
            cur_branch = user_info.get("branch", "CSE-A")
            b_idx = BRANCH_OPTIONS.index(cur_branch) if cur_branch in BRANCH_OPTIONS else 0
            up_branch = st.selectbox("Branch:", BRANCH_OPTIONS, index=b_idx, key="prof_branch")
            up_cgpa = st.number_input("CGPA:", 0.0, 10.0, float(user_info.get("cgpa", 7.5)), 0.1, key="prof_cgpa")
            up_backlogs = st.number_input("Backlogs:", 0, 20, int(user_info.get("backlogs", 0)), key="prof_backlogs")
            
            if st.button("Save", key="save_profile"):
                USERS[st.session_state.user_id]["email"] = up_email
                USERS[st.session_state.user_id]["phone"] = up_phone
                USERS[st.session_state.user_id]["branch"] = up_branch
                USERS[st.session_state.user_id]["cgpa"] = up_cgpa
                USERS[st.session_state.user_id]["backlogs"] = up_backlogs
                st.success("✅ Saved!")


    # Admin/Faculty Role Dashboard
    else:
        st.markdown(f"## Admin Dashboard ({st.session_state.role})")
        ft1, ft2, ft3 = st.tabs(["📢 Drives", "📊 Records", "👥 Users"])
        
        # Publish New Drive Tab
        with ft1:
            st.markdown("### 📢 Post Drive")
            c_name = st.text_input("Company:", key="admin_cname")
            c_role = st.text_input("Role:", key="admin_crole")
            c_pkg = st.text_input("Package:", key="admin_cpkg")
            c_cgpa = st.number_input("Min CGPA:", 0.0, 10.0, 6.5, 0.1, key="admin_ccgpa")
            c_backlogs = st.number_input("Max Backlogs:", 0, 10, 0, key="admin_cbacklogs")
            c_branches = st.multiselect("Branches:", BRANCH_OPTIONS, default=["CSE-A", "ECE"], key="admin_cbranches")
            
            if st.button("Publish", key="publish_drive"):
                if c_name and c_role:
                    ACTIVE_DRIVES.append({
                        "Drive_ID": f"DRV_{len(ACTIVE_DRIVES)+1}",
                        "Company": c_name,
                        "Role": c_role,
                        "Package": c_pkg,
                        "Min_CGPA": c_cgpa,
                        "Max_Backlogs": c_backlogs,
                        "Branches": c_branches
                    })
                    st.success(f"✅ {c_name} published!")
                else:
                    st.error("❌ Required fields missing.")


        # Attendance Records Tab
        with ft2:
            st.markdown("### 📊 Attendance Records")
            if ATTENDANCE_LOGS:
                st.dataframe(pd.DataFrame(ATTENDANCE_LOGS), use_container_width=True)
            else:
                st.info("ℹ️ No records.")


        # User Management Tab
        with ft3:
            st.markdown("### 👥 Users")
            rows = [{"User ID": u, "Name": i.get("name"), "Role": i.get("role"), "Branch": i.get("branch")} for u, i in USERS.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True)