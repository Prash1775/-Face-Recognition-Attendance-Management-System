# SETUP INSTRUCTIONS
## Face Recognition Attendance Management System

### ⚡ 5-Minute Quick Setup

#### 1. Navigate to Project Directory
```bash
cd "c:\Users\prash\Desktop\studant app\attendance_system"
```

#### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*Note: If face_recognition fails, you may need dlib pre-built:*
```bash
pip install face-recognition-models
```

#### 4. Run Application
```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

---

## 📋 Detailed Setup Guide

### Prerequisites
- **Python 3.8+** (Recommended: 3.10 or later)
- **pip** (Python package manager)
- **Webcam** (for face capture)
- **4GB RAM minimum**
- **Windows 10+, macOS 10.13+, or Linux**

### Step 1: Python Installation

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer with "Add Python to PATH" checked
3. Verify: `python --version`

**macOS:**
```bash
brew install python3
python3 --version
```

**Linux:**
```bash
sudo apt-get install python3 python3-pip
python3 --version
```

### Step 2: Clone/Extract Project

Extract the attendance_system folder to your desired location.

### Step 3: Virtual Environment Setup

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- streamlit (UI framework)
- opencv-python (image processing)
- face-recognition (face detection)
- numpy (numerical computing)
- pillow (image handling)
- plotly (charts)
- fpdf2 (PDF generation)
- pytz (timezone handling)
- pandas (data frames)

### Step 5: Run the Application

```bash
streamlit run app.py
```

### Step 6: Configuration

#### Change Admin Password (IMPORTANT!)
1. Login as Admin (password: `admin123`)
2. Create a new admin password immediately
3. Update the hash in `auth.py` line ~42 if needed

#### Configure Face Recognition Tolerance
Edit `components/face_engine.py` line 6:
```python
TOLERANCE = 0.6  # Lower = stricter match (0.5 = very strict, 0.7 = loose)
```

#### Change Database Location
Edit `components/db.py` line 5:
```python
DB_PATH = "data/attendance.db"  # Change path here
```

---

## 🎯 First Time Usage

### As Admin:
1. Login: `admin123`
2. Go to Student Management → Add Student
3. Go to Teacher Management → Add Teacher
4. Go to Teacher Management → Assign Courses

### As Teacher:
1. Login with credentials (set up by admin)
2. Go to "Start Session"
3. Select course and set duration
4. System generates PIN (e.g., "4721")
5. Share PIN with students

### As Student:
1. Register with face enrollment
2. Login with roll number
3. Enter session PIN
4. Capture face (press spacebar to take photo)
5. Attendance marked! ✅

---

## 📦 Dependency Details

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.28.1 | Web UI framework |
| opencv-python | 4.8.1.78 | Image processing |
| face-recognition | 1.3.5 | Face detection & encoding |
| numpy | 1.24.3 | Numerical arrays |
| pillow | 10.0.0 | Image handling |
| plotly | 5.17.0 | Interactive charts |
| fpdf2 | 2.7.0 | PDF generation |
| pytz | 2023.3 | Timezone support |
| pandas | 2.1.1 | Data analysis |

---

## 🔧 Troubleshooting

### Issue: "No module named face_recognition"
**Solution:**
```bash
pip install face-recognition --upgrade
pip install dlib --upgrade
```

### Issue: "No camera detected"
**Solution:**
- Check browser permissions (Chrome: Settings → Privacy → Camera)
- Allow camera access when prompted
- Restart browser

### Issue: Pip installation is slow
**Solution:**
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### Issue: "sqlite3 database is locked"
**Solution:**
1. Close all connections (logout from all windows)
2. Delete `data/attendance.db`
3. Restart application

### Issue: Face not detected
**Solution:**
- Ensure good lighting (natural light best)
- Face should be clearly visible (avoid glasses/masks)
- Position face in center of frame
- Try 3-4 times

### Issue: Streamlit port 8501 already in use
**Solution:**
```bash
streamlit run app.py --server.port 8502
```

---

## 🚀 Deployment Options

### Local Server (Development)
```bash
streamlit run app.py
```

### Remote Server (Production)
Install nginx + gunicorn:
```bash
pip install gunicorn
gunicorn --workers 4 --timeout 0 --bind 0.0.0.0:8000 "streamlit.cli:main"
```

### Cloud Deployment (Recommended)
**Streamlit Cloud:**
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Deploy in 1 click

**Heroku:**
1. Create `runtime.txt`: `python-3.10.0`
2. Create `Procfile`: `web: streamlit run app.py`
3. Deploy via Heroku CLI

**AWS/Azure/GCP:**
Use Docker:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD streamlit run app.py
```

