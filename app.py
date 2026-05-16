import streamlit as st
from components import db, auth

COLLEGE_NAME = "Department of Technology, Pune"

# Page configuration
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_app():
    """Initialize app"""
    auth.init_session_state()
    db.init_db()
    
    st.markdown("""
    <style>
    /* Modern Streamlit UI Overrides */
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Custom Sidebar UI */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Modern Gradient Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3), 0 4px 6px -2px rgba(37, 99, 235, 0.15) !important;
    }
    
    /* Form & Input Fields */
    div[data-testid="stForm"] {
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid #30363d;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    div[data-baseweb="input"] {
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    
    /* Typography Overrides */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    db.expire_old_sessions()
    db.init_db()
    """Main app entry point"""
    init_app()
    
    # Check if user is logged in
    if not auth.is_logged_in():
        show_home_page()
    else:
        show_role_based_page()

def show_home_page():
    """Home page with role selection"""
    # College header
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{COLLEGE_NAME}</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Face Recognition Attendance Management System</h2>", 
                unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("### Welcome! Please select your role to login")
        
        role = st.radio(
            "Select Role:",
            ["Student", "Teacher", "Administrator"],
            horizontal=True
        )
        
        st.divider()
        
        if role == "Student":
            show_student_login()
        elif role == "Teacher":
            show_teacher_login()
        elif role == "Administrator":
            show_admin_login()

def show_student_login():
    """Student login section"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🎓 Student Login")
        with st.form("home_student_login"):
            roll_number = st.text_input("Roll Number", placeholder="e.g., DATA001")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=False)
            if submit:
                if not roll_number or not password:
                    st.error("Please fill all fields")
                else:
                    success, message = auth.login_student(roll_number, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        st.info("**New Student?** Register from the Student Portal after logging in for the first time, or contact your administrator.")

def show_teacher_login():
    """Teacher login section"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 👨‍🏫 Teacher Login")
        with st.form("home_teacher_login"):
            teacher_id = st.text_input("Teacher ID", placeholder="e.g., TECH001")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=False)
            if submit:
                if not teacher_id or not password:
                    st.error("Please fill all fields")
                else:
                    success, message = auth.login_teacher(teacher_id, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        st.info("**Note:** Contact administrator for teacher account creation and course assignments.")

def show_admin_login():
    """Admin login section"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Administrator Login")
        with st.form("home_admin_login"):
            password = st.text_input("Admin Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=False)
            if submit:
                if not password:
                    st.error("Please enter password")
                else:
                    success, message = auth.login_admin(password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        st.info("**Default Password:** admin123 (Please change this in production)")

def show_role_based_page():
    """Route to appropriate page based on user role"""
    user = auth.get_current_user()
    
    # Sidebar
    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.write(f"**Role:** {user['role'].title()}")
    
    if user['role'] == 'student':
        st.sidebar.write(f"**ID:** {user['id']}")
    elif user['role'] == 'teacher':
        st.sidebar.write(f"**ID:** {user['id']}")
    
    st.sidebar.divider()
    
    # Navigation menu based on role
    if user['role'] == 'student':
        show_student_navigation()
    elif user['role'] == 'teacher':
        show_teacher_navigation()
    elif user['role'] == 'admin':
        show_admin_navigation()
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Logout", use_container_width=False):
        auth.logout()
        st.rerun()

def show_student_navigation():
    """Student navigation menu"""
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{COLLEGE_NAME}</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Student Attendance Portal</h3>", 
                unsafe_allow_html=True)
    st.divider()
    
    user = auth.get_current_user()
    
    menu = st.sidebar.radio(
        "Navigation",
        ["Mark Attendance", "View Attendance", "Profile"]
    )
    
    # Import student page functions
    from pages.student import (
        show_mark_attendance_page,
        show_attendance_view,
        show_profile_page
    )
    
    if menu == "Mark Attendance":
        show_mark_attendance_page(user)
    elif menu == "View Attendance":
        show_attendance_view(user)
    elif menu == "Profile":
        show_profile_page(user)

def show_teacher_navigation():
    """Teacher navigation menu"""
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{COLLEGE_NAME}</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Teacher Attendance Portal</h3>", 
                unsafe_allow_html=True)
    st.divider()
    
    user = auth.get_current_user()
    
    menu = st.sidebar.radio(
        "Navigation",
        ["Start Session", "Active Sessions", "View Attendance", "Session History"]
    )
    
    # Import teacher page functions
    from pages.teacher import (
        show_start_session_page,
        show_active_sessions,
        show_attendance_view as show_teacher_attendance,
        show_session_history
    )
    
    if menu == "Start Session":
        show_start_session_page(user)
    elif menu == "Active Sessions":
        show_active_sessions(user)
    elif menu == "View Attendance":
        show_teacher_attendance(user)
    elif menu == "Session History":
        show_session_history(user)

def show_admin_navigation():
    """Admin navigation menu"""
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{COLLEGE_NAME}</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Administration Dashboard</h3>", 
                unsafe_allow_html=True)
    st.divider()
    
    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard Overview",
            "Student Management",
            "Teacher Management",
            "Attendance Logs",
            "Analytics Reports"
        ]
    )
    
    # Import admin page functions
    from pages.admin import (
        show_dashboard_overview,
        show_student_management,
        show_teacher_management,
        show_attendance_logs,
        show_analytics_reports
    )
    
    if menu == "Dashboard Overview":
        show_dashboard_overview()
    elif menu == "Student Management":
        show_student_management()
    elif menu == "Teacher Management":
        show_teacher_management()
    elif menu == "Attendance Logs":
        show_attendance_logs()
    elif menu == "Analytics Reports":
        show_analytics_reports()

if __name__ == "__main__":
    main()
