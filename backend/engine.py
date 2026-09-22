import json
import uuid
from backend.database import get_db

def calculate_personal_baseline_time(student_id: str, conn) -> float:
    """Calculates student's baseline response time across all answered questions."""
    row = conn.execute(
        """
        SELECT AVG(response_time) as avg_time, COUNT(*) as cnt
        FROM question_attempts
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchone()
    if row and row["cnt"] and row["cnt"] > 0 and row["avg_time"]:
        return max(5.0, round(float(row["avg_time"]), 1))
    return 20.0  # default baseline 20s if insufficient data

def calculate_topic_contrast_baseline(student_id: str, topic_id: str, conn) -> float:
    """Calculates student's baseline response time on other topics to detect anomalies."""
    row = conn.execute(
        """
        SELECT AVG(response_time) as avg_time, COUNT(*) as cnt
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.question_id
        WHERE qa.student_id = ? AND q.topic_id != ?
        """,
        (student_id, topic_id)
    ).fetchone()
    if row and row["cnt"] and row["cnt"] > 0 and row["avg_time"]:
        return max(5.0, round(float(row["avg_time"]), 1))
    return calculate_personal_baseline_time(student_id, conn)

def analyze_student_learning_signals(student_id: str, quiz_id: str = None) -> list[dict]:
    """
    Learning Support Signal Engine
    Analyzes student attempts across topics to detect hidden academic support needs.
    Returns list of generated or updated support signals.
    """
    signals_created_or_updated = []
    
    with get_db() as conn:
        # Get overall quiz score if quiz_id is provided
        overall_quiz_score = None
        if quiz_id:
            attempt_row = conn.execute(
                """
                SELECT score FROM quiz_attempts
                WHERE quiz_id = ? AND student_id = ? AND completed = 1
                ORDER BY end_time DESC LIMIT 1
                """,
                (quiz_id, student_id)
            ).fetchone()
            if attempt_row:
                overall_quiz_score = round(float(attempt_row["score"]), 1)
        
        # Fetch all questions attempted by the student grouped by topic
        query = """
            SELECT 
                q.topic_id,
                t.topic_name,
                c.chapter_id,
                c.chapter_name,
                s.subject_id,
                s.subject_name,
                COUNT(qa.id) as total_attempts,
                SUM(CASE WHEN qa.is_correct = 0 THEN 1 ELSE 0 END) as error_count,
                AVG(qa.response_time) as avg_response_time,
                SUM(CASE WHEN qa.is_correct = 0 AND qa.confidence_level IN ('Confident', 'Very Confident') THEN 1 ELSE 0 END) as overconfidence_mismatches,
                SUM(CASE WHEN qa.is_correct = 1 AND qa.confidence_level = 'Not Sure' THEN 1 ELSE 0 END) as underconfidence_mismatches,
                MAX(qa.attempt_number) as max_attempt_number
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.question_id
            JOIN topics t ON q.topic_id = t.topic_id
            JOIN chapters c ON t.chapter_id = c.chapter_id
            JOIN subjects s ON c.subject_id = s.subject_id
            WHERE qa.student_id = ?
            GROUP BY q.topic_id, t.topic_name, c.chapter_id, c.chapter_name, s.subject_id, s.subject_name
        """
        topic_stats = conn.execute(query, (student_id,)).fetchall()
        
        for row in topic_stats:
            topic_id = row["topic_id"]
            topic_name = row["topic_name"]
            subject_id = row["subject_id"]
            subject_name = row["subject_name"]
            chapter_name = row["chapter_name"]
            
            total_attempts = row["total_attempts"]
            error_count = row["error_count"] or 0
            avg_resp_time = round(float(row["avg_response_time"] or 0.0), 1)
            overconf_mismatch = row["overconfidence_mismatches"] or 0
            underconf_mismatch = row["underconfidence_mismatches"] or 0
            max_attempt = row["max_attempt_number"] or 1
            
            # If no errors on this topic, support score is low
            if error_count == 0 and total_attempts > 0:
                continue
                
            personal_baseline = calculate_topic_contrast_baseline(student_id, topic_id, conn)
            
            # Factor 1: Error Frequency & Rate (0 - 35 points)
            error_rate = error_count / total_attempts if total_attempts > 0 else 0
            error_points = min(35.0, (error_rate * 25.0) + (min(error_count, 5) * 2.0))
            
            # Factor 2: Repeated Attempts on same concept (0 - 20 points)
            attempt_points = min(20.0, max(0, (max_attempt - 1) * 8.0 + (total_attempts // 2) * 3.0))
            
            # Factor 3: Response Time Anomaly vs Baseline (0 - 25 points)
            time_ratio = avg_resp_time / personal_baseline if personal_baseline > 0 else 1.0
            if time_ratio > 1.2:
                time_points = min(25.0, (time_ratio - 1.0) * 16.0)
            else:
                time_points = 0.0
                
            # Factor 4: Confidence Mismatch (0 - 25 points)
            mismatch_points = min(25.0, (overconf_mismatch * 10.0) + (underconf_mismatch * 3.0))
            
            composite_score = round(min(100.0, error_points + attempt_points + time_points + mismatch_points), 1)
            
            # Threshold for generating a possible academic support signal
            if composite_score >= 45.0 or (error_count >= 2 and overconf_mismatch >= 1):
                # Generate explainable evidence points (pedagogical, constructive, no labeling)
                bullets = []
                if overall_quiz_score and overall_quiz_score >= 70:
                    bullets.append(
                        f"Student achieved an acceptable overall score of {overall_quiz_score}%, but performance on '{topic_name}' shows hidden support signals."
                    )
                if error_count > 0:
                    bullets.append(
                        f"{error_count} repeated mistake{'s' if error_count > 1 else ''} recorded on questions relating to '{topic_name}'."
                    )
                if overconf_mismatch > 0:
                    bullets.append(
                        f"{overconf_mismatch} confidence mismatch{'es' if overconf_mismatch > 1 else ''}: Student selected 'Confident' or 'Very Confident' on incorrect answers, indicating a conceptual misconception."
                    )
                if time_ratio >= 1.3:
                    bullets.append(
                        f"Average response time ({avg_resp_time}s) is {round(time_ratio, 1)}x higher than the student's baseline ({personal_baseline}s), suggesting cognitive struggle or hesitation."
                    )
                if max_attempt > 1:
                    bullets.append(
                        f"Multiple attempts ({max_attempt}) recorded on this concept without score stabilization."
                    )
                
                # Fetch recent question attempts for this topic to show question-by-question evidence
                recent_q_attempts = conn.execute(
                    """
                    SELECT q.question_text, qa.selected_option, q.correct_option, qa.is_correct,
                           qa.response_time, qa.confidence_level, qa.attempt_number, qa.created_at
                    FROM question_attempts qa
                    JOIN questions q ON qa.question_id = q.question_id
                    WHERE qa.student_id = ? AND q.topic_id = ?
                    ORDER BY qa.created_at DESC LIMIT 5
                    """,
                    (student_id, topic_id)
                ).fetchall()
                
                evidence_payload = {
                    "support_score": composite_score,
                    "status_label": "Possible Support Signal Detected",
                    "recommendation": "Teacher review recommended for targeted academic support",
                    "subject_name": subject_name,
                    "chapter_name": chapter_name,
                    "topic_name": topic_name,
                    "overall_quiz_score": overall_quiz_score,
                    "factors": {
                        "error_count": error_count,
                        "total_attempts": total_attempts,
                        "max_attempts": max_attempt,
                        "confidence_mismatch_count": overconf_mismatch,
                        "avg_response_time_seconds": avg_resp_time,
                        "personal_baseline_seconds": personal_baseline,
                        "time_ratio": round(time_ratio, 2)
                    },
                    "explanation_bullets": bullets,
                    "recent_attempts": [dict(r) for r in recent_q_attempts]
                }
                
                # Check if signal already exists for this student and topic
                existing = conn.execute(
                    "SELECT signal_id, status FROM learning_signals WHERE student_id = ? AND topic_id = ?",
                    (student_id, topic_id)
                ).fetchone()
                
                if existing:
                    signal_id = existing["signal_id"]
                    # If existing is already resolved or in intervention, keep appropriate status unless new errors
                    new_status = existing["status"]
                    if new_status == 'RESOLVED' and error_count > 0:
                        new_status = 'REVIEW'
                        
                    conn.execute(
                        """
                        UPDATE learning_signals
                        SET subject_id = ?, error_frequency = ?, repeated_attempts = ?,
                            average_response_time = ?, confidence_mismatch = ?,
                            support_score = ?, status = ?, evidence_json = ?, generated_at = CURRENT_TIMESTAMP
                        WHERE signal_id = ?
                        """,
                        (subject_id, error_count, max_attempt, avg_resp_time, overconf_mismatch,
                         composite_score, new_status, json.dumps(evidence_payload), signal_id)
                    )
                else:
                    signal_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"
                    conn.execute(
                        """
                        INSERT INTO learning_signals (
                            signal_id, student_id, subject_id, topic_id, error_frequency,
                            repeated_attempts, average_response_time, confidence_mismatch,
                            support_score, status, evidence_json, generated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'REVIEW', ?, CURRENT_TIMESTAMP)
                        """,
                        (signal_id, student_id, subject_id, topic_id, error_count,
                         max_attempt, avg_resp_time, overconf_mismatch, composite_score, json.dumps(evidence_payload))
                    )
                
                signals_created_or_updated.append({
                    "signal_id": signal_id,
                    "topic_name": topic_name,
                    "support_score": composite_score,
                    "status": "REVIEW"
                })
                
    return signals_created_or_updated
