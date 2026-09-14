# SVIST Training, Placement & Smart Biometric Portal

A Streamlit-based web application for managing student placement drives, eligibility verification, job applications, profile updates, and geofenced biometric attendance for **Sree Vahini Institute of Science & Technology, Tiruvuru**.

> This is an academic/student project created for demonstration and learning purposes.

## Features

### Student Portal

- Student login using roll number and password
- Face-profile registration using the device camera
- Biometric face-verification workflow for attendance
- GPS/geofence-based attendance validation
- View active recruitment drives
- Check eligibility using CGPA, department, and backlog criteria
- Apply for eligible placement drives
- Update profile details including email, phone, branch, CGPA, and backlogs

### Faculty Portal

- Faculty login using faculty ID and password
- View student attendance records
- Create and publish placement drives
- Check placement-drive information

### TPO Admin Portal

- TPO administrator login
- Publish and manage recruitment drives
- View biometric attendance records
- View student job applications
- View registered student, faculty, and TPO user records

### User Interface

- Royal blue and sky-blue themed dashboard
- Animated header and interactive placement cards
- Responsive Streamlit layout
- Separate dashboards for Student, Faculty, and TPO Admin roles

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic |
| Streamlit | Web user interface |
| Pandas | Table and record display |
| NumPy | Numerical operations |
| OpenCV | Image preprocessing |
| Streamlit JS Eval | Browser geolocation access |
| InsightFace + ONNX Runtime | Face-verification experiment |

## Project Structure

```text
svist_tpo_portal/
│
├── app.py
├── database.py
├── utils.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── venv/                 # Local virtual environment; not uploaded to GitHub
```

## Installation

### 1. Clone the repository

```bash
git clone [https://github.com/ushasri522/svist-tpo-portal.git](https://github.com/ushasri522/svist-tpo-portal.git)
cd svist-tpo-portal
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will typically open at:

```text
http://localhost:8501
```

## Demo Login Credentials

| User Role | User ID | Password |
|---|---|---|
| Student | `23MG1A0001` | `pass` |
| Faculty | `FCTCSEA1` | `pass` |
| TPO Admin | `TPO1` | `pass` |

## User Account Format

### Students

Student accounts are automatically generated in this format:

```text
23MG1A0001 to 23MG1A1000
```

All generated student accounts use:

```text
Password: pass
```

### Faculty

Faculty account format depends on the department:

```text
FCTCSEA1
FCTCSEB1
FCTCSEC1
FCTDS1
FCTAIML1
FCTECE1
FCTEEE1
FCTMECH1
FCTCIVIL1
```

All generated faculty accounts use:

```text
Password: pass
```

### TPO Admin

```text
TPO1
TPO2
```

Password for both accounts:

```text
pass
```

## Face Verification Note

The attendance module is designed as a learning prototype.

- Real facial recognition needs supported packages and compatible Python versions.
- For reliable InsightFace setup, Python 3.10 or Python 3.11 is recommended.
- Camera access requires browser permission.
- Location access requires browser permission.
- For a real production attendance system, face liveness detection, encrypted biometric storage, explicit consent, audit logs, and secure server-side authentication are necessary.

## Deployment Notes

For deployment on Render:

```bash
pip install -r requirements.txt
```

Use this start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Make sure `requirements.txt` contains at least:

```text
streamlit
pandas
numpy
opencv-python-headless
streamlit-js-eval
```

## Important Security Note

This project is a demonstration application.

Do not use the sample credentials in a real production system. Before real deployment:

- Replace plain-text passwords with password hashes.
- Use a secure database instead of in-memory Python lists/dictionaries.
- Protect sensitive user details and biometric information.
- Do not upload face images or biometric data to public GitHub repositories.
- Add role-based authorization and secure session handling.
- Obtain user consent before collecting camera and location data.

## Author

**Usha Sri Kodiganti**

B.Tech Student  
Sree Vahini Institute of Science & Technology  
Tiruvuru, Andhra Pradesh, India

## Repository

[GitHub Repository](https://github.com/ushasri522/svist-tpo-portal)
