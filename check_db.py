import sqlite3

conn = sqlite3.connect("data/attendance.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("""
SELECT id, teacher_id, subject, course, year, division,
       status, start_time, duration_minutes
FROM sessions
""")

rows = c.fetchall()

print("\n===== SESSIONS TABLE =====")
for row in rows:
    print(dict(row))

conn.close()
