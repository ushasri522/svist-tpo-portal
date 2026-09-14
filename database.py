# database.py

# Global Branch Options for SVIST
BRANCH_OPTIONS = [
    "CSE-A",
    "CSE-B",
    "CSE-C",
    "DS",
    "AIML",
    "ECE",
    "EEE",
    "MECH",
    "CIVIL",
]


# System Users Database Store
USERS = {}


# -------------------------------------------------------------------
# 1. TPO ADMIN ACCOUNTS
# -------------------------------------------------------------------
for i in range(1, 3):
    tpo_id = f"TPO{i}"

    USERS[tpo_id] = {
        "name": f"TPO Officer {i}",
        "role": "TPO Admin",
        "password": "pass",
        "email": f"tpo{i}@sreevahini.edu.in",
        "phone": "9876543210",
    }


# -------------------------------------------------------------------
# 2. FACULTY ACCOUNTS
# -------------------------------------------------------------------
for branch in BRANCH_OPTIONS:
    clean_branch = branch.replace("-", "")

    for i in range(1, 11):
        faculty_id = f"FCT{clean_branch}{i}"

        USERS[faculty_id] = {
            "name": f"Faculty {branch} {i}",
            "role": "Faculty",
            "password": "pass",
            "branch": branch,
            "email": f"faculty_{clean_branch.lower()}{i}@sreevahini.edu.in",
            "phone": "9876543210",
        }


# -------------------------------------------------------------------
# 3. STUDENT ACCOUNTS
# -------------------------------------------------------------------
for i in range(1, 1001):
    roll_no = f"23MG1A{i:04d}"
    assigned_branch = BRANCH_OPTIONS[(i - 1) % len(BRANCH_OPTIONS)]

    USERS[roll_no] = {
        "name": f"Student {i}",
        "role": "Student",
        "password": "pass",
        "branch": assigned_branch,
        "cgpa": 7.5,
        "backlogs": 0,
        "email": f"{roll_no.lower()}@sreevahini.edu.in",
        "phone": "",
        "resume_pdf": None,
        "registered_face": None,
    }


# -------------------------------------------------------------------
# 4. SHARED IN-MEMORY STORAGE
# -------------------------------------------------------------------
ACTIVE_DRIVES = []
ATTENDANCE_LOGS = []
APPLICATIONS_LOG = []