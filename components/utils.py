import random
import string
import csv
import io
import pandas as pd
from datetime import datetime, timedelta

import pytz
from fpdf import FPDF

COLLEGE_NAME = "Department of Technology, Pune"
IST = pytz.timezone('Asia/Kolkata')

def generate_pin(length=4):
    """Generate random PIN"""
    return ''.join(random.choices(string.digits, k=length))


def get_current_time_ist():
    """Get current time in IST"""
    return datetime.now(IST).replace(tzinfo=None)

def get_time_remaining(session_start, duration_minutes):
    """
    Calculate remaining time in session
    
    Args:
        session_start: datetime object
        duration_minutes: int
    
    Returns:
        dict with seconds_remaining, formatted_time, is_expired
    """
    now = get_current_time_ist()
    session_end = session_start + timedelta(minutes=duration_minutes)
    
    remaining = (session_end - now).total_seconds()
    
    if remaining <= 0:
        return {
            'seconds_remaining': 0,
            'formatted_time': '00:00:00',
            'is_expired': True,
            'minutes_remaining': 0,
            'seconds_part': 0
        }
    
    minutes_remaining = int(remaining // 60)
    seconds_part = int(remaining % 60)
    minutes_part = minutes_remaining % 60
    hours_part = minutes_remaining // 60
    
    formatted = f"{hours_part:02d}:{minutes_part:02d}:{seconds_part:02d}"
    
    return {
        'seconds_remaining': int(remaining),
        'formatted_time': formatted,
        'is_expired': False,
        'minutes_remaining': minutes_remaining,
        'seconds_part': seconds_part
    }

def export_to_csv(data, columns=None):
    """
    Export data to CSV bytes
    
    Args:
        data: list of dicts
        columns: list of column names (optional, uses first dict keys if None)
    
    Returns:
        bytes (CSV content)
    """
    if not data:
        return None
    
    if columns is None and isinstance(data[0], dict):
        columns = list(data[0].keys())
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    
    writer.writeheader()
    for row in data:
        writer.writerow({col: row.get(col, '') for col in columns})
    
    return output.getvalue().encode('utf-8')

def create_attendance_pdf(header_title, data, columns, filename="attendance"):
    from fpdf import FPDF   # ✅ force import again
    pdf = FPDF()
    """
    Create PDF report for attendance
    
    Args:
        header_title: str - Title for the report
        data: list of dicts
        columns: list of column names
        filename: str - Filename without extension
    
    Returns:
        bytes (PDF content)
    """
    if FPDF is None:
        raise RuntimeError("PDF generation is not available. Please install the 'fpdf2' package in your environment: pip install fpdf2")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    # College header
    pdf.cell(0, 10, COLLEGE_NAME, ln=True, align="C")
    pdf.ln(2)
    # Report title
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, header_title, ln=True, align="C")
    pdf.ln(5)
    
    # Generate timestamp
    now_ist = get_current_time_ist()
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Generated on: {now_ist.strftime('%Y-%m-%d %H:%M:%S IST')}", ln=True, align="R")
    pdf.ln(3)
    
    # Table headers
    pdf.set_font("Arial", "B", 10)
    col_width = 190 / len(columns)
    
    for col in columns:
        pdf.cell(col_width, 7, str(col)[:20], border=1, align="C")
    pdf.ln()
    
    # Table data
    pdf.set_font("Arial", "", 9)
    for row in data:
        for col in columns:
            value = str(row.get(col, ''))[:20]
            pdf.cell(col_width, 6, value, border=1, align="L")
        pdf.ln()
    
    # Footer
    pdf.ln(5)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "This is an official document from Department of Technology, Pune", border=0)
    pdf_data = pdf.output(dest='S').encode('latin-1')
    return pdf_data


def format_datetime(dt):

    
    """Format datetime to IST string"""
    if isinstance(dt, str):
        return dt
    if dt is None:
        return "-"
    
    try:
        # Assume dt is naive datetime in IST
        ist_dt = dt if isinstance(dt, datetime) else datetime.fromisoformat(str(dt))
        return ist_dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(dt)

def get_attendance_percentage(attended, total):
    """Calculate attendance percentage"""
    if total == 0:
        return 0
    return round((attended / total) * 100, 2)

def validate_email(email):
    """Simple email validation"""
    return '@' in email and '.' in email.split('@')[1]

def validate_phone(phone):
    """Validate phone number (10 digits)"""
    return len(phone) == 10 and phone.isdigit()

def get_course_year_division_options():
    """Get predefined options for course, year, and division"""
    courses = [
        "BSc Data Science",
        "B.Tech Data Science",
        "M.Tech Data Science",
        "BSc Blockchain",
        "PG Data Science"
    ]
    
    years = ["First", "Second", "Third", "Fourth"]
    divisions = ["A", "B"]
    
    return courses, years, divisions

def create_subject_key(course, year, division, subject):
    """Create a unique key for course/subject combination"""
    return f"{course}_{year}_{division}_{subject}"

def dataframe_to_csv_bytes(df):
    """Convert pandas DataFrame to CSV bytes"""
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_buffer.seek(0)
    return csv_buffer.getvalue()

def dataframe_to_excel_bytes(df):
    """Convert pandas DataFrame to Excel bytes"""
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    return excel_buffer.getvalue()
