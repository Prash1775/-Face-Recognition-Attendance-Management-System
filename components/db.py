import sqlite3
import pickle
import numpy as np
from datetime import datetime, timedelta
import os
import streamlit as st
from supabase import create_client, Client

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "attendance.db")
DB_PATH = os.path.abspath(DB_PATH)

# Supabase configuration (optional fallback to SQLite)
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

_supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase connection error: {e}")
else:
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.warning("⚠️ Supabase credentials not found in st.secrets. Falling back to local SQLite.")

def is_supabase():
    """Check if we are using Supabase"""
    return _supabase is not None

def get_connection():
    """Get SQLite database connection (internal use only)"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all database tables (SQLite fallback)"""
    if not is_supabase():
        conn = get_connection()
        c = conn.cursor()
        
        # Students table
        c.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                course TEXT NOT NULL,
                year TEXT NOT NULL,
                division TEXT NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                face_encoding BLOB,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Teachers table
        c.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Teacher assignments
        c.execute("""
            CREATE TABLE IF NOT EXISTS teacher_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                year TEXT NOT NULL,
                division TEXT NOT NULL,
                subject TEXT NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                UNIQUE(teacher_id, course, year, division, subject)
            )
        """)
        
        # Sessions table
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                year TEXT NOT NULL,
                division TEXT NOT NULL,
                subject TEXT NOT NULL,
                session_pin TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_minutes INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            )
        """)
        
        # Attendance table
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                roll_number TEXT NOT NULL,
                mark_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verification_status TEXT DEFAULT 'face_verified',
                FOREIGN KEY (session_id) REFERENCES sessions(id),
                FOREIGN KEY (student_id) REFERENCES students(id),
                UNIQUE(session_id, student_id)
            )
        """)
        
        conn.commit()
        conn.close()

# ============ STUDENT OPERATIONS ============

