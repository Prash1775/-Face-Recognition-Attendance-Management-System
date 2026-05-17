-- 1. Create Students Table
CREATE TABLE IF NOT EXISTS students (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    roll_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    course TEXT NOT NULL,
    year TEXT NOT NULL,
    division TEXT NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    face_encoding JSONB, -- Storing as JSON array of floats
    registration_date TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Create Teachers Table
CREATE TABLE IF NOT EXISTS teachers (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    teacher_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    registration_date TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Create Teacher Assignments Table
CREATE TABLE IF NOT EXISTS teacher_assignments (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    teacher_id BIGINT REFERENCES teachers(id) ON DELETE CASCADE,
    course TEXT NOT NULL,
    year TEXT NOT NULL,
    division TEXT NOT NULL,
    subject TEXT NOT NULL,
    UNIQUE(teacher_id, course, year, division, subject)
);

-- 4. Create Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    teacher_id BIGINT REFERENCES teachers(id) ON DELETE CASCADE,
    course TEXT NOT NULL,
    year TEXT NOT NULL,
    division TEXT NOT NULL,
    subject TEXT NOT NULL,
    session_pin TEXT NOT NULL,
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER NOT NULL,
    status TEXT DEFAULT 'active'
);

-- 5. Create Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id BIGINT REFERENCES sessions(id) ON DELETE CASCADE,
    student_id BIGINT REFERENCES students(id) ON DELETE CASCADE,
    roll_number TEXT NOT NULL,
    mark_time TIMESTAMPTZ DEFAULT NOW(),
    verification_status TEXT DEFAULT 'face_verified',
    UNIQUE(session_id, student_id)
);

-- Enable RLS (Row Level Security) - Optional but recommended
-- For simplicity in a student project, you can keep it open or add simple policies.
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;

-- Allow all access for now (Development mode)
CREATE POLICY "Public Read/Write" ON students FOR ALL USING (true);
CREATE POLICY "Public Read/Write" ON teachers FOR ALL USING (true);
CREATE POLICY "Public Read/Write" ON teacher_assignments FOR ALL USING (true);
CREATE POLICY "Public Read/Write" ON sessions FOR ALL USING (true);
CREATE POLICY "Public Read/Write" ON attendance FOR ALL USING (true);
