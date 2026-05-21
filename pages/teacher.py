import streamlit as st
from components import db, auth, utils

COLLEGE_NAME = "Department of Technology, Pune"


def main():
    st.set_page_config(page_title="Teacher Portal - Attendance System", layout="wide")

    st.markdown(
        f"<h1 style='text-align: center; color: #1f77b4;'>{COLLEGE_NAME}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='text-align: center;'>Teacher Attendance Portal</h3>",
        unsafe_allow_html=True
    )
    st.divider()

    if not auth.is_logged_in():
        show_login_page()
    else:
        user = auth.get_current_user()
        if user["role"] == "teacher":
            show_teacher_dashboard()
        else:
            st.error("This page is for teachers only")


def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Teacher Login")

        with st.form("teacher_login_form"):
            teacher_id = st.text_input("Teacher ID", placeholder="e.g., TECH001")
            password = st.text_input("Password", type="password")

            submit = st.form_submit_button("Login", use_container_width=False)

            if submit:
                if not teacher_id or not password:
                    st.error("Please fill all fields")
                    return

                success, message = auth.login_teacher(teacher_id, password)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def show_teacher_dashboard():
    user = auth.get_current_user()

    st.sidebar.write(f"**Welcome, {user['name']}!**")
    st.sidebar.write(f"Teacher ID: {user['id']}")

    if st.sidebar.button("Logout", use_container_width=False):
        auth.logout()
        st.rerun()

    st.sidebar.divider()

    menu = st.sidebar.radio(
        "Select Option",
        ["Start Session", "Active Sessions", "View Attendance", "Session History"]
    )

    if menu == "Start Session":
        show_start_session_page(user)
    elif menu == "Active Sessions":
        show_active_sessions(user)
    elif menu == "View Attendance":
        show_attendance_view(user)
    elif menu == "Session History":
        show_session_history(user)


def show_start_session_page(user):
    st.header("Start Attendance Session")

    assignments = db.get_teacher_assignments(user["teacher_db_id"])

    if not assignments:
        st.warning("No course assignments found")
        return

    assignment_options = [
        f"{a['subject']} - {a['course']} ({a['year']} {a['division']})"
        for a in assignments
    ]

    selected_idx = st.selectbox(
        "Select Course",
        range(len(assignment_options)),
        format_func=lambda i: assignment_options[i]
    )

    assignment = assignments[selected_idx]

    duration = st.number_input(
        "Session Duration (minutes)",
        min_value=1,
        max_value=180,
        value=5
    )

    if st.button("Start Session", use_container_width=False):
        session_pin = utils.generate_pin(length=4)

        session_id = db.create_session(
            teacher_db_id=int(user["teacher_db_id"]),
            course=assignment["course"],
            year=assignment["year"],
            division=assignment["division"],
            subject=assignment["subject"],
            session_pin=session_pin,
            duration_minutes=duration
        )

        st.success("✅ Session started successfully!")
        st.info(f"🆔 Session ID: {session_id}")
        st.info(f"🔑 Session PIN: {session_pin}")


def show_active_sessions(user):
    st.header("Active Sessions")

    sessions = db.get_sessions_by_teacher(user["teacher_db_id"], limit=20)

    active_sessions = [s for s in sessions if s["status"] == "active"]

    if not active_sessions:
        st.info("No active sessions")
        return

    for session in active_sessions:
        with st.container(border=True):
            st.write(f"📘 Subject: {session['subject']}")
            st.write(f"🎓 {session['course']} - {session['year']} {session['division']}")
            st.write(f"🕒 Started: {session['start_time']}")
            st.write(f"🔑 PIN: {session['session_pin']}")

            if st.button(f"End Session {session['id']}"):
                db.end_session(session["id"])
                st.success("✅ Session ended")
                st.rerun()


@st.dialog("Detailed Attendance List", width="large")
def show_detailed_attendance_dialog(session_id, subject, date_str):
    st.write(f"##### Detailed Attendance List for {subject} on {date_str}")
    details = db.get_attendance_by_session(session_id)
    
    if details:
        import pandas as pd
        formatted_details = []
        for d in details:
            mark_time = d.get("mark_time", "")
            try:
                dt = pd.to_datetime(mark_time)
                date_val = dt.strftime('%Y-%m-%d')
                time_val = dt.strftime('%I:%M %p')
            except:
                date_val = ""
                time_val = mark_time
                
            formatted_details.append({
                "Student Name": d.get("name", ""),
                "Roll Number": d.get("roll_number", ""),
                "Status": d.get("status", ""),
                "Subject": subject,
                "Date": date_val,
                "Time": time_val
            })
        
        df_details = pd.DataFrame(formatted_details)
        st.table(df_details)
        
        csv = df_details.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Details (CSV)", data=csv, file_name=f"detailed_attendance_{session_id}.csv", mime="text/csv", key=f"dl_{session_id}")
    else:
        st.info("No detailed records found for this session.")