def add_student(roll_number, name, email, course, year, division, phone, password_hash, face_encoding=None):
    if is_supabase():
        data = {
            "roll_number": roll_number,
            "name": name,
            "email": email,
            "course": course,
            "year": year,
            "division": division,
            "phone": phone,
            "password_hash": password_hash,
            "face_encoding": face_encoding.tolist() if face_encoding is not None else None
        }
        try:
            response = _supabase.table("students").insert(data).execute()
            return True, response.data[0]['id']
        except Exception as e:
            return False, str(e)
    else:
        conn = get_connection()
        c = conn.cursor()
        try:
            face_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
            c.execute("""
                INSERT INTO students 
                (roll_number, name, email, course, year, division, phone, password_hash, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (roll_number, name, email, course, year, division, phone, password_hash, face_blob))
            conn.commit()
            return True, c.lastrowid
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

def get_student_by_roll(roll_number):
    if is_supabase():
        response = _supabase.table("students").select("*").eq("roll_number", roll_number).eq("is_active", True).execute()
        if response.data:
            student = response.data[0]
            if student['face_encoding']:
                student['face_encoding'] = np.array(student['face_encoding'])
            return student
        return None
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE roll_number = ? AND is_active = 1", (roll_number,))
        row = c.fetchone()
        conn.close()
        if row:
            student = dict(row)
            if row['face_encoding']:
                student['face_encoding'] = pickle.loads(row['face_encoding'])
            return student
        return None

def get_student_by_email(email):
    if is_supabase():
        response = _supabase.table("students").select("*").eq("email", email).eq("is_active", True).execute()
        if response.data:
            student = response.data[0]
            if student['face_encoding']:
                student['face_encoding'] = np.array(student['face_encoding'])
            return student
        return None
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE email = ? AND is_active = 1", (email,))
        row = c.fetchone()
        conn.close()
        if row:
            student = dict(row)
            if row['face_encoding']:
                student['face_encoding'] = pickle.loads(row['face_encoding'])
            return student
        return None

def update_student_face_encoding(student_id, face_encoding):
    if is_supabase():
        _supabase.table("students").update({"face_encoding": face_encoding.tolist()}).eq("id", student_id).execute()
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE students SET face_encoding = ? WHERE id = ?", (pickle.dumps(face_encoding), student_id))
        conn.commit()
        conn.close()

def get_all_students():
    if is_supabase():
        response = _supabase.table("students").select("*").eq("is_active", True).order("roll_number").execute()
        return response.data
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE is_active = 1 ORDER BY roll_number")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def delete_student(student_id):
    if is_supabase():
        _supabase.table("students").update({"is_active": False}).eq("id", student_id).execute()
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE students SET is_active = 0 WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()

# ============ TEACHER OPERATIONS ============

def add_teacher(teacher_id, name, email, phone, password_hash):
    if is_supabase():
        data = {"teacher_id": teacher_id, "name": name, "email": email, "phone": phone, "password_hash": password_hash}
        try:
            response = _supabase.table("teachers").insert(data).execute()
            return True, response.data[0]['id']
        except Exception as e:
            return False, str(e)
    else:
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO teachers (teacher_id, name, email, phone, password_hash) VALUES (?, ?, ?, ?, ?)",
                      (teacher_id, name, email, phone, password_hash))
            conn.commit()
            return True, c.lastrowid
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

def get_teacher_by_id(teacher_id):
    if is_supabase():
        response = _supabase.table("teachers").select("*").eq("teacher_id", teacher_id).eq("is_active", True).execute()
        return response.data[0] if response.data else None
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM teachers WHERE teacher_id = ? AND is_active = 1", (teacher_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

def get_teacher_by_email(email):
    if is_supabase():
        response = _supabase.table("teachers").select("*").eq("email", email).eq("is_active", True).execute()
        return response.data[0] if response.data else None
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM teachers WHERE email = ? AND is_active = 1", (email,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

def get_all_teachers():
    if is_supabase():
        response = _supabase.table("teachers").select("*").eq("is_active", True).order("name").execute()
        return response.data
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM teachers WHERE is_active = 1 ORDER BY name")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def delete_teacher(teacher_id):
    if is_supabase():
        _supabase.table("teachers").update({"is_active": False}).eq("id", teacher_id).execute()
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE teachers SET is_active = 0 WHERE id = ?", (teacher_id,))
        conn.commit()
        conn.close()

# ============ TEACHER ASSIGNMENT OPERATIONS ============

def assign_course_to_teacher(teacher_db_id, course, year, division, subject):
    if is_supabase():
        data = {"teacher_id": teacher_db_id, "course": course, "year": year, "division": division, "subject": subject}
        try:
            _supabase.table("teacher_assignments").insert(data).execute()
            return True, None
        except Exception as e:
            return False, str(e)
    else:
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO teacher_assignments (teacher_id, course, year, division, subject) VALUES (?, ?, ?, ?, ?)",
                      (teacher_db_id, course, year, division, subject))
            conn.commit()
            return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

def get_teacher_assignments(teacher_db_id):
    if is_supabase():
        response = _supabase.table("teacher_assignments").select("*").eq("teacher_id", teacher_db_id).order("course").execute()
        return response.data
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM teacher_assignments WHERE teacher_id = ? ORDER BY course", (teacher_db_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

# ============ SESSION OPERATIONS ============

def create_session(teacher_db_id, course, year, division, subject, session_pin, duration_minutes):
    if is_supabase():
        data = {
            "teacher_id": teacher_db_id,
            "course": course,
            "year": year,
            "division": division,
            "subject": subject,
            "session_pin": session_pin,
            "duration_minutes": duration_minutes,
            "status": "active"
        }
        response = _supabase.table("sessions").insert(data).execute()
        return response.data[0]['id']
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO sessions (teacher_id, course, year, division, subject, session_pin, duration_minutes, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')",
                  (teacher_db_id, course, year, division, subject, session_pin, duration_minutes))
        conn.commit()
        session_id = c.lastrowid
        conn.close()
        return session_id

def get_active_session(session_id):
    if is_supabase():
        response = _supabase.table("sessions").select("*").eq("id", session_id).eq("status", "active").execute()
        return response.data[0] if response.data else None
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE id = ? AND status = 'active'", (session_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

def end_session(session_id):
    if is_supabase():
        _supabase.table("sessions").update({"status": "ended", "end_time": datetime.now().isoformat()}).eq("id", session_id).execute()
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE sessions SET status = 'ended', end_time = ? WHERE id = ?", (datetime.now(), session_id))
        conn.commit()
        conn.close()

def expire_old_sessions():
    if is_supabase():
        try:
            response = _supabase.table("sessions").select("id, start_time, duration_minutes").eq("status", "active").execute()
            
            for session in response.data:
                # Need to handle timezone-aware datetime correctly
                start_str = session['start_time']
                if 'Z' in start_str:
                    start_str = start_str.replace('Z', '+00:00')
                    
                start = datetime.fromisoformat(start_str)
                now = datetime.now(start.tzinfo)
                
                if now > start + timedelta(minutes=session['duration_minutes']):
                    _supabase.table("sessions").update({"status": "ended"}).eq("id", session['id']).execute()
        except Exception as e:
            # Table might not exist yet or connection error
            print(f"Warning: Could not expire sessions: {e}")
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE sessions SET status='ended' WHERE status='active' AND datetime(start_time, '+' || duration_minutes || ' minutes') <= datetime('now')")
        conn.commit()
        conn.close()

def get_sessions_by_teacher(teacher_db_id, limit=20):
    if is_supabase():
        response = _supabase.table("sessions").select("*").eq("teacher_id", teacher_db_id).order("start_time", desc=True).limit(limit).execute()
        return response.data
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE teacher_id = ? ORDER BY start_time DESC LIMIT ?", (teacher_db_id, limit))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_student_active_sessions(course, year, division):
    if is_supabase():
        response = _supabase.table("sessions").select("*").eq("course", course).eq("year", year).eq("division", division).eq("status", "active").execute()
        res = []
        for session in response.data:
            start = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00'))
            if datetime.now(start.tzinfo) <= start + timedelta(minutes=session['duration_minutes']):
                res.append(session)
        return res
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM sessions
            WHERE status='active' AND course=? AND year=? AND division=?
            AND datetime(start_time, '+' || duration_minutes || ' minutes') > datetime('now')
            ORDER BY start_time DESC
        """, (course, year, division))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

