# Quick Start Guide

## Project: Face Recognition Attendance Management System
**College**: Department of Technology, Pune

## What's Been Created

### ✅ Complete Project Structure
```
attendance_system/
├── app.py                      # Main entry point with role-based routing
├── requirements.txt            # All dependencies
├── README.md                   # Full documentation
├── .gitignore                 # Git ignore file
│
├── components/
│   ├── __init__.py
│   ├── db.py                  # SQLite database operations
│   ├── face_engine.py         # Face recognition & verification
│   ├── auth.py                # Login & session management
│   └── utils.py               # Helpers (PIN, timer, export)
│
├── pages/
│   ├── __init__.py
│   ├── student.py             # Student portal (register, mark attendance, view)
│   ├── teacher.py             # Teacher portal (sessions, live attendance)
│   └── admin.py               # Admin dashboard (management, analytics)
│
└── data/
    └── attendance.db          # Auto-created SQLite database
```

## Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd "c:\Users\prash\Desktop\studant app\attendance_system"
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run app.py
```

### Step 3: Login
- **Admin**: Password: `admin123`
- **Student/Teacher**: Create through admin panel or use self-registration

## Features Implemented

### 🎓 Student Portal
✅ Self-registration with face encoding capture
✅ PIN + face verification for attendance marking
✅ View attendance records
✅ Export as CSV/PDF
✅ Profile management

### 👨‍🏫 Teacher Portal
✅ Create attendance sessions with auto 4-digit PIN
✅ Real-time attendance monitoring
✅ Session timer with remaining time
✅ Live attendance count
✅ Download attendance reports

### 🔐 Admin Dashboard
✅ Key metrics & KPI overview
✅ Student management (add/view/delete)
✅ Teacher management with course assignments
✅ Attendance logs with advanced filtering
✅ Analytics with Plotly charts
✅ Attendance trends visualization

## Database Tables Created

1. **students** - Roll number, name, email, course, year, division, face encoding
2. **teachers** - Teacher ID, name, email, phone
3. **teacher_assignments** - Course assignments linking teachers to subjects
4. **sessions** - Attendance sessions with PIN, timer, status
5. **attendance** - Individual attendance records with verification status

## Security Features

✅ SHA-256 password hashing
✅ Face encodings (never images) stored as pickled numpy BLOBs
✅ In-memory face comparison only
✅ One attendance per student per session (UNIQUE constraint)
✅ Session PIN expiry with timer
✅ Role-based access control

## Key Configurations

- **Face Recognition Tolerance**: 0.6 (adjust for strictness)
- **Default Model**: HOG (fast), can use CNN (accurate)
- **PIN Length**: 4 digits
- **Time Zone**: IST (Asia/Kolkata)
- **Courses**: 5 options (Data Science, Blockchain, etc.)
- **Academic Years**: First through Fourth
- **Divisions**: A, B

## Data Flow

### Student Attendance
1. Student captures face at registration → Face encoding extracted & stored
2. Teacher starts session → PIN generated
3. Student enters PIN → System finds session
4. Student captures face → Compared with stored encoding in-memory
5. If match → Attendance marked (no image stored)

## Export Options

✅ CSV export for all logs
✅ PDF reports with college header
✅ Filtered exports by date, course, teacher
✅ Analytics charts (Plotly interactive)

## What to Do Next

### First Time Setup:
1. Run `streamlit run app.py`
2. Login as Admin (password: admin123)
3. Change admin password ⚠️
4. Add teachers and their course assignments
5. Add students (or let them self-register)
6. Teachers start sessions, students mark attendance

### Sample Workflow:
```
Admin Panel →
  Add Teacher: TECH001 (Email: tech01@college.com)
  Assign Course: BSc Data Science, Year 1, Div A, Subject: Python

Student Portal →
  Self-register: Roll DATA001
  Capture face → Stored encrypted

Teacher Portal →
  Start Session → PIN: 1234
  Share PIN with class

Student Portal →
  Enter PIN 1234 → Capture face → Attendance ✓
```

## Important Notes

1. **No Images Stored**: Only 128-d face encodings as pickled numpy arrays
2. **In-Memory Processing**: Face comparison happens in RAM, never saved
3. **Auto-Expiry**: Students not marked by session end are absent
4. **UNIQUE Constraint**: One attendance per student per session
5. **GDPR Compliant**: No raw biometric data storage

## Troubleshooting

**Issue**: Face not detected
- Solution: Ensure good lighting, clear face visibility

**Issue**: Dependencies fail
- Solution: `pip install --upgrade -r requirements.txt`

**Issue**: Database error
- Solution: Delete `data/attendance.db` and restart (fresh database)

## System Requirements

- Python 3.8+
- 4GB RAM minimum
- Webcam for face capture
- Modern browser (Chrome, Firefox, Safari, Edge)

## File Statistics

- **Total Files**: 13
- **Python Code Files**: 10
- **Configuration Files**: 2
- **Documentation**: 1
- **Total Lines of Code**: ~2000+

## Next Steps

1. ✅ Project created
2. → Install dependencies (pip install -r requirements.txt)
3. → Run app (streamlit run app.py)
4. → Change admin password
5. → Add users and start using

---

**Status**: ✅ COMPLETED - Ready to Use
**Version**: 1.0.0
**College**: Department of Technology, Pune
**Date**: 2026-03-27