---

## 📊 Database Initialization

The database is **auto-created** on first run with tables:
- students
- teachers
- teacher_assignments
- sessions
- attendance

**To reset database:**
```bash
rm data/attendance.db
# Database will be recreated on next run
```

---

## 🔐 Security Setup

### 1. Change Admin Password
**File**: `components/auth.py` (Line ~42)
```python
def login_admin(admin_password):
    admin_hash = hashlib.sha256("YOUR_NEW_PASSWORD".encode()).hexdigest()
```

Generate new hash:
```python
import hashlib
print(hashlib.sha256("your_password".encode()).hexdigest())
```

### 2. Enable HTTPS
For production, use nginx with SSL:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
    }
}
```

### 3. Database Backup
```bash
cp data/attendance.db data/attendance_backup_$(date +%Y%m%d).db
```

---

## 📱 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Full Support | Recommended |
| Firefox | ✅ Full Support | Good |
| Safari | ✅ Full Support | Requires permission |
| Edge | ✅ Full Support | Full |
| Opera | ✅ Full Support | Good |

---

## 🎓 Test Accounts (After Setup)

**Admin**
- Password: `admin123` (change this!)

**Sample Teacher** (Add via Admin Panel)
- ID: TECH001
- Email: tech01@college.com

**Sample Student** (Self-register)
- Roll: DATA001
- Password: (your choice)

---

## 📞 Support

### Common Issues:
1. **Dependencies**: `pip install --upgrade -r requirements.txt`
2. **Database**: Delete `data/attendance.db` and restart
3. **Camera**: Check browser permissions
4. **Face**: Ensure good lighting and clear visibility
5. **Port**: Change with `--server.port XXXX`

### Getting Help:
- Check `README.md` for features
- Review `QUICKSTART.md` for quick start
- Visit [Streamlit Docs](https://docs.streamlit.io)
- Check [face_recognition GitHub](https://github.com/ageitgey/face_recognition)

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Python installed (`python --version`)
- [ ] Virtual environment active (`(venv)` in prompt)
- [ ] Dependencies installed (`pip list`)
- [ ] Application runs (`streamlit run app.py`)
- [ ] Can access http://localhost:8501
- [ ] Admin login works
- [ ] Can add students
- [ ] Can add teachers
- [ ] Can capture face
- [ ] Charts display properly
- [ ] Export functions work

---

## 🆘 Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate              # macOS/Linux
venv\Scripts\activate                 # Windows

# Install/upgrade packages
pip install -r requirements.txt
pip install --upgrade streamlit

# Run app
streamlit run app.py
streamlit run app.py --server.port 8502  # Different port

# Reset database
rm data/attendance.db

# Check Python version
python --version
python3 --version

# Deactivate environment
deactivate
```

---

## 📚 Additional Resources

- **Streamlit Documentation**: https://docs.streamlit.io
- **face_recognition Library**: https://github.com/ageitgey/face_recognition
- **SQLite3 Reference**: https://www.sqlite.org/docs.html
- **Plotly Charts**: https://plotly.com/python/
- **fpdf2 PDF**: https://py-pdf.github.io/fpdf2/

---

## 🎉 Next Steps

1. ✅ Complete setup above
2. → Test admin login
3. → Add sample teacher and student
4. → Test attendance marking
5. → Explore analytics dashboard
6. → Deploy to production

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-27  
**Status**: Production Ready  
**College**: Department of Technology, Pune