# ============ ANALYTICS & ADMIN OPERATIONS ============

def get_admin_stats():
    if is_supabase():
        students = len(_supabase.table("students").select("id").eq("is_active", True).execute().data)
        teachers = len(_supabase.table("teachers").select("id").eq("is_active", True).execute().data)
        active_sessions = len(_supabase.table("sessions").select("id").eq("status", "active").execute().data)
        total_sessions = len(_supabase.table("sessions").select("id").execute().data)
        total_attendance = len(_supabase.table("attendance").select("id").execute().data)
        return {"students": students, "teachers": teachers, "active_sessions": active_sessions, "total_sessions": total_sessions, "total_attendance": total_attendance}
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM students WHERE is_active = 1")
        students = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM teachers WHERE is_active = 1")
        teachers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'")
        active_sessions = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM attendance")
        total_attendance = c.fetchone()[0]
        conn.close()
        return {"students": students, "teachers": teachers, "active_sessions": active_sessions, "total_sessions": total_sessions, "total_attendance": total_attendance}

def get_attendance_status_distribution():
    if is_supabase():
        response = _supabase.table("attendance").select("verification_status").execute()
        stats = {}
        for row in response.data:
            s = row['verification_status']
            stats[s] = stats.get(s, 0) + 1
        return [{"verification_status": k, "count": v} for k, v in stats.items()]
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT verification_status, COUNT(*) as count FROM attendance GROUP BY verification_status")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_recent_sessions_with_teacher(limit=10):
    if is_supabase():
        response = _supabase.table("sessions").select("*, teachers(name)").order("start_time", desc=True).limit(limit).execute()
        for row in response.data:
            row['name'] = row['teachers']['name']
        return response.data
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT s.*, t.name FROM sessions s JOIN teachers t ON s.teacher_id = t.id ORDER BY s.start_time DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_teacher_session_stats():
    if is_supabase():
        teachers = _supabase.table("teachers").select("id, name").execute().data
        sessions = _supabase.table("sessions").select("id, teacher_id, status").execute().data
        stats = []
        for t in teachers:
            t_sessions = [s for s in sessions if s['teacher_id'] == t['id']]
            stats.append({"name": t['name'], "sessions": len(t_sessions), "active_sessions": len([s for s in t_sessions if s['status'] == 'active'])})
        return stats
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT t.name, COUNT(s.id) as sessions, SUM(CASE WHEN s.status='active' THEN 1 ELSE 0 END) as active_sessions FROM teachers t LEFT JOIN sessions s ON t.id = s.teacher_id GROUP BY t.id, t.name ORDER BY sessions DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_daily_attendance_trend(days=30):
    if is_supabase():
        since = (datetime.now() - timedelta(days=days)).isoformat()
        response = _supabase.table("attendance").select("mark_time").gte("mark_time", since).execute()
        trends = {}
        for row in response.data:
            date = row['mark_time'].split('T')[0]
            trends[date] = trends.get(date, 0) + 1
        return sorted([{"date": k, "count": v} for k, v in trends.items()], key=lambda x: x['date'])
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT DATE(mark_time) as date, COUNT(*) as count FROM attendance WHERE mark_time >= datetime('now', '-30 days') GROUP BY DATE(mark_time) ORDER BY date")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

