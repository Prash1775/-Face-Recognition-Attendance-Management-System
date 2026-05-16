import hashlib
import streamlit as st
from components import db

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    """Verify password against stored hash"""
    return stored_hash == hash_password(provided_password)

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'teacher_db_id' not in st.session_state:
        st.session_state.teacher_db_id = None
    if 'student_db_id' not in st.session_state:
        st.session_state.student_db_id = None

def login_student(roll_number, password):
    """Authenticate student with roll number and password"""
    student = db.get_student_by_roll(roll_number)
    
    if not student:
        return False, "Roll number not found"
    
    if not verify_password(student['password_hash'], password):
        return False, "Incorrect password"
    
    # Set session state
    st.session_state.logged_in = True
    st.session_state.user_role = "student"
    st.session_state.user_id = student['roll_number']
    st.session_state.user_name = student['name']
    st.session_state.user_email = student['email']
    st.session_state.student_db_id = student['id']
    
    return True, f"Welcome {student['name']}!"

def login_teacher(teacher_id, password):
    """Authenticate teacher with teacher ID and password"""
    teacher = db.get_teacher_by_id(teacher_id)
    
    if not teacher:
        return False, "Teacher ID not found"
    
    if not verify_password(teacher['password_hash'], password):
        return False, "Incorrect password"
    
    # Set session state
    st.session_state.logged_in = True
    st.session_state.user_role = "teacher"
    st.session_state.user_id = teacher['teacher_id']
    st.session_state.user_name = teacher['name']
    st.session_state.user_email = teacher['email']
    st.session_state.teacher_db_id = teacher['id']
    
    return True, f"Welcome {teacher['name']}!"

def login_admin(admin_password):
    """Authenticate admin with password"""
    # Admin password hash (initially "admin123")
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    
    if not verify_password(admin_hash, admin_password):
        return False, "Incorrect admin password"
    
    st.session_state.logged_in = True
    st.session_state.user_role = "admin"
    st.session_state.user_id = "admin"
    st.session_state.user_name = "Administrator"
    
    return True, "Welcome Administrator!"

def logout():
    """Logout current user"""
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.current_session_id = None
    st.session_state.teacher_db_id = None
    st.session_state.student_db_id = None

def is_logged_in():
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)

def get_current_user():
    """Get current logged-in user info"""
    if not is_logged_in():
        return None
    
    return {
        'role': st.session_state.get('user_role'),
        'id': st.session_state.get('user_id'),
        'name': st.session_state.get('user_name'),
        'email': st.session_state.get('user_email'),
        'student_db_id': st.session_state.get('student_db_id'),
        'teacher_db_id': st.session_state.get('teacher_db_id')
    }

def require_login(required_role=None):
    """
    Decorator to require login for a page
    
    Args:
        required_role: str or list of str for required role(s)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                st.error("Please login first")
                st.stop()
            
            if required_role:
                user_role = st.session_state.get('user_role')
                allowed_roles = required_role if isinstance(required_role, list) else [required_role]
                
                if user_role not in allowed_roles:
                    st.error(f"This page requires {required_role} access")
                    st.stop()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
