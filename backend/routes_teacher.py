import json
import uuid
from starlette.responses import JSONResponse
from backend.auth import get_current_user, can_teacher_access_class, can_teacher_access_student
from backend.database import get_db

async def get_dashboard(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized teacher access"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    
    with get_db() as conn:
        # Get count of assigned classes
        classes_cnt = conn.execute(
            "SELECT COUNT(DISTINCT class_id) as cnt FROM teacher_classes WHERE teacher_id = ?",
            (teacher_id,)
        ).fetchone()["cnt"]
        
        # Get count of assigned students across these classes
        students_cnt = conn.execute(
            """
            SELECT COUNT(DISTINCT s.student_id) as cnt
            FROM students s
            JOIN teacher_classes tc ON s.class_id = tc.class_id
            WHERE tc.teacher_id = ? AND s.status = 'active'
            """,
            (teacher_id,)
        ).fetchone()["cnt"]
        
        # Get count of quizzes created by this teacher
        quizzes_cnt = conn.execute(
            "SELECT COUNT(*) as cnt FROM quizzes WHERE teacher_id = ?",
            (teacher_id,)
        ).fetchone()["cnt"]
        
        # Get count of possible support signals for teacher's students
        signals_cnt = conn.execute(
            """
            SELECT COUNT(DISTINCT ls.signal_id) as cnt
            FROM learning_signals ls
            JOIN students s ON ls.student_id = s.student_id
            JOIN teacher_classes tc ON s.class_id = tc.class_id
            WHERE tc.teacher_id = ? AND ls.status IN ('REVIEW', 'ACKNOWLEDGED')
            """,
            (teacher_id,)
        ).fetchone()["cnt"]
        
        # Get active interventions count
        interventions_cnt = conn.execute(
            """
            SELECT COUNT(*) as cnt FROM interventions
            WHERE teacher_id = ? AND status IN ('ASSIGNED', 'IN_PROGRESS')
            """,
            (teacher_id,)
        ).fetchone()["cnt"]
        
        # Recent support signals requiring review
        recent_signals = conn.execute(
            """
            SELECT ls.signal_id, ls.student_id, s.name as student_name,
                   c.class_name, c.section, sub.subject_name, top.topic_name,
                   ls.support_score, ls.status, ls.generated_at
            FROM learning_signals ls
            JOIN students s ON ls.student_id = s.student_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN topics top ON ls.topic_id = top.topic_id
            JOIN chapters ch ON top.chapter_id = ch.chapter_id
            JOIN subjects sub ON ch.subject_id = sub.subject_id
            JOIN teacher_classes tc ON c.class_id = tc.class_id
            WHERE tc.teacher_id = ? AND ls.status IN ('REVIEW', 'ACKNOWLEDGED')
            GROUP BY ls.signal_id
            ORDER BY ls.generated_at DESC
            LIMIT 5
            """,
            (teacher_id,)
        ).fetchall()
        
        return JSONResponse({
            "teacher": user["teacher"],
            "stats": {
                "assigned_students": students_cnt,
                "active_classes": classes_cnt,
                "quizzes_created": quizzes_cnt,
                "support_signals": signals_cnt,
                "active_interventions": interventions_cnt
            },
            "recent_signals": [dict(s) for s in recent_signals]
        })

async def list_assigned_classes(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    with get_db() as conn:
        classes = conn.execute(
            """
            SELECT tc.class_id, c.class_name, c.section, c.academic_year,
                   tc.subject_id, s.subject_name,
                   COUNT(DISTINCT stu.student_id) as student_count
            FROM teacher_classes tc
            JOIN classes c ON tc.class_id = c.class_id
            JOIN subjects s ON tc.subject_id = s.subject_id
            LEFT JOIN students stu ON c.class_id = stu.class_id AND stu.status = 'active'
            WHERE tc.teacher_id = ?
            GROUP BY tc.class_id, c.class_name, c.section, c.academic_year, tc.subject_id, s.subject_name
            """,
            (teacher_id,)
        ).fetchall()
        return JSONResponse({"classes": [dict(c) for c in classes]})

async def list_class_students(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    class_id = request.path_params.get("class_id")
    
    if not can_teacher_access_class(teacher_id, class_id):
        return JSONResponse({"error": "Access forbidden: Class not assigned to this teacher"}, status_code=403)
        
    with get_db() as conn:
        students = conn.execute(
            """
            SELECT s.student_id, s.name, s.admission_number, s.section, s.status,
                   COUNT(DISTINCT ls.signal_id) as active_signals_count,
                   MAX(ls.support_score) as highest_support_score
            FROM students s
            LEFT JOIN learning_signals ls ON s.student_id = ls.student_id AND ls.status IN ('REVIEW', 'ACKNOWLEDGED')
            WHERE s.class_id = ? AND s.status = 'active'
            GROUP BY s.student_id, s.name, s.admission_number, s.section, s.status
            ORDER BY s.name ASC
            """,
            (class_id,)
        ).fetchall()
        return JSONResponse({"students": [dict(s) for s in students]})

async def list_quizzes(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    with get_db() as conn:
        quizzes = conn.execute(
            """
            SELECT q.quiz_id, q.title, q.description, s.subject_name, c.chapter_name,
                   q.difficulty, q.time_limit, q.status, q.created_at,
                   COUNT(DISTINCT ques.question_id) as question_count,
                   COUNT(DISTINCT qa.attempt_id) as total_attempts,
                   AVG(qa.score) as average_student_score
            FROM quizzes q
            JOIN subjects s ON q.subject_id = s.subject_id
            LEFT JOIN chapters c ON q.chapter_id = c.chapter_id
            LEFT JOIN questions ques ON q.quiz_id = ques.quiz_id
            LEFT JOIN quiz_attempts qa ON q.quiz_id = qa.quiz_id AND qa.completed = 1
            WHERE q.teacher_id = ?
            GROUP BY q.quiz_id, q.title, q.description, s.subject_name, c.chapter_name,
                     q.difficulty, q.time_limit, q.status, q.created_at
            ORDER BY q.created_at DESC
            """,
            (teacher_id,)
        ).fetchall()
        return JSONResponse({"quizzes": [dict(q) for q in quizzes]})

async def create_quiz(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    title = body.get("title", "").strip()
    subject_id = body.get("subject_id")
    chapter_id = body.get("chapter_id")
    difficulty = body.get("difficulty", "Medium")
    time_limit = int(body.get("time_limit", 15))
    status = body.get("status", "published")
    description = body.get("description", "")
    questions = body.get("questions", [])
    
    if not title or not subject_id:
        return JSONResponse({"error": "Title and Subject are required"}, status_code=400)
        
    quiz_id = f"QZ-{uuid.uuid4().hex[:8].upper()}"
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO quizzes (
                quiz_id, title, description, subject_id, chapter_id,
                teacher_id, difficulty, time_limit, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (quiz_id, title, description, subject_id, chapter_id,
             teacher_id, difficulty, time_limit, status)
        )
        
        # Insert questions if provided
        for q in questions:
            q_id = f"Q-{uuid.uuid4().hex[:8].upper()}"
            conn.execute(
                """
                INSERT INTO questions (
                    question_id, quiz_id, topic_id, question_text,
                    option_a, option_b, option_c, option_d,
                    correct_option, explanation, difficulty
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (q_id, quiz_id, q.get("topic_id"), q.get("question_text"),
                 q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d"),
                 q.get("correct_option", "A").upper(), q.get("explanation", ""), q.get("difficulty", difficulty))
            )
            
    return JSONResponse({
        "message": "Quiz created successfully",
        "quiz_id": quiz_id,
        "questions_count": len(questions)
    })

async def add_questions_to_quiz(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    quiz_id = request.path_params.get("quiz_id")
    
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    questions = body.get("questions", [])
    if not questions:
        return JSONResponse({"error": "No questions provided"}, status_code=400)
        
    with get_db() as conn:
        quiz = conn.execute("SELECT quiz_id FROM quizzes WHERE quiz_id = ? AND teacher_id = ?", (quiz_id, teacher_id)).fetchone()
        if not quiz:
            return JSONResponse({"error": "Quiz not found or not created by you"}, status_code=404)
            
        for q in questions:
            q_id = f"Q-{uuid.uuid4().hex[:8].upper()}"
            conn.execute(
                """
                INSERT INTO questions (
                    question_id, quiz_id, topic_id, question_text,
                    option_a, option_b, option_c, option_d,
                    correct_option, explanation, difficulty
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (q_id, quiz_id, q.get("topic_id"), q.get("question_text"),
                 q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d"),
                 q.get("correct_option", "A").upper(), q.get("explanation", ""), q.get("difficulty", "Medium"))
            )
            
    return JSONResponse({"message": f"{len(questions)} question(s) added successfully"})

async def delete_quiz(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    quiz_id = request.path_params.get("quiz_id")
    
    with get_db() as conn:
        quiz = conn.execute("SELECT quiz_id FROM quizzes WHERE quiz_id = ? AND teacher_id = ?", (quiz_id, teacher_id)).fetchone()
        if not quiz:
            return JSONResponse({"error": "Quiz not found or you lack permission to delete it"}, status_code=404)
            
        conn.execute("DELETE FROM quizzes WHERE quiz_id = ?", (quiz_id,))
        return JSONResponse({"message": "Quiz deleted successfully"})

async def list_support_signals(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    
    with get_db() as conn:
        signals = conn.execute(
            """
            SELECT ls.signal_id, ls.student_id, s.name as student_name, s.admission_number,
                   c.class_name, c.section, sub.subject_name, top.topic_id, top.topic_name,
                   ls.error_frequency, ls.repeated_attempts, ls.average_response_time,
                   ls.confidence_mismatch, ls.support_score, ls.status, ls.generated_at
            FROM learning_signals ls
            JOIN students s ON ls.student_id = s.student_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN topics top ON ls.topic_id = top.topic_id
            JOIN chapters ch ON top.chapter_id = ch.chapter_id
            JOIN subjects sub ON ch.subject_id = sub.subject_id
            JOIN teacher_classes tc ON c.class_id = tc.class_id
            WHERE tc.teacher_id = ?
            GROUP BY ls.signal_id
            ORDER BY ls.support_score DESC, ls.generated_at DESC
            """,
            (teacher_id,)
        ).fetchall()
        return JSONResponse({"signals": [dict(s) for s in signals]})

async def get_signal_evidence(request):
    """
    Detailed Evidence Screen: Shows transparent pedagogical evidence behind the signal.
    """
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    signal_id = request.path_params.get("signal_id")
    
    with get_db() as conn:
        signal = conn.execute(
            """
            SELECT ls.signal_id, ls.student_id, s.name as student_name, s.admission_number,
                   c.class_name, c.section, sub.subject_name, top.topic_id, top.topic_name,
                   ch.chapter_name, ls.error_frequency, ls.repeated_attempts,
                   ls.average_response_time, ls.confidence_mismatch, ls.support_score,
                   ls.status, ls.evidence_json, ls.generated_at
            FROM learning_signals ls
            JOIN students s ON ls.student_id = s.student_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN topics top ON ls.topic_id = top.topic_id
            JOIN chapters ch ON top.chapter_id = ch.chapter_id
            JOIN subjects sub ON ch.subject_id = sub.subject_id
            JOIN teacher_classes tc ON c.class_id = tc.class_id
            WHERE ls.signal_id = ? AND tc.teacher_id = ?
            GROUP BY ls.signal_id
            """,
            (signal_id, teacher_id)
        ).fetchone()
        
        if not signal:
            return JSONResponse({"error": "Signal not found or unauthorized"}, status_code=404)
            
        evidence_data = {}
        if signal["evidence_json"]:
            try:
                evidence_data = json.loads(signal["evidence_json"])
            except Exception:
                evidence_data = {}
                
        # Fetch question attempts history for this student & topic
        attempts = conn.execute(
            """
            SELECT q.question_text, qa.selected_option, q.correct_option,
                   qa.is_correct, qa.response_time, qa.confidence_level,
                   qa.attempt_number, qa.created_at
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.question_id
            WHERE qa.student_id = ? AND q.topic_id = ?
            ORDER BY qa.created_at DESC
            LIMIT 10
            """,
            (signal["student_id"], signal["topic_id"])
        ).fetchall()
        
        # Check if intervention is already active for this student and topic
        intervention = conn.execute(
            """
            SELECT intervention_id, intervention_type, teacher_note, assigned_at, status
            FROM interventions
            WHERE student_id = ? AND topic_id = ?
            ORDER BY assigned_at DESC LIMIT 1
            """,
            (signal["student_id"], signal["topic_id"])
        ).fetchone()
        
        res = dict(signal)
        res["parsed_evidence"] = evidence_data
        res["recent_attempts"] = [dict(a) for a in attempts]
        res["active_intervention"] = dict(intervention) if intervention else None
        
        return JSONResponse({"evidence": res})

async def create_intervention(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    student_id = body.get("student_id")
    topic_id = body.get("topic_id")
    intervention_type = body.get("intervention_type", "3-question concept check")
    teacher_note = body.get("teacher_note", "").strip()
    
    if not student_id or not topic_id:
        return JSONResponse({"error": "Student and Topic are required"}, status_code=400)
        
    if not can_teacher_access_student(teacher_id, student_id):
        return JSONResponse({"error": "Unauthorized student access"}, status_code=403)
        
    intervention_id = f"INT-{uuid.uuid4().hex[:8].upper()}"
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO interventions (
                intervention_id, student_id, teacher_id, topic_id,
                intervention_type, teacher_note, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'ASSIGNED')
            """,
            (intervention_id, student_id, teacher_id, topic_id, intervention_type, teacher_note)
        )
        
        # Update signal status to INTERVENING
        conn.execute(
            "UPDATE learning_signals SET status = 'INTERVENING' WHERE student_id = ? AND topic_id = ?",
            (student_id, topic_id)
        )
        
    return JSONResponse({
        "message": "Intervention created and assigned to student",
        "intervention_id": intervention_id
    })

async def list_interventions(request):
    user = get_current_user(request)
    if not user or user["role"] != "teacher":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    teacher_id = user["teacher"]["teacher_id"]
    with get_db() as conn:
        interventions = conn.execute(
            """
            SELECT i.intervention_id, i.student_id, s.name as student_name,
                   c.class_name, c.section, sub.subject_name, top.topic_name,
                   i.intervention_type, i.teacher_note, i.assigned_at, i.completed_at, i.status,
                   fur.before_score, fur.after_score, fur.improvement, fur.result_status
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN topics top ON i.topic_id = top.topic_id
            JOIN chapters ch ON top.chapter_id = ch.chapter_id
            JOIN subjects sub ON ch.subject_id = sub.subject_id
            LEFT JOIN follow_up_results fur ON i.intervention_id = fur.intervention_id
            WHERE i.teacher_id = ?
            ORDER BY i.assigned_at DESC
            """,
            (teacher_id,)
        ).fetchall()
        return JSONResponse({"interventions": [dict(i) for i in interventions]})