# ============ ATTENDANCE OPERATIONS ============

def mark_attendance(session_id, student_id, roll_number, verification_status='face_verified'):
    if is_supabase():
        data = {"session_id": session_id, "student_id": student_id, "roll_number": roll_number, "verification_status": verification_status}
        try:
            _supabase.table("attendance").insert(data).execute()
            return True, None
        except Exception:
            return False, "Already marked"
    else:
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO attendance (session_id, student_id, roll_number, verification_status) VALUES (?, ?, ?, ?)",
                      (session_id, student_id, roll_number, verification_status))
            conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            return False, "Already marked"
        finally:
            conn.close()

def check_attendance_exists(session_id, student_id):
    if is_supabase():
        response = _supabase.table("attendance").select("id").eq("session_id", session_id).eq("student_id", student_id).execute()
        return len(response.data) > 0
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM attendance WHERE session_id = ? AND student_id = ?", (session_id, student_id))
        res = c.fetchone()
        conn.close()
        return res is not None

def get_session_attendance(session_id):
    if is_supabase():
        response = _supabase.table("attendance").select("*, students(name)").eq("session_id", session_id).execute()
        for row in response.data:
            row['name'] = row['students']['name']
        return response.data
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT a.*, s.name FROM attendance a JOIN students s ON a.student_id = s.id WHERE a.session_id = ?", (session_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_student_attendance_by_roll(roll_number):
    if is_supabase():
        response = _supabase.table("attendance").select("*, sessions(*)").eq("roll_number", roll_number).execute()
        res = []
        for row in response.data:
            if not row['sessions']: continue
            s = row['sessions']
            res.append({"mark_time": row['mark_time'], "verification_status": row['verification_status'],
                        "subject": s['subject'], "course": s['course'], "year": s['year'], "division": s['division']})
        return res
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT a.mark_time, a.verification_status, ss.subject, ss.course, ss.year, ss.division FROM attendance a JOIN sessions ss ON a.session_id = ss.id WHERE a.roll_number = ?", (roll_number,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_attendance_logs(teacher_db_id=None, course=None, date_from=None, date_to=None):
    if is_supabase():
        query = _supabase.table("attendance").select("*, students(name, roll_number), sessions(*)")
        if teacher_db_id: query = query.eq("sessions.teacher_id", teacher_db_id)
        if course: query = query.eq("sessions.course", course)
        if date_from: query = query.gte("mark_time", date_from)
        if date_to: query = query.lte("mark_time", date_to)
        response = query.execute()
        res = []
        for row in response.data:
            if not row['sessions']: continue
            res.append({"roll_number": row['students']['roll_number'], "name": row['students']['name'],
                        "subject": row['sessions']['subject'], "course": row['sessions']['course'],
                        "mark_time": row['mark_time'], "verification_status": row['verification_status']})
        return res
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT st.roll_number, st.name, ss.subject, ss.course, a.mark_time, a.verification_status FROM attendance a JOIN students st ON a.student_id = st.id JOIN sessions ss ON a.session_id = ss.id")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_attendance_summary(session_id):
    if is_supabase():
        session = _supabase.table("sessions").select("*").eq("id", session_id).execute().data[0]
        attended = len(_supabase.table("attendance").select("id").eq("session_id", session_id).execute().data)
        total = len(_supabase.table("students").select("id").eq("course", session['course']).eq("year", session['year']).eq("division", session['division']).eq("is_active", True).execute().data)
        return {"session": session, "attended": attended, "total": total, "absent": total - attended}
    else:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        res = c.fetchone()
        if not res: return None
        session = dict(res)
        c.execute("SELECT COUNT(*) as count FROM attendance WHERE session_id = ?", (session_id,))
        attended = c.fetchone()['count']
        c.execute("SELECT COUNT(*) as count FROM students WHERE course = ? AND year = ? AND division = ?", (session['course'], session['year'], session['division']))
        total = c.fetchone()['count']
        conn.close()
        return {"session": session, "attended": attended, "total": total, "absent": total - attended}
