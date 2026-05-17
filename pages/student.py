import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from PIL import Image
from components import db

def show_profile_page(user):
    st.header("Profile & Face Registration")

    student = db.get_student_by_roll(user['id'])
    if not student:
        st.error("Student not found")
        return

    st.write(f"Name: {student['name']}")
    st.write(f"Roll Number: {student['roll_number']}")
    st.write(f"Email: {student['email']}")

    img_file = None
    if st.toggle("📷 Activate Webcam for Registration"):
        img_file = st.camera_input("Take a photo with your webcam")

    if img_file is not None:
        # Use MD5 hash of actual image bytes as cache key.
        # filename+size was identical for different photos (same webcam name, similar JPEG sizes)
        # causing retries to always return the cached failure without re-processing.
        import hashlib
        image_bytes = img_file.getvalue()
        image_key = f"reg_{hashlib.md5(image_bytes).hexdigest()}"

        if image_key not in st.session_state:
            with st.spinner("⚙️ Analyzing face image..."):
                from components import face_engine
                img = Image.open(img_file)
                img.load()  # Force PIL decode before thumbnail
                img.thumbnail((640, 640))

                encoding = face_engine.extract_face_encoding(img)

                if encoding is not None:
                    db.update_student_face_encoding(student['id'], encoding)
                    st.session_state[image_key] = "success"
                    st.success("✅ Face registered successfully! You can turn off the webcam toggle now.")
                    st.rerun()
                else:
                    st.session_state[image_key] = "fail"
                    # Capture diagnostic errors
                    diag_errs = st.session_state.get("face_diagnostic_errors", [])
                    st.session_state[f"{image_key}_diags"] = diag_errs
                    if diag_errs:
                        st.error("❌ Face detection failed details:\n" + "\n".join([f"- {err}" for err in diag_errs]))
                    else:
                        st.error("❌ No face detected. Please look directly at the camera in good lighting.")
        else:
            if st.session_state[image_key] == "success":
                st.success("✅ Face registered successfully! You can turn off the webcam toggle now.")
            else:
                diag_errs = st.session_state.get(f"{image_key}_diags", [])
                if diag_errs:
                    st.error("❌ Face detection failed details:\n" + "\n".join([f"- {err}" for err in diag_errs]))
                else:
                    st.error("❌ No face detected. Please clear the photo and try again.")


def show_mark_attendance_page(user):
    db.expire_old_sessions()
    st.header("Mark Attendance (Face + PIN)")
    st.write("Select an active session (subject/section) to mark your attendance.")

    student = db.get_student_by_roll(user['id'])

    if not student or student.get('face_encoding') is None:
        st.warning("You must register your face in your profile before marking attendance.")
        return

    sessions = db.get_student_active_sessions(
        student['course'], 
        student['year'], 
        student['division']
    )

    if not sessions:
        st.info("No active sessions available right now.")
        return

    session_options = [
        f"{s['subject']} ({s['course']} {s['year']} {s['division']})"
        for s in sessions
    ]

    selected_idx = st.selectbox(
        "Select Session",
        range(len(session_options)),
        format_func=lambda i: session_options[i]
    )

    selected_session = sessions[selected_idx]

    pin = st.text_input("Enter Session PIN", type="password")

    pin_valid = pin and str(pin).strip() == str(selected_session['session_pin']).strip()

    if pin and not pin_valid:
        st.error("❌ Incorrect PIN")
        return

    if pin_valid:
        already_marked = db.check_attendance_exists(
            selected_session['id'],
            student['id']
        )

        if already_marked:
            st.warning("⚠️ Attendance already marked for this session")
            return
            
        st.divider()
        st.write("#### 📷 Face Check")
        st.info("Look straight into the camera to automatically mark attendance.")
        
        img_file = st.camera_input("Take a photo to mark attendance")
        
        if img_file is not None:
            # Use MD5 hash of actual bytes — unique per photo
            import hashlib
            image_bytes = img_file.getvalue()
            image_key = f"verify_{hashlib.md5(image_bytes).hexdigest()}"
            
            if image_key not in st.session_state:
                with st.spinner("⚙️ Analyzing and verifying face..."):
                    from components import face_engine
                    img = Image.open(img_file)
                    img.load()  # Force PIL decode before thumbnail
                    img.thumbnail((640, 640))
                    
                    encoding = face_engine.extract_face_encoding(img)
                    
                    if encoding is None:
                        st.session_state[image_key] = ("error", "❌ No face detected. Look directly at the camera.")
                        st.error("❌ No face detected. Look directly at the camera.")
                    else:
                        match = face_engine.verify_face(student['face_encoding'], encoding)
                        if not match:
                            st.session_state[image_key] = ("error", "❌ Face does not match registered student.")
                            st.error("❌ Face does not match registered student.")
                        else:
                            success, msg = db.mark_attendance(selected_session['id'], student['id'], student['roll_number'], 'face_verified')
                            if success:
                                st.session_state[image_key] = ("success", "✅ Attendance marked successfully!")
                                st.success("✅ Attendance marked successfully!")
                                st.rerun()
                            else:
                                st.session_state[image_key] = ("warning", msg)
                                st.warning(msg)
            else:
                status, message = st.session_state[image_key]
                if status == "success":
                    st.success(message)
                elif status == "warning":
                    st.warning(message)
                else:
                    st.error(message)


