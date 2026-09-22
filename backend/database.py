import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartedu.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS classes (
    class_id TEXT PRIMARY KEY,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL,
    academic_year TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id TEXT PRIMARY KEY,
    subject_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS chapters (
    chapter_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    chapter_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    topic_id TEXT PRIMARY KEY,
    chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    topic_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    department TEXT,
    employee_number TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    class_id TEXT REFERENCES classes(class_id) ON DELETE SET NULL,
    section TEXT,
    admission_number TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teacher_classes (
    id TEXT PRIMARY KEY,
    teacher_id TEXT NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    class_id TEXT NOT NULL REFERENCES classes(class_id) ON DELETE CASCADE,
    subject_id TEXT NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE(teacher_id, class_id, subject_id)
);

CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    subject_id TEXT NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    chapter_id TEXT REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    teacher_id TEXT NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    difficulty TEXT DEFAULT 'Medium',
    time_limit INTEGER DEFAULT 15,
    status TEXT NOT NULL DEFAULT 'published' CHECK(status IN ('draft', 'published')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    topic_id TEXT REFERENCES topics(topic_id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    difficulty TEXT DEFAULT 'Medium'
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    attempt_id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    score REAL DEFAULT 0.0,
    completed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS question_attempts (
    id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL REFERENCES quiz_attempts(attempt_id) ON DELETE CASCADE,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    question_id TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    selected_option TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    response_time REAL NOT NULL,
    confidence_level TEXT NOT NULL CHECK(confidence_level IN ('Not Sure', 'Somewhat Sure', 'Confident', 'Very Confident')),
    attempt_number INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_signals (
    signal_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id TEXT REFERENCES subjects(subject_id) ON DELETE SET NULL,
    topic_id TEXT NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    error_frequency INTEGER DEFAULT 0,
    repeated_attempts INTEGER DEFAULT 0,
    average_response_time REAL DEFAULT 0.0,
    confidence_mismatch INTEGER DEFAULT 0,
    support_score REAL DEFAULT 0.0,
    status TEXT DEFAULT 'REVIEW' CHECK(status IN ('REVIEW', 'ACKNOWLEDGED', 'INTERVENING', 'RESOLVED')),
    evidence_json TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interventions (
    intervention_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    teacher_id TEXT NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    topic_id TEXT NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    intervention_type TEXT NOT NULL,
    teacher_note TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'ASSIGNED' CHECK(status IN ('ASSIGNED', 'IN_PROGRESS', 'COMPLETED'))
);

CREATE TABLE IF NOT EXISTS follow_up_results (
    result_id TEXT PRIMARY KEY,
    intervention_id TEXT UNIQUE NOT NULL REFERENCES interventions(intervention_id) ON DELETE CASCADE,
    before_score REAL NOT NULL,
    after_score REAL NOT NULL,
    improvement REAL NOT NULL,
    result_status TEXT NOT NULL CHECK(result_status IN ('Improved', 'Partially Improved', 'Further Review Recommended')),
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_students_user ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_teachers_user ON teachers(user_id);
CREATE INDEX IF NOT EXISTS idx_teacher_classes ON teacher_classes(teacher_id, class_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_teacher ON quizzes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_q_attempts_student ON question_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_q_attempts_question ON question_attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_signals_student ON learning_signals(student_id);
CREATE INDEX IF NOT EXISTS idx_interventions_student ON interventions(student_id);
"""

@contextmanager
def get_db(db_path=None):
    target = db_path or DB_PATH
    conn = sqlite3.connect(target, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path=None):
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
