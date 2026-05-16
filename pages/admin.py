import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components import db, auth, utils
from datetime import datetime, timedelta

COLLEGE_NAME = "Department of Technology, Pune"

def main():
    st.set_page_config(page_title="Admin Dashboard - Attendance System", layout="wide")
    
    # College header
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{COLLEGE_NAME}</h1>", 
                unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Administration Dashboard</h3>", 
                unsafe_allow_html=True)
    st.divider()
    
    # Check if logged in as admin
    if not auth.is_logged_in():
        show_admin_login()
    else:
        user = auth.get_current_user()
        if user['role'] == 'admin':
            show_admin_dashboard()
        else:
            st.error("This page is for administrators only")

def show_admin_login():
    """Admin login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Administrator Login")
        
        with st.form("admin_login_form"):
            password = st.text_input("Admin Password", type="password")
            submit = st.form_submit_button("Login", width='stretch')
            
            if submit:
                if not password:
                    st.error("Please enter password")
                    return
                
                success, message = auth.login_admin(password)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def show_admin_dashboard():
    """Main admin dashboard"""
    user = auth.get_current_user()
    
    st.sidebar.write(f"**Welcome, {user['name']}!**")
    
    if st.sidebar.button("Logout", width='stretch'):
        auth.logout()
        st.rerun()
    
    st.sidebar.divider()
    
    # Menu options
    menu = st.sidebar.radio(
        "Select Option",
        [
            "Dashboard Overview",
            "Student Management",
            "Teacher Management",
            "Attendance Logs",
            "Analytics Reports"
        ]
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

def show_dashboard_overview():
    db.expire_old_sessions()
    st.write("### Dashboard Overview")
    
    # Get statistics
    stats = db.get_admin_stats()
    students = db.get_all_students()
    teachers = db.get_all_teachers()
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", stats['students'])
    
    with col2:
        st.metric("Total Teachers", stats['teachers'])
    
    with col3:
        st.metric("Active Sessions", stats['active_sessions'])
    
    with col4:
        st.metric("Total Sessions", stats['total_sessions'])
    
    with col5:
        st.metric("Total Attendance", stats['total_attendance'])
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    # Student distribution by course
    with col1:
        if students:
            course_data = pd.DataFrame(students)
            course_counts = course_data['course'].value_counts()
            
            fig = px.pie(
                values=course_counts.values,
                names=course_counts.index,
                title="Student Distribution by Course",
                hole=0.3
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No students enrolled yet")
    
    # Attendance by verification status
    with col2:
        status_data = db.get_attendance_status_distribution()
        
        if status_data:
            status_df = pd.DataFrame(status_data)
            fig = px.bar(
                status_df,
                x='verification_status',
                y='count',
                title="Attendance Verification Status",
                labels={'verification_status': 'Status', 'count': 'Count'}
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No attendance data yet")
    
    st.divider()
    
    # Recent sessions
    st.write("### Recent Sessions")
    
    recent_sessions = db.get_recent_sessions_with_teacher(limit=10)
    
    if recent_sessions:
        display_data = []
        for session in recent_sessions:
            summary = db.get_attendance_summary(session['id'])
            display_data.append({
                'Teacher': session['name'],
                'Subject': session['subject'],
                'Course': session['course'],
                'Started': utils.format_datetime(session['start_time']),
                'Status': session['status'],
                'Attendance': f"{summary['attended']}/{summary['total']}"
            })
        
        st.dataframe(display_data, width='stretch', hide_index=True)

def show_student_management():
    """Student management interface"""
    st.write("### Student Management")
    
    tab1, tab2, tab3 = st.tabs(["View Students", "Add Student", "Delete Student"])
    
    with tab1:
        show_student_list()
    
    with tab2:
        show_add_student_form()
    
    with tab3:
        show_delete_student_form()

def show_student_list():
    """Display all students"""
    students = db.get_all_students()
    
    if not students:
        st.info("No students enrolled")
        return
    
    # Create dataframe
    df = pd.DataFrame(students)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        course_filter = st.multiselect(
            "Filter by Course",
            df['course'].unique(),
            default=None
        )
    
    with col2:
        year_filter = st.multiselect(
            "Filter by Year",
            df['year'].unique(),
            default=None
        )
    
    with col3:
        division_filter = st.multiselect(
            "Filter by Division",
            df['division'].unique(),
            default=None
        )
    
    # Apply filters
    filtered_df = df.copy()
    if course_filter:
        filtered_df = filtered_df[filtered_df['course'].isin(course_filter)]
    if year_filter:
        filtered_df = filtered_df[filtered_df['year'].isin(year_filter)]
    if division_filter:
        filtered_df = filtered_df[filtered_df['division'].isin(division_filter)]
    
    # Display table
    display_df = filtered_df[['roll_number', 'name', 'email', 'course', 'year', 'division', 'phone']]
    st.dataframe(display_df, width='stretch', hide_index=True)
    
    # Export options
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = utils.dataframe_to_csv_bytes(display_df)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name="students_list.csv",
            mime="text/csv",
            width='stretch'
        )
    
    with col2:
        st.write("Total: " + str(len(filtered_df)))

def show_add_student_form():
    """Form to add new student"""
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            roll_number = st.text_input("Roll Number")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
        
        with col2:
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")
        
        courses, years, divisions = utils.get_course_year_division_options()
        
        col1, col2 = st.columns(2)
        
        with col1:
            course = st.selectbox("Course", courses, key="add_course")
            year = st.selectbox("Year", years, key="add_year")
        
        with col2:
            division = st.selectbox("Division", divisions, key="add_division")
        
        submit = st.form_submit_button("Add Student", width='stretch')
        
        if submit:
            if not all([roll_number, name, email, phone, password]):
                st.error("Please fill all fields")
                return
            
            password_hash = auth.hash_password(password)
            
            success, msg = db.add_student(
                roll_number=roll_number,
                name=name,
                email=email,
                course=course,
                year=year,
                division=division,
                phone=phone,
                password_hash=password_hash,
                face_encoding=None
            )
            
            if success:
                st.success(f"✅ Student added: {roll_number}")
            else:
                st.error(f"Error: {msg}")

def show_delete_student_form():
    """Form to delete student"""
    students = db.get_all_students()
    
    if not students:
        st.info("No students to delete")
        return
    
    student_options = {f"{s['roll_number']} - {s['name']}": s for s in students}
    
    selected = st.selectbox("Select Student to Delete", list(student_options.keys()))
    student = student_options[selected]
    
    st.warning(f"⚠️ This will delete {student['name']} (Roll: {student['roll_number']})")
    
    if st.button("Delete Student", width='stretch'):
        db.delete_student(student['id'])
        st.success("✅ Student deleted")
        st.rerun()

def show_teacher_management():
    """Teacher management interface"""
    st.write("### Teacher Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "View Teachers",
        "Add Teacher",
        "Assign Courses",
        "Delete Teacher"
    ])
    
    with tab1:
        show_teacher_list()
    
    with tab2:
        show_add_teacher_form()
    
    with tab3:
        show_assign_courses_form()
    
    with tab4:
        show_delete_teacher_form()

def show_teacher_list():
    """Display all teachers"""
    teachers = db.get_all_teachers()
    
    if not teachers:
        st.info("No teachers registered")
        return
    
    for teacher in teachers:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{teacher['name']}** (ID: {teacher['teacher_id']})")
                st.write(f"Email: {teacher['email']}")
                st.write(f"Phone: {teacher['phone']}")
            
            with col2:
                # Show assignments count
                assignments = db.get_teacher_assignments(teacher['id'])
                st.write(f"Assignments: {len(assignments)}")
            
            with col3:
                if st.button("View Details", key=f"view_{teacher['id']}", use_container_width=False):
                    show_teacher_details(teacher)

def show_teacher_details(teacher):
    """Show teacher details in expander"""
    with st.expander(f"Details: {teacher['name']}"):
        assignments = db.get_teacher_assignments(teacher['id'])
        
        st.write("**Assigned Courses:**")
        
        if assignments:
            for assign in assignments:
                st.write(f"- {assign['course']} (Year {assign['year']}, Division {assign['division']}) - {assign['subject']}")
        else:
            st.write("No course assignments")

def show_add_teacher_form():
    """Form to add new teacher"""
    with st.form("add_teacher_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            teacher_id = st.text_input("Teacher ID")
            name = st.text_input("Full Name")
        
        with col2:
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        password = st.text_input("Password", type="password")
        
        submit = st.form_submit_button("Add Teacher", use_container_width=False)
        
        if submit:
            if not all([teacher_id, name, email, phone, password]):
                st.error("Please fill all fields")
                return
            
            password_hash = auth.hash_password(password)
            
            success, msg = db.add_teacher(
                teacher_id=teacher_id,
                name=name,
                email=email,
                phone=phone,
                password_hash=password_hash
            )
            
            if success:
                st.success(f"✅ Teacher added: {teacher_id}")
            else:
                st.error(f"Error: {msg}")

def show_assign_courses_form():
    """Form to assign courses to teachers"""
    teachers = db.get_all_teachers()
    
    if not teachers:
        st.info("No teachers registered")
        return
    
    teacher_options = {f"{t['teacher_id']} - {t['name']}": t for t in teachers}
    
    selected_teacher = st.selectbox("Select Teacher", list(teacher_options.keys()))
    teacher = teacher_options[selected_teacher]
    
    courses, years, divisions = utils.get_course_year_division_options()
    
    with st.form("assign_course_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            course = st.selectbox("Course", courses, key="assign_course")
            year = st.selectbox("Year", years, key="assign_year")
        
        with col2:
            division = st.selectbox("Division", divisions, key="assign_div")
        
        with col3:
            subject = st.text_input("Subject Name")
        
        submit = st.form_submit_button("Assign Course", use_container_width=False)
        
        if submit:
            if not subject:
                st.error("Please enter subject name")
                return
            
            success, msg = db.assign_course_to_teacher(
                teacher_db_id=teacher['id'],
                course=course,
                year=year,
                division=division,
                subject=subject
            )
            
            if success:
                st.success("✅ Course assigned")
            else:
                st.error(f"Error: {msg}")

def show_delete_teacher_form():
    """Form to delete teacher"""
    teachers = db.get_all_teachers()
    
    if not teachers:
        st.info("No teachers to delete")
        return
    
    teacher_options = {f"{t['teacher_id']} - {t['name']}": t for t in teachers}
    
    selected = st.selectbox("Select Teacher to Delete", list(teacher_options.keys()))
    teacher = teacher_options[selected]
    
    st.warning(f"⚠️ This will delete {teacher['name']}")
    
    if st.button("Delete Teacher", use_container_width=False):
        db.delete_teacher(teacher['id'])
        st.success("✅ Teacher deleted")
        st.rerun()

def show_attendance_logs():
    """View and filter attendance logs"""
    st.write("### Attendance Logs")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        teachers = db.get_all_teachers()
        teacher_options = {f"{t['teacher_id']} - {t['name']}": t['id'] for t in teachers}
        teacher_filter = st.selectbox("Filter by Teacher", ["All"] + list(teacher_options.keys()))
        teacher_id = teacher_options[teacher_filter] if teacher_filter != "All" else None
    
    with col2:
        students = db.get_all_students()
        courses = list(set([s['course'] for s in students]))
        course_filter = st.selectbox("Filter by Course", ["All"] + courses)
        course = course_filter if course_filter != "All" else None
    
    with col3:
        date_range = st.date_input("Date Range", value=(datetime.now().date() - timedelta(days=30), datetime.now().date()), max_value=datetime.now().date())
        if len(date_range) == 2:
            date_from, date_to = date_range
        else:
            date_from = date_to = date_range[0]
    
    # Get logs
    logs = db.get_attendance_logs(
        teacher_db_id=teacher_id,
        course=course,
        date_from=date_from,
        date_to=date_to
    )
    
    if logs:
        display_data = []
        for log in logs:
            display_data.append({
                'Roll No': log['roll_number'],
                'Name': log['name'],
                'Subject': log['subject'],
                'Course': log['course'],
                'Date': utils.format_datetime(log['mark_time']),
                'Status': log['verification_status']
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=False, hide_index=True)
        
        # Export
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = utils.dataframe_to_csv_bytes(df)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name="attendance_logs.csv",
                mime="text/csv",
                use_container_width=False
            )
        
        with col2:
            st.write(f"Total Records: {len(df)}")
    else:
        st.info("No attendance logs found")

def show_analytics_reports():
    """Analytics and reports"""
    st.write("### Analytics Reports")
    
    tab1, tab2, tab3 = st.tabs(["Course Analytics", "Teacher Analytics", "Attendance Trends"])
    
    with tab1:
        show_course_analytics()
    
    with tab2:
        show_teacher_analytics()
    
    with tab3:
        show_attendance_trends()

def show_course_analytics():
    """Course-wise analytics"""
    students = db.get_all_students()
    
    if not students:
        st.info("No data available")
        return
    
    df = pd.DataFrame(students)
    
    col1, col2 = st.columns(2)
    
    with col1:
        course_year = df.groupby(['course', 'year']).size().reset_index(name='count')
        fig = px.bar(
            course_year,
            x='course',
            y='count',
            color='year',
            title="Student Distribution by Course and Year",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=False)
    
    with col2:
        course_div = df.groupby(['course', 'division']).size().reset_index(name='count')
        fig = px.bar(
            course_div,
            x='course',
            y='count',
            color='division',
            title="Student Distribution by Division",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=False)

def show_teacher_analytics():
    """Teacher and session analytics"""
    teacher_stats_data = db.get_teacher_session_stats()
    teacher_stats = pd.DataFrame(teacher_stats_data)
    
    if not teacher_stats.empty:
        fig = px.bar(
            teacher_stats,
            x='name',
            y='sessions',
            title="Sessions by Teacher",
            labels={'name': 'Teacher', 'sessions': 'Total Sessions'}
        )
        st.plotly_chart(fig, use_container_width=False)
    else:
        st.info("No session data yet")

def show_attendance_trends():
    """Attendance trends over time"""
    data = db.get_daily_attendance_trend(days=30)
    
    if data:
        df = pd.DataFrame(data)
        fig = px.line(
            df,
            x='date',
            y='count',
            title="Daily Attendance Trend (Last 30 Days)",
            markers=True,
            labels={'date': 'Date', 'count': 'Attendance Count'}
        )
        st.plotly_chart(fig, use_container_width=False)
    else:
        st.info("No attendance data yet")

if __name__ == "__main__":
    auth.init_session_state()
    db.init_db()
    main()