def show_attendance_view(user):
    st.header("View Attendance")
    st.subheader("📊 Attendance Dashboard")

    # get student
    student = db.get_student_by_roll(user['id'])

    if not student:
        st.error("Student not found")
        return

    attendance = db.get_student_attendance_by_roll(student['roll_number'])

    if not attendance:
        st.warning("No attendance records found.")
        return

    df = pd.DataFrame(attendance)

    # rename columns
    df = df.rename(columns={
        "subject": "Subject",
        "course": "Course",
        "mark_time": "DateTime",
        "verification_status": "Status"
    })

    # Separate Date and Time
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["Date"] = df["DateTime"].dt.date
    df["Time"] = df["DateTime"].dt.strftime("%H:%M:%S")

    # Filters
    st.write("#### Filters")
    col1, col2 = st.columns(2)
    subjects = ["All Subjects"] + list(df["Subject"].unique())
    selected_subject = col1.selectbox("Filter by Subject", subjects)
    
    dates = ["All Dates"] + sorted(list(df["Date"].astype(str).unique()), reverse=True)
    selected_date = col2.selectbox("Filter by Date", dates)
    
    # Apply Filters
    filtered_df = df.copy()
    if selected_subject != "All Subjects":
        filtered_df = filtered_df[filtered_df["Subject"] == selected_subject]
        
    if selected_date != "All Dates":
        filtered_df = filtered_df[filtered_df["Date"].astype(str) == selected_date]

    # table
    st.subheader("📋 Attendance Records")
    if filtered_df.empty:
        st.info("No records match your filters.")
        st.dataframe(filtered_df, use_container_width=False)
    else:
        display_df = filtered_df[["Subject", "Course", "Date", "Time", "Status"]]
        st.dataframe(display_df, use_container_width=False, hide_index=True)

    # metrics based on filtered_df
    total = len(filtered_df)
    present = len(filtered_df[filtered_df["Status"] == "face_verified"])
    absent = total - present
    percentage = (present / total) * 100 if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Filtered Classes", total)
    col2.metric("Present", present)
    col3.metric("Absent", absent)
    col4.metric("Attendance %", f"{percentage:.1f}%")

    st.divider()

    # Dynamic Graphs
    if not filtered_df.empty:
        # bar chart
        subject_count = filtered_df.groupby("Subject").size().reset_index(name="Count")
        fig_bar = px.bar(subject_count, x="Subject", y="Count", title="Classes per Subject (Filtered)")
        st.plotly_chart(fig_bar, use_container_width=False)

        # pie chart
        pie_data = pd.DataFrame({
            "Status": ["Present", "Absent"],
            "Count": [present, absent]
        })
        fig_pie = px.pie(pie_data, names="Status", values="Count", title="Attendance Distribution (Filtered)")
        st.plotly_chart(fig_pie, use_container_width=False)

    # ✅ FIX: define csv BEFORE button
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Attendance (CSV)",
        data=csv,
        file_name="attendance.csv",
        mime="text/csv",
        key="student_attendance_download"
    )
