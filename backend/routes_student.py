import json
import uuid
from starlette.responses import JSONResponse
from backend.auth import get_current_user
from backend.database import get_db
from backend.engine import analyze_student_learning_signals

async def get_dashboard(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized student access"}, status_code=403)
        
    student = user.get("student")
    if not student:
        return JSONResponse({"error": "Student profile not found"}, status_code=404)
        
    student_id = student["student_id"]
    class_id = student.get("class_id")
    
    with get_db() as conn:
        # Fetch student's class name
        class_info = None
        if class_id:
            c = conn.execute("SELECT class_name, section, academic_year FROM classes WHERE class_id = ?", (class_id,)).fetchone()
            if c:
                class_info = dict(c)
                
        # Fetch assigned published quizzes
        quizzes = conn.execute(
            """
            SELECT q.quiz_id, q.title, q.description, s.subject_name, q.difficulty, q.time_limit,
                   COUNT(ques.question_id) as question_count,
                   MAX(qa.score) as best_score,
                   COUNT(qa.attempt_id) as attempts_count
            FROM quizzes q
            JOIN subjects s ON q.subject_id = s.subject_id
            LEFT JOIN questions ques ON q.quiz_id = ques.quiz_id
            LEFT JOIN quiz_attempts qa ON q.quiz_id = qa.quiz_id AND qa.student_id = ? AND qa.completed = 1
            WHERE q.status = 'published'
            GROUP BY q.quiz_id, q.title, q.description, s.subject_name, q.difficulty, q.time_limit
            ORDER BY q.created_at DESC
            LIMIT 10
            """,
            (student_id,)
        ).fetchall()
        
        # Fetch active assigned interventions
        interventions = conn.execute(
            """
            SELECT i.intervention_id, i.topic_id, t.topic_name, s.subject_name,
                   i.intervention_type, i.teacher_note, i.assigned_at, i.status,
                   tch.name as teacher_name
            FROM interventions i
            JOIN topics t ON i.topic_id = t.topic_id
            JOIN chapters c ON t.chapter_id = c.chapter_id
            JOIN subjects s ON c.subject_id = s.subject_id
            JOIN teachers tch ON i.teacher_id = tch.teacher_id
            WHERE i.student_id = ? AND i.status IN ('ASSIGNED', 'IN_PROGRESS')
            ORDER BY i.assigned_at DESC
            """,
            (student_id,)
        ).fetchall()
        
        # Overall student stats
        stats_row = conn.execute(
            """
            SELECT 
                COUNT(DISTINCT qa.attempt_id) as total_quizzes_completed,
                AVG(qa.score) as average_score,
                COUNT(qatt.id) as total_questions_answered,
                SUM(CASE WHEN qatt.is_correct = 1 THEN 1 ELSE 0 END) as total_correct
            FROM quiz_attempts qa
            LEFT JOIN question_attempts qatt ON qa.attempt_id = qatt.attempt_id
            WHERE qa.student_id = ? AND qa.completed = 1
            """,
            (student_id,)
        ).fetchone()
        
        stats = {
            "total_quizzes": stats_row["total_quizzes_completed"] or 0,
            "average_score": round(float(stats_row["average_score"] or 0.0), 1),
            "questions_answered": stats_row["total_questions_answered"] or 0,
            "accuracy_percent": round(
                (stats_row["total_correct"] / stats_row["total_questions_answered"] * 100.0) 
                if stats_row["total_questions_answered"] else 0.0, 1
            )
        }
        
        # Recent completed quiz attempts
        recent_attempts = conn.execute(
            """
            SELECT qa.attempt_id, q.title, s.subject_name, qa.score, qa.end_time
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.quiz_id
            JOIN subjects s ON q.subject_id = s.subject_id
            WHERE qa.student_id = ? AND qa.completed = 1
            ORDER BY qa.end_time DESC LIMIT 5
            """,
            (student_id,)
        ).fetchall()
        
        return JSONResponse({
            "student": student,
            "class_info": class_info,
            "stats": stats,
            "quizzes": [dict(q) for q in quizzes],
            "active_interventions": [dict(i) for i in interventions],
            "recent_attempts": [dict(a) for a in recent_attempts]
        })

async def list_quizzes(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    student_id = user["student"]["student_id"]
    with get_db() as conn:
        quizzes = conn.execute(
            """
            SELECT q.quiz_id, q.title, q.description, s.subject_name, c.chapter_name,
                   q.difficulty, q.time_limit,
                   COUNT(ques.question_id) as question_count,
                   MAX(qa.score) as best_score,
                   COUNT(qa.attempt_id) as attempts_count
            FROM quizzes q
            JOIN subjects s ON q.subject_id = s.subject_id
            LEFT JOIN chapters c ON q.chapter_id = c.chapter_id
            LEFT JOIN questions ques ON q.quiz_id = ques.quiz_id
            LEFT JOIN quiz_attempts qa ON q.quiz_id = qa.quiz_id AND qa.student_id = ? AND qa.completed = 1
            WHERE q.status = 'published'
            GROUP BY q.quiz_id, q.title, q.description, s.subject_name, c.chapter_name, q.difficulty, q.time_limit
            ORDER BY q.created_at DESC
            """,
            (student_id,)
        ).fetchall()
        return JSONResponse({"quizzes": [dict(q) for q in quizzes]})

async def get_quiz_details(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    quiz_id = request.path_params.get("quiz_id")
    with get_db() as conn:
        quiz = conn.execute(
            """
            SELECT q.quiz_id, q.title, q.description, s.subject_name, c.chapter_name,
                   q.difficulty, q.time_limit, tch.name as teacher_name
            FROM quizzes q
            JOIN subjects s ON q.subject_id = s.subject_id
            LEFT JOIN chapters c ON q.chapter_id = c.chapter_id
            JOIN teachers tch ON q.teacher_id = tch.teacher_id
            WHERE q.quiz_id = ? AND q.status = 'published'
            """,
            (quiz_id,)
        ).fetchone()
        
        if not quiz:
            return JSONResponse({"error": "Quiz not found or not published"}, status_code=404)
            
        # Security: Do NOT reveal correct_option or explanation to student during quiz!
        questions = conn.execute(
            """
            SELECT question_id, question_text, option_a, option_b, option_c, option_d, difficulty, topic_id
            FROM questions
            WHERE quiz_id = ?
            ORDER BY rowid ASC
            """,
            (quiz_id,)
        ).fetchall()
        
        return JSONResponse({
            "quiz": dict(quiz),
            "questions": [dict(q) for q in questions]
        })

async def start_quiz(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    quiz_id = request.path_params.get("quiz_id")
    student_id = user["student"]["student_id"]
    
    with get_db() as conn:
        quiz = conn.execute("SELECT quiz_id FROM quizzes WHERE quiz_id = ? AND status = 'published'", (quiz_id,)).fetchone()
        if not quiz:
            return JSONResponse({"error": "Quiz not available"}, status_code=404)
            
        attempt_id = f"ATT-{uuid.uuid4().hex[:8].upper()}"
        conn.execute(
            "INSERT INTO quiz_attempts (attempt_id, quiz_id, student_id, start_time, completed) VALUES (?, ?, ?, CURRENT_TIMESTAMP, 0)",
            (attempt_id, quiz_id, student_id)
        )
        return JSONResponse({
            "attempt_id": attempt_id,
            "message": "Quiz attempt started"
        })

async def answer_question(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    student_id = user["student"]["student_id"]
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    attempt_id = body.get("attempt_id")
    question_id = body.get("question_id")
    selected_option = body.get("selected_option", "").strip().upper()
    response_time = float(body.get("response_time", 15.0))
    confidence_level = body.get("confidence_level", "").strip()
    
    valid_confidences = ['Not Sure', 'Somewhat Sure', 'Confident', 'Very Confident']
    if confidence_level not in valid_confidences:
        return JSONResponse({"error": f"Invalid confidence level. Must be one of: {valid_confidences}"}, status_code=400)
        
    if selected_option not in ['A', 'B', 'C', 'D']:
        return JSONResponse({"error": "Option must be A, B, C, or D"}, status_code=400)
        
    with get_db() as conn:
        # Check active attempt belongs to student
        attempt = conn.execute(
            "SELECT attempt_id, quiz_id, completed FROM quiz_attempts WHERE attempt_id = ? AND student_id = ?",
            (attempt_id, student_id)
        ).fetchone()
        if not attempt:
            return JSONResponse({"error": "Quiz attempt not found"}, status_code=404)
        if attempt["completed"]:
            return JSONResponse({"error": "Quiz attempt is already completed"}, status_code=400)
            
        # Check question and correct option
        q = conn.execute("SELECT correct_option, explanation, topic_id FROM questions WHERE question_id = ?", (question_id,)).fetchone()
        if not q:
            return JSONResponse({"error": "Question not found"}, status_code=404)
            
        is_correct = 1 if selected_option == q["correct_option"] else 0
        
        # Calculate attempt number for this question by student
        prev_attempts = conn.execute(
            "SELECT COUNT(*) as cnt FROM question_attempts WHERE student_id = ? AND question_id = ?",
            (student_id, question_id)
        ).fetchone()["cnt"]
        attempt_number = prev_attempts + 1
        
        attempt_log_id = f"QA-{uuid.uuid4().hex[:8].upper()}"
        conn.execute(
            """
            INSERT INTO question_attempts (
                id, attempt_id, student_id, question_id, selected_option,
                is_correct, response_time, confidence_level, attempt_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (attempt_log_id, attempt_id, student_id, question_id, selected_option,
             is_correct, response_time, confidence_level, attempt_number)
        )
        
        return JSONResponse({
            "is_correct": bool(is_correct),
            "correct_option": q["correct_option"],
            "explanation": q["explanation"],
            "attempt_number": attempt_number
        })

async def finish_quiz(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    student_id = user["student"]["student_id"]
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    attempt_id = body.get("attempt_id")
    
    with get_db() as conn:
        attempt = conn.execute(
            "SELECT attempt_id, quiz_id, completed FROM quiz_attempts WHERE attempt_id = ? AND student_id = ?",
            (attempt_id, student_id)
        ).fetchone()
        if not attempt:
            return JSONResponse({"error": "Attempt not found"}, status_code=404)
            
        quiz_id = attempt["quiz_id"]
        
        # Total questions in this quiz
        total_questions = conn.execute(
            "SELECT COUNT(*) as cnt FROM questions WHERE quiz_id = ?", (quiz_id,)
        ).fetchone()["cnt"]
        
        # Questions answered correctly in this attempt
        correct_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM question_attempts WHERE attempt_id = ? AND is_correct = 1",
            (attempt_id,)
        ).fetchone()["cnt"]
        
        score = round((correct_count / total_questions * 100.0) if total_questions > 0 else 0.0, 1)
        
        conn.execute(
            "UPDATE quiz_attempts SET score = ?, completed = 1, end_time = CURRENT_TIMESTAMP WHERE attempt_id = ?",
            (score, attempt_id)
        )
        
    # Analyze student learning signals via the engine!
    generated_signals = analyze_student_learning_signals(student_id, quiz_id)
    
    return JSONResponse({
        "message": "Quiz completed successfully",
        "score": score,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "signals_generated_count": len(generated_signals)
    })

async def list_interventions(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    student_id = user["student"]["student_id"]
    with get_db() as conn:
        interventions = conn.execute(
            """
            SELECT i.intervention_id, i.topic_id, t.topic_name, s.subject_name, c.chapter_name,
                   i.intervention_type, i.teacher_note, i.assigned_at, i.completed_at, i.status,
                   tch.name as teacher_name,
                   fur.before_score, fur.after_score, fur.improvement, fur.result_status
            FROM interventions i
            JOIN topics t ON i.topic_id = t.topic_id
            JOIN chapters c ON t.chapter_id = c.chapter_id
            JOIN subjects s ON c.subject_id = s.subject_id
            JOIN teachers tch ON i.teacher_id = tch.teacher_id
            LEFT JOIN follow_up_results fur ON i.intervention_id = fur.intervention_id
            WHERE i.student_id = ?
            ORDER BY i.assigned_at DESC
            """,
            (student_id,)
        ).fetchall()
        return JSONResponse({"interventions": [dict(i) for i in interventions]})

async def get_intervention_assessment(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    intervention_id = request.path_params.get("intervention_id")
    student_id = user["student"]["student_id"]
    
    with get_db() as conn:
        intervention = conn.execute(
            """
            SELECT i.intervention_id, i.topic_id, t.topic_name, s.subject_name,
                   i.intervention_type, i.teacher_note, i.status
            FROM interventions i
            JOIN topics t ON i.topic_id = t.topic_id
            JOIN chapters c ON t.chapter_id = c.chapter_id
            JOIN subjects s ON c.subject_id = s.subject_id
            WHERE i.intervention_id = ? AND i.student_id = ?
            """,
            (intervention_id, student_id)
        ).fetchone()
        
        if not intervention:
            return JSONResponse({"error": "Intervention not found"}, status_code=404)
            
        topic_id = intervention["topic_id"]
        
        # Fetch up to 3 targeted questions on this topic for the follow-up concept check
        questions = conn.execute(
            """
            SELECT question_id, question_text, option_a, option_b, option_c, option_d, difficulty
            FROM questions
            WHERE topic_id = ?
            ORDER BY question_id ASC
            LIMIT 3
            """,
            (topic_id,)
        ).fetchall()
        
        # If fewer than 3, grab any questions from same topic or chapter
        if len(questions) < 3:
            questions = conn.execute(
                """
                SELECT question_id, question_text, option_a, option_b, option_c, option_d, difficulty
                FROM questions
                ORDER BY RANDOM()
                LIMIT 3
                """
            ).fetchall()
            
        return JSONResponse({
            "intervention": dict(intervention),
            "questions": [dict(q) for q in questions]
        })

async def submit_intervention_assessment(request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
    intervention_id = request.path_params.get("intervention_id")
    student_id = user["student"]["student_id"]
    
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    answers = body.get("answers", []) # list of {question_id, selected_option}
    if not answers:
        return JSONResponse({"error": "No answers submitted"}, status_code=400)
        
    with get_db() as conn:
        intervention = conn.execute(
            "SELECT intervention_id, topic_id, teacher_id, status FROM interventions WHERE intervention_id = ? AND student_id = ?",
            (intervention_id, student_id)
        ).fetchone()
        if not intervention:
            return JSONResponse({"error": "Intervention not found"}, status_code=404)
            
        topic_id = intervention["topic_id"]
        
        # Calculate before_score on this topic from previous attempts
        prev_attempts = conn.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN qa.is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.question_id
            WHERE qa.student_id = ? AND q.topic_id = ?
            """,
            (student_id, topic_id)
        ).fetchone()
        
        if prev_attempts and prev_attempts["total"] and prev_attempts["total"] > 0:
            before_score = round(float(prev_attempts["correct"] / prev_attempts["total"] * 100.0), 1)
        else:
            before_score = 40.0  # default baseline before score if not previously measured
            
        correct_count = 0
        for ans in answers:
            q_id = ans.get("question_id")
            opt = ans.get("selected_option", "").upper()
            q = conn.execute("SELECT correct_option FROM questions WHERE question_id = ?", (q_id,)).fetchone()
            if q and opt == q["correct_option"]:
                correct_count += 1
                
        after_score = round((correct_count / len(answers) * 100.0), 1)
        improvement = round(after_score - before_score, 1)
        
        if improvement >= 20.0:
            result_status = "Improved"
        elif improvement >= 5.0:
            result_status = "Partially Improved"
        else:
            result_status = "Further Review Recommended"
            
        result_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
        
        # Record follow-up result
        conn.execute(
            """
            INSERT INTO follow_up_results (
                result_id, intervention_id, before_score, after_score, improvement, result_status
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(intervention_id) DO UPDATE SET
                before_score = excluded.before_score,
                after_score = excluded.after_score,
                improvement = excluded.improvement,
                result_status = excluded.result_status,
                completed_at = CURRENT_TIMESTAMP
            """,
            (result_id, intervention_id, before_score, after_score, improvement, result_status)
        )
        
        # Update intervention status to COMPLETED
        conn.execute(
            "UPDATE interventions SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP WHERE intervention_id = ?",
            (intervention_id,)
        )
        
        # If improved, update associated learning signal to RESOLVED
        if result_status == "Improved":
            conn.execute(
                "UPDATE learning_signals SET status = 'RESOLVED' WHERE student_id = ? AND topic_id = ?",
                (student_id, topic_id)
            )
            
        return JSONResponse({
            "message": "Follow-up assessment completed",
            "before_score": before_score,
            "after_score": after_score,
            "improvement": improvement,
            "result_status": result_status
        })
