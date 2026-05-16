# Face Recognition Attendance Management System

## Overview
This is a comprehensive face recognition-based attendance management system built with Streamlit, OpenCV, and face_recognition. It provides role-based access for students, teachers, and administrators.

## Features

### 👨‍🎓 Student Portal
- **Self-Registration**: Register with face enrollment (no images stored, only encodings)
- **Mark Attendance**: Quick attendance marking with PIN + face verification
- **View Attendance**: Check attendance records and export as CSV/PDF
- **Profile Management**: Update password and view enrolled information

### 👨‍🏫 Teacher Portal
- **Start Sessions**: Create attendance sessions with auto-generated 4-digit PIN
- **Real-time Monitoring**: Live attendance count for active sessions
- **Session Management**: View and end sessions, track time remaining
- **Attendance Reports**: Download session attendance as CSV/PDF

### 🔐 Admin Dashboard
- **Dashboard Overview**: Key metrics, charts, and recent sessions
- **Student Management**: Add/view/delete students with filtering
- **Teacher Management**: Manage teachers and assign courses
- **Attendance Logs**: Comprehensive attendance logs with filters
- **Analytics Reports**: Course-wise, teacher-wise, and trend analyses

## Technology Stack

- **Frontend**: Streamlit
- **Face Recognition**: face_recognition library (dlib + CNN)
- **Database**: SQLite3
- **Charts**: Plotly
- **PDF Export**: fpdf2
- **Cryptography**: SHA-256 password hashing

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Steps

1. **Clone/Extract the project**
   ```bash
   cd attendance_system
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will open in your default browser at `http://localhost:8501`

## Default Credentials

### Admin Login
- **Password**: `admin123` (⚠️ Change in production!)

### Sample Student/Teacher
You can add them through the admin panel

## Database Structure

### Tables
- **students**: Roll number, name, email, course, year, division, face encoding
- **teachers**: Teacher ID, name, email, phone, password
- **teacher_assignments**: Course assignments for teachers
- **sessions**: Attendance sessions with PIN and timer
- **attendance**: Attendance records with face verification status

## Key Features

### 🔒 Security
- **Passwords**: SHA-256 hashing
- **Face Encodings**: Stored as pickled numpy arrays (BLOB)
- **No Images**: Only face encodings stored, never raw images

### 📊 Attendance Tracking
- **One Attendance Per Session**: UNIQUE constraint prevents duplicate marking
- **Session Expiry**: Auto-marked absent after session timer ends
- **Face Verification**: In-memory comparison, no storage

### 📁 Data Management
- **CSV Export**: Attendance logs for spreadsheet analysis
- **PDF Reports**: Formatted reports with college header
- **Filtering**: Date range, course, teacher filters for logs

## Courses Available
- BSc Data Science
- B.Tech Data Science
- M.Tech Data Science
- BSc Blockchain
- PG Data Science

## Academic Structure
- **Years**: First, Second, Third, Fourth
- **Divisions**: A, B

## Usage Examples

### Student: Mark Attendance
1. Login with Roll Number
2. Enter Session PIN (provided by teacher)
3. Capture face photo
4. System verifies face and marks attendance

### Teacher: Start Session
1. Login with Teacher ID
2. Select course/subject
3. Set session duration
4. Share 4-digit PIN with students
5. Monitor attendance in real-time
6. End session when complete

### Admin: View Analytics
1. Login with admin password
2. Access Dashboard for KPIs
3. View course-wise student distribution
4. Generate attendance trends
5. Export comprehensive reports

## File Structure
```
attendance_system/
├── app.py                    # Main entry point
├── requirements.txt          # Python dependencies
├── components/
│   ├── db.py               # Database operations
│   ├── face_engine.py      # Face recognition logic
│   ├── auth.py             # Authentication & session
│   └── utils.py            # Helper functions
├── pages/
│   ├── student.py          # Student portal
│   ├── teacher.py          # Teacher portal
│   └── admin.py            # Admin dashboard
└── data/
    └── attendance.db       # SQLite database (auto-created)
```

## Configuration

### Face Recognition Settings
- **Tolerance**: 0.6 (matching threshold - lower = stricter)
- **Model**: HOG (faster) - can change to CNN for accuracy
- **Encodings**: 128-dimensional numpy arrays

### Session Settings
- **PIN Length**: 4 digits
- **Session Duration**: 15-180 minutes (configurable)
- **Time Zone**: IST (Asia/Kolkata)

## Troubleshooting

### Face Not Detected
- Ensure good lighting
- Position face clearly in frame
- Avoid glasses or masks
- Try re-registering with better photo

### Session PIN Not Found
- Verify PIN is correct (4 digits)
- Check if session is still active
- Ensure correct course selected

### Dependencies Issues
- Clear pip cache: `pip cache purge`
- Reinstall: `pip install -r requirements.txt --force-reinstall`

## Security Recommendations

1. **Change Default Admin Password** immediately
2. **Use HTTPS** when deploying (use Streamlit Cloud or nginx)
3. **Regular Backups** of attendance.db
4. **User Access Control**: Limit admin access
5. **Audit Logs**: Monitor attendance modifications

## Performance Tips

- Use **HOG model** for faster face detection (default)
- Optimize face image size (recommended: 500x500px)
- Regular database cleanup of old sessions
- Use **caching** for reports

## Browser Compatibility
- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅

## Known Limitations

1. **Multiple Faces**: System rejects if >1 face in frame
2. **Poor Lighting**: May fail face detection
3. **Heavy Makeup/Accessories**: May affect matching
4. **Batch Processing**: Not optimized for bulk imports

## Future Enhancements

- [ ] LDAP/Active Directory integration
- [ ] Mobile app for teachers
- [ ] QR code based attendance
- [ ] Email notifications
- [ ] API endpoints for integration
- [ ] Multi-language support
- [ ] Biometric fingerprint support

## Licensing
This project is built for Department of Technology, Pune

## Support
For issues or feature requests, contact the administrator.

## 🚀 Cloud Deployment (Streamlit Cloud + Supabase)

To deploy this application to the cloud and ensure permanent data storage:

### 1. Database Setup (Supabase)
1.  Create a free account on [Supabase](https://supabase.com/).
2.  Create a new project.
3.  Go to the **SQL Editor** in Supabase and paste the contents of `supabase_setup.sql`.
4.  Run the script to create all necessary tables.

### 2. GitHub Deployment
1.  Push your code to a GitHub repository.
2.  Go to [Streamlit Community Cloud](https://share.streamlit.io/) and connect your repository.
3.  Select `app.py` as the main entry point.

### 3. Environment Variables (Secrets)
In the Streamlit Cloud dashboard, go to **Settings > Secrets** and add your Supabase credentials:
```toml
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"
```

### 4. Mobile Access
Once deployed, simply open the Streamlit URL on your mobile phone browser. The app will automatically adjust its layout and use your phone's camera for face recognition.

**Last Updated**: 2026-03-27
**Version**: 1.0.0
**College**: Department of Technology, Pune
