import json
import uuid
from starlette.responses import JSONResponse
from backend.auth import get_current_user, hash_password
from backend.database import get_db

def log_admin_action(conn, user_id: str, action: str, target_type: str, target_id: str, details: str = ""):
    conn.execute(
        """
        INSERT INTO audit_logs (log_id, user_id, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (f"LOG-{uuid.uuid4().hex[:8].upper()}", user_id, action, target_type, target_id, details)
    )

async def get_dashboard(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized admin access"}, status_code=403)
        
    with get_db() as conn:
        students_cnt = conn.execute("SELECT COUNT(*) as cnt FROM students").fetchone()["cnt"]
        teachers_cnt = conn.execute("SELECT COUNT(*) as cnt FROM teachers").fetchone()["cnt"]
        classes_cnt = conn.execute("SELECT COUNT(*) as cnt FROM classes").fetchone()["cnt"]
        subjects_cnt = conn.execute("SELECT COUNT(*) as cnt FROM subjects").fetchone()["cnt"]
        topics_cnt = conn.execute("SELECT COUNT(*) as cnt FROM topics").fetchone()["cnt"]
        quizzes_cnt = conn.execute("SELECT COUNT(*) as cnt FROM quizzes").fetchone()["cnt"]
        signals_cnt = conn.execute("SELECT COUNT(*) as cnt FROM learning_signals WHERE status = 'REVIEW'").fetchone()["cnt"]
        interventions_cnt = conn.execute("SELECT COUNT(*) as cnt FROM interventions").fetchone()["cnt"]
        
        recent_logs = conn.execute(
            """
            SELECT log_id, action, target_type, target_id, details, timestamp
            FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT 8
            """
        ).fetchall()
        
        return JSONResponse({
            "stats": {
                "students": students_cnt,
                "teachers": teachers_cnt,
                "classes": classes_cnt,
                "subjects": subjects_cnt,
                "topics": topics_cnt,
                "quizzes": quizzes_cnt,
                "active_support_signals": signals_cnt,
                "total_interventions": interventions_cnt
            },
            "recent_logs": [dict(l) for l in recent_logs]
        })

async def list_students(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    with get_db() as conn:
        students = conn.execute(
            """
            SELECT s.student_id, s.user_id, s.name, s.admission_number, s.section,
                   s.status, s.created_at, u.email, c.class_id, c.class_name
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN classes c ON s.class_id = c.class_id
            ORDER BY s.name ASC
            """
        ).fetchall()
        return JSONResponse({"students": [dict(s) for s in students]})

async def create_student(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "SmartEdu123!")
    class_id = body.get("class_id")
    section = body.get("section", "A")
    admission_number = body.get("admission_number", "").strip()
    
    if not name or not email:
        return JSONResponse({"error": "Name and email are required"}, status_code=400)
        
    if not admission_number:
        admission_number = f"STU-{uuid.uuid4().hex[:6].upper()}"
        
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing:
            return JSONResponse({"error": "A user with this email already exists"}, status_code=400)
            
        user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
        student_id = f"STU-{uuid.uuid4().hex[:8].upper()}"
        pwd_hash, salt = hash_password(password)
        
        conn.execute(
            "INSERT INTO users (id, email, password_hash, salt, role, status) VALUES (?, ?, ?, ?, 'student', 'active')",
            (user_id, email, pwd_hash, salt)
        )
        conn.execute(
            """
            INSERT INTO students (student_id, user_id, name, class_id, section, admission_number, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
            """,
            (student_id, user_id, name, class_id, section, admission_number)
        )
        
        log_admin_action(conn, user["id"], "CREATE_STUDENT", "student", student_id, f"Created student {name} ({email})")
        
    return JSONResponse({
        "message": "Student created successfully",
        "student_id": student_id,
        "user_id": user_id
    })

async def update_student(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    student_id = request.path_params.get("student_id")
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    name = body.get("name", "").strip()
    class_id = body.get("class_id")
    section = body.get("section")
    
    with get_db() as conn:
        stu = conn.execute("SELECT student_id, user_id FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if not stu:
            return JSONResponse({"error": "Student not found"}, status_code=404)
            
        conn.execute(
            "UPDATE students SET name = COALESCE(?, name), class_id = ?, section = ?, updated_at = CURRENT_TIMESTAMP WHERE student_id = ?",
            (name or None, class_id, section, student_id)
        )
        log_admin_action(conn, user["id"], "UPDATE_STUDENT", "student", student_id, f"Updated student {name}")
        
    return JSONResponse({"message": "Student updated successfully"})

async def toggle_student_status(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    student_id = request.path_params.get("student_id")
    with get_db() as conn:
        stu = conn.execute("SELECT student_id, user_id, status FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if not stu:
            return JSONResponse({"error": "Student not found"}, status_code=404)
            
        new_status = 'inactive' if stu["status"] == 'active' else 'active'
        conn.execute("UPDATE students SET status = ? WHERE student_id = ?", (new_status, student_id))
        conn.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, stu["user_id"]))
        
        log_admin_action(conn, user["id"], "TOGGLE_STATUS", "student", student_id, f"Changed status to {new_status}")
        
    return JSONResponse({"message": f"Student status changed to {new_status}", "new_status": new_status})

async def delete_student_permanently(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Only administrators can permanently delete records"}, status_code=403)
        
    student_id = request.path_params.get("student_id")
    
    with get_db() as conn:
        stu = conn.execute("SELECT student_id, user_id, name FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if not stu:
            return JSONResponse({"error": "Student not found"}, status_code=404)
            
        user_id = stu["user_id"]
        name = stu["name"]
        
        # Safe relational deletion: Cascade deletion initiated via foreign key constraints on user_id / student_id
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        log_admin_action(conn, user["id"], "PERMANENT_DELETE", "student", student_id, f"Permanently deleted student {name}")
        
    return JSONResponse({"message": f"Student {name} and associated records permanently deleted"})

async def list_teachers(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    with get_db() as conn:
        teachers = conn.execute(
            """
            SELECT t.teacher_id, t.user_id, t.name, t.department, t.employee_number,
                   t.status, t.created_at, u.email,
                   COUNT(DISTINCT tc.class_id) as assigned_classes_count
            FROM teachers t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN teacher_classes tc ON t.teacher_id = tc.teacher_id
            GROUP BY t.teacher_id, t.user_id, t.name, t.department, t.employee_number, t.status, t.created_at, u.email
            ORDER BY t.name ASC
            """
        ).fetchall()
        return JSONResponse({"teachers": [dict(t) for t in teachers]})

async def create_teacher(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "SmartEdu123!")
    department = body.get("department", "Science")
    employee_number = body.get("employee_number", "").strip()
    
    if not name or not email:
        return JSONResponse({"error": "Name and email are required"}, status_code=400)
        
    if not employee_number:
        employee_number = f"EMP-{uuid.uuid4().hex[:6].upper()}"
        
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing:
            return JSONResponse({"error": "A user with this email already exists"}, status_code=400)
            
        user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
        teacher_id = f"TCH-{uuid.uuid4().hex[:8].upper()}"
        pwd_hash, salt = hash_password(password)
        
        conn.execute(
            "INSERT INTO users (id, email, password_hash, salt, role, status) VALUES (?, ?, ?, ?, 'teacher', 'active')",
            (user_id, email, pwd_hash, salt)
        )
        conn.execute(
            """
            INSERT INTO teachers (teacher_id, user_id, name, department, employee_number, status)
            VALUES (?, ?, ?, ?, ?, 'active')
            """,
            (teacher_id, user_id, name, department, employee_number)
        )
        
        log_admin_action(conn, user["id"], "CREATE_TEACHER", "teacher", teacher_id, f"Created teacher {name} ({email})")
        
    return JSONResponse({
        "message": "Teacher created successfully",
        "teacher_id": teacher_id,
        "user_id": user_id
    })

async def toggle_teacher_status(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = request.path_params.get("teacher_id")
    with get_db() as conn:
        tch = conn.execute("SELECT teacher_id, user_id, status FROM teachers WHERE teacher_id = ?", (teacher_id,)).fetchone()
        if not tch:
            return JSONResponse({"error": "Teacher not found"}, status_code=404)
            
        new_status = 'inactive' if tch["status"] == 'active' else 'active'
        conn.execute("UPDATE teachers SET status = ? WHERE teacher_id = ?", (new_status, teacher_id))
        conn.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, tch["user_id"]))
        
        log_admin_action(conn, user["id"], "TOGGLE_STATUS", "teacher", teacher_id, f"Changed status to {new_status}")
        
    return JSONResponse({"message": f"Teacher status changed to {new_status}", "new_status": new_status})

async def delete_teacher_permanently(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Only administrators can permanently delete records"}, status_code=403)
        
    teacher_id = request.path_params.get("teacher_id")
    with get_db() as conn:
        tch = conn.execute("SELECT teacher_id, user_id, name FROM teachers WHERE teacher_id = ?", (teacher_id,)).fetchone()
        if not tch:
            return JSONResponse({"error": "Teacher not found"}, status_code=404)
            
        user_id = tch["user_id"]
        name = tch["name"]
        
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        log_admin_action(conn, user["id"], "PERMANENT_DELETE", "teacher", teacher_id, f"Permanently deleted teacher {name}")
        
    return JSONResponse({"message": f"Teacher {name} permanently deleted"})

async def assign_teacher_to_class(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    teacher_id = body.get("teacher_id")
    class_id = body.get("class_id")
    subject_id = body.get("subject_id")
    
    if not teacher_id or not class_id or not subject_id:
        return JSONResponse({"error": "Teacher, Class, and Subject are all required"}, status_code=400)
        
    rec_id = f"TC-{uuid.uuid4().hex[:8].upper()}"
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO teacher_classes (id, teacher_id, class_id, subject_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(teacher_id, class_id, subject_id) DO NOTHING
            """,
            (rec_id, teacher_id, class_id, subject_id)
        )
        log_admin_action(conn, user["id"], "ASSIGN_TEACHER", "teacher_classes", rec_id, f"Assigned teacher {teacher_id} to class {class_id} for subject {subject_id}")
        
    return JSONResponse({"message": "Teacher assigned to class and subject successfully"})

async def assign_student_to_class(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    student_id = body.get("student_id")
    class_id = body.get("class_id")
    section = body.get("section", "A")
    
    if not student_id or not class_id:
        return JSONResponse({"error": "Student and Class are required"}, status_code=400)
        
    with get_db() as conn:
        conn.execute("UPDATE students SET class_id = ?, section = ? WHERE student_id = ?", (class_id, section, student_id))
        log_admin_action(conn, user["id"], "ASSIGN_STUDENT", "students", student_id, f"Assigned student {student_id} to class {class_id}")
        
    return JSONResponse({"message": "Student assigned to class successfully"})

async def list_classes(request):
    user = get_current_user(request)
    if not user or user["role"] not in ("admin", "teacher"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    with get_db() as conn:
        classes = conn.execute(
            """
            SELECT c.class_id, c.class_name, c.section, c.academic_year,
                   COUNT(DISTINCT s.student_id) as student_count
            FROM classes c
            LEFT JOIN students s ON c.class_id = s.class_id AND s.status = 'active'
            GROUP BY c.class_id, c.class_name, c.section, c.academic_year
            ORDER BY c.class_name ASC
            """
        ).fetchall()
        return JSONResponse({"classes": [dict(c) for c in classes]})

async def create_class(request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    class_name = body.get("class_name", "").strip()
    section = body.get("section", "A").strip()
    academic_year = body.get("academic_year", "2026-2027").strip()
    
    if not class_name:
        return JSONResponse({"error": "Class name is required"}, status_code=400)
        
    class_id = f"CLS-{uuid.uuid4().hex[:8].upper()}"
    with get_db() as conn:
        conn.execute(
            "INSERT INTO classes (class_id, class_name, section, academic_year) VALUES (?, ?, ?, ?)",
            (class_id, class_name, section, academic_year)
        )
        log_admin_action(conn, user["id"], "CREATE_CLASS", "classes", class_id, f"Created class {class_name}-{section}")
        
    return JSONResponse({"message": "Class created successfully", "class_id": class_id})

async def get_curriculum(request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
    with get_db() as conn:
        subjects = conn.execute("SELECT subject_id, subject_name, description FROM subjects ORDER BY subject_name ASC").fetchall()
        chapters = conn.execute("SELECT chapter_id, subject_id, chapter_name FROM chapters ORDER BY chapter_name ASC").fetchall()
        topics = conn.execute("SELECT topic_id, chapter_id, topic_name FROM topics ORDER BY topic_name ASC").fetchall()
        
        return JSONResponse({
            "subjects": [dict(s) for s in subjects],
            "chapters": [dict(c) for c in chapters],
            "topics": [dict(t) for t in topics]
        })