def show_attendance_view(user):
    st.write("### View Session Attendance")

    sessions = db.get_sessions_by_teacher(user["teacher_db_id"], limit=50)

    if not sessions:
        st.info("No sessions yet")
        return

    st.write("#### Date-wise Attendance Summary")
    
    # Extract unique subjects and courses and dates for filters
    subjects = list(set([s["subject"] for s in sessions]))
    subjects.insert(0, "All Subjects")
    
    courses = list(set([f"{s['course']} {s['year']} {s['division']}" for s in sessions]))
    courses.insert(0, "All Courses")
    
    dates = []
    for s in sessions:
        try:
            d = str(s['start_time']).split(' ')[0]
            if d not in dates:
                dates.append(d)
        except: pass
    dates.sort(reverse=True)
    dates.insert(0, "All Dates")
    
    col1, col2, col3 = st.columns(3)
    selected_subject = col1.selectbox("Filter by Subject", subjects)
    selected_course = col2.selectbox("Filter by Course", courses)
    selected_date = col3.selectbox("Filter by Date", dates)

    # Filter sessions first
    filtered_sessions = []
    for s in sessions:
        course_str = f"{s['course']} {s['year']} {s['division']}"
        try:
            date_str = str(s['start_time']).split(' ')[0] 
        except:
            date_str = str(s['start_time'])
            
        if selected_subject != "All Subjects" and s["subject"] != selected_subject:
            continue
        if selected_course != "All Courses" and course_str != selected_course:
            continue
        if selected_date != "All Dates" and date_str != selected_date:
            continue
        
        # Add the string versions so we don't recalculate
        s['_course_str'] = course_str
        s['_date_str'] = date_str
        filtered_sessions.append(s)

    if not filtered_sessions:
        st.info("No matching summary data available")
        return

    # Render table header
    header_cols = st.columns([1.5, 2, 2, 2, 1, 1, 1])
    header_cols[0].markdown("**Action**")
    header_cols[1].markdown("**Date**")
    header_cols[2].markdown("**Subject**")
    header_cols[3].markdown("**Course**")
    header_cols[4].markdown("**Total**")
    header_cols[5].markdown("**Present**")
    header_cols[6].markdown("**Absent**")
    
    st.divider()

    for s in filtered_sessions:
        summary = db.get_attendance_summary(s["id"])
        if summary:
            total = summary['total']
            present = summary['attended']
            absent = summary['absent']
            
            cols = st.columns([1.5, 2, 2, 2, 1, 1, 1])
            
            if cols[0].button("Show Attendance", key=f"btn_show_{s['id']}"):
                show_detailed_attendance_dialog(s["id"], s["subject"], s["_date_str"])
                
            cols[1].write(s['_date_str'])
            cols[2].write(s["subject"])
            cols[3].write(s['_course_str'])
            cols[4].write(str(total))
            cols[5].write(str(present))
            cols[6].write(str(absent))
            
            st.divider()


def show_session_history(user):
    st.write("### Session History")

    sessions = db.get_sessions_by_teacher(user["teacher_db_id"], limit=100)

    if not sessions:
        st.info("No session history")
        return

    # Extract dates for filter
    dates = []
    for s in sessions:
        try:
            d = str(s['start_time']).split(' ')[0]
            if d not in dates:
                dates.append(d)
        except: pass
    dates.sort(reverse=True)
    dates.insert(0, "All Dates")
    
    selected_date = st.selectbox("Filter History by Date", dates)
    
    # Filter sessions
    filtered_sessions = sessions
    if selected_date != "All Dates":
        filtered_sessions = [s for s in sessions if str(s['start_time']).startswith(selected_date)]

    if not filtered_sessions:
        st.info("No sessions match the selected date.")
        
    for session in filtered_sessions:
        with st.container(border=True):
            st.write(f"**{session['subject']}** ({session['course']})")
            st.write(f"Year {session['year']}, Division {session['division']}")
            st.write(f"Started: {session['start_time']}")
            st.write(f"Status: {session['status']}")
            
            # Show attendance numbers
            summary = db.get_attendance_summary(session["id"])
            if summary:
                total = summary.get('total', 0)
                present = summary.get('attended', 0)
                absent = summary.get('absent', 0)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Expected", total)
                col2.metric("Present", present)
                col3.metric("Absent", absent)


if __name__ == "__main__":
    auth.init_session_state()
    db.init_db()
    main()
