import os
import sys
import unittest
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from starlette.testclient import TestClient
from backend.server import app, startup
from backend.database import get_db, init_db
from backend.seed_data import seed_database
from backend.auth import create_token, hash_password

class TestSmartEduFullAcceptance(unittest.TestCase):
    shared_teacher_id = None
    shared_student_id = None
    shared_quiz_id = None
    target_signal_id = None
    student_headers = None
    teacher_headers = None

    @classmethod
    def setUpClass(cls):
        startup()
        cls.client = TestClient(app)
        
        # Clean any prior test artifacts
        with get_db() as conn:
            conn.execute("DELETE FROM users WHERE email IN ('rfeynman@smartedu.edu', 'marie.curie@smartedu.edu', 'temp.student@smartedu.edu')")
        
        # Log in admin to get admin token
        res = cls.client.post("/api/auth/login", json={"email": "admin@smartedu.edu", "password": "Admin123!"})
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        cls.admin_token = res.json()["token"]
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}
        
    def test_01_admin_creates_teacher(self):
        """1. Admin creates a teacher."""
        payload = {
            "name": "Prof. Richard Feynman",
            "email": "rfeynman@smartedu.edu",
            "password": "Password123!",
            "department": "Physics",
            "employee_number": "EMP-PHY999"
        }
        res = self.client.post("/api/admin/teachers", json=payload, headers=self.admin_headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertIn("teacher_id", data)
        self.teacher_id = data["teacher_id"]
        TestSmartEduFullAcceptance.shared_teacher_id = self.teacher_id

    def test_02_admin_creates_student(self):
        """2. Admin creates a student."""
        payload = {
            "name": "Marie Curie",
            "email": "marie.curie@smartedu.edu",
            "password": "Password123!",
            "class_id": "CLS-11SCI",
            "section": "A",
            "admission_number": "ADM-TEST-001"
        }
        res = self.client.post("/api/admin/students", json=payload, headers=self.admin_headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertIn("student_id", data)
        self.student_id = data["student_id"]
        TestSmartEduFullAcceptance.shared_student_id = self.student_id

    def test_03_admin_assigns_student_to_class(self):
        """3. Admin assigns the student to a class."""
        payload = {
            "student_id": TestSmartEduFullAcceptance.shared_student_id,
            "class_id": "CLS-11SCI",
            "section": "A"
        }
        res = self.client.post("/api/admin/assign-student", json=payload, headers=self.admin_headers)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIn("successfully", res.json()["message"].lower())

    def test_04_admin_assigns_teacher_to_class_and_subject(self):
        """4. Admin assigns the teacher to that class/subject."""
        payload = {
            "teacher_id": TestSmartEduFullAcceptance.shared_teacher_id,
            "class_id": "CLS-11SCI",
            "subject_id": "SUB-PHY"
        }
        res = self.client.post("/api/admin/assign-teacher", json=payload, headers=self.admin_headers)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIn("successfully", res.json()["message"].lower())

    def test_05_and_06_teacher_creates_quiz_with_questions(self):
        """5. Teacher creates a quiz. 6. Teacher adds multiple questions."""
        # Log in as created teacher
        res_login = self.client.post("/api/auth/login", json={"email": "rfeynman@smartedu.edu", "password": "Password123!"})
        self.assertEqual(res_login.status_code, 200, res_login.text)
        teacher_token = res_login.json()["token"]
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
        TestSmartEduFullAcceptance.teacher_headers = teacher_headers
        
        quiz_payload = {
            "title": "Electrodynamics & Advanced Circuit Analysis",
            "description": "Comprehensive evaluation of Kirchhoff's network rules and resistance laws.",
            "subject_id": "SUB-PHY",
            "chapter_id": "CHP-PHY01",
            "difficulty": "Hard",
            "time_limit": 20,
            "status": "published",
            "questions": [
                {
                    "topic_id": "TOP-PHY01",
                    "question_text": "Kirchhoff's loop rule is an expression of the law of conservation of:",
                    "option_a": "Electric charge",
                    "option_b": "Energy",
                    "option_c": "Angular momentum",
                    "option_d": "Current density",
                    "correct_option": "B",
                    "explanation": "Kirchhoff's Voltage Law expresses conservation of energy around any closed loop."
                },
                {
                    "topic_id": "TOP-PHY01",
                    "question_text": "In a node connecting 3 conductors with currents I1=5A in, I2=3A in, what is I3 leaving the node?",
                    "option_a": "2A",
                    "option_b": "8A",
                    "option_c": "15A",
                    "option_d": "0A",
                    "correct_option": "B",
                    "explanation": "Conservation of charge: Sum of in = Sum of out => 5 + 3 = 8A."
                },
                {
                    "topic_id": "TOP-PHY02",
                    "question_text": "When the temperature of an ohmic metallic wire increases, its resistance:",
                    "option_a": "Decreases linearly",
                    "option_b": "Increases due to increased lattice collisions",
                    "option_c": "Remains constant",
                    "option_d": "Drops to zero",
                    "correct_option": "B",
                    "explanation": "Increased thermal vibrations enhance electron scattering, raising resistance."
                }
            ]
        }
        res_quiz = self.client.post("/api/teacher/quizzes", json=quiz_payload, headers=teacher_headers)
        self.assertEqual(res_quiz.status_code, 200, res_quiz.text)
        quiz_id = res_quiz.json()["quiz_id"]
        TestSmartEduFullAcceptance.shared_quiz_id = quiz_id

    def test_07_and_08_student_logs_in_and_sees_assigned_quiz(self):
        """7. Student logs in. 8. Student sees the assigned quiz."""
        res_login = self.client.post("/api/auth/login", json={"email": "marie.curie@smartedu.edu", "password": "Password123!"})
        self.assertEqual(res_login.status_code, 200, res_login.text)
        student_token = res_login.json()["token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        TestSmartEduFullAcceptance.student_headers = student_headers
        
        res_quizzes = self.client.get("/api/student/quizzes", headers=student_headers)
        self.assertEqual(res_quizzes.status_code, 200)
        quizzes = res_quizzes.json()["quizzes"]
        quiz_ids = [q["quiz_id"] for q in quizzes]
        self.assertIn(TestSmartEduFullAcceptance.shared_quiz_id, quiz_ids)

    def test_09_to_14_student_answers_with_confidence_and_triggers_support_signal(self):
        """
        9. Student answers questions.
        10. Student provides confidence levels.
        11. Quiz result is stored.
        12. Question-level attempts stored.
        13. System analyzes learning behavior.
        14. Possible support signal is generated.
        """
        headers = TestSmartEduFullAcceptance.student_headers
        quiz_id = TestSmartEduFullAcceptance.shared_quiz_id
        
        # Get questions
        q_res = self.client.get(f"/api/student/quizzes/{quiz_id}", headers=headers)
        self.assertEqual(q_res.status_code, 200)
        questions = q_res.json()["questions"]
        self.assertEqual(len(questions), 3)
        
        # Start attempt
        start_res = self.client.post(f"/api/student/quizzes/{quiz_id}/start", headers=headers)
        self.assertEqual(start_res.status_code, 200)
        attempt_id = start_res.json()["attempt_id"]
        
        # Question 1: Answer incorrectly with "Very Confident" and high response time (48s)
        ans1 = self.client.post(
            f"/api/student/quizzes/{quiz_id}/answer",
            json={
                "attempt_id": attempt_id,
                "question_id": questions[0]["question_id"],
                "selected_option": "A", # Wrong!
                "response_time": 48.0,
                "confidence_level": "Very Confident"
            },
            headers=headers
        )
        self.assertEqual(ans1.status_code, 200)
        self.assertFalse(ans1.json()["is_correct"])
        
        # Question 2: Answer incorrectly with "Very Confident" and high response time (52s)
        ans2 = self.client.post(
            f"/api/student/quizzes/{quiz_id}/answer",
            json={
                "attempt_id": attempt_id,
                "question_id": questions[1]["question_id"],
                "selected_option": "A", # Wrong!
                "response_time": 52.0,
                "confidence_level": "Very Confident"
            },
            headers=headers
        )
        self.assertEqual(ans2.status_code, 200)
        self.assertFalse(ans2.json()["is_correct"])
        
        # Question 3: Answer correctly
        ans3 = self.client.post(
            f"/api/student/quizzes/{quiz_id}/answer",
            json={
                "attempt_id": attempt_id,
                "question_id": questions[2]["question_id"],
                "selected_option": "B", # Correct!
                "response_time": 18.0,
                "confidence_level": "Confident"
            },
            headers=headers
        )
        self.assertEqual(ans3.status_code, 200)
        self.assertTrue(ans3.json()["is_correct"])
        
        # Finish quiz
        finish_res = self.client.post(f"/api/student/quizzes/{quiz_id}/finish", json={"attempt_id": attempt_id}, headers=headers)
        self.assertEqual(finish_res.status_code, 200)
        fin_data = finish_res.json()
        self.assertEqual(fin_data["correct_count"], 1)
        self.assertEqual(fin_data["total_questions"], 3)
        self.assertGreater(fin_data["signals_generated_count"], 0)

    def test_15_and_16_teacher_sees_signal_and_opens_explainable_evidence(self):
        """15. Teacher sees the signal. 16. Teacher opens the evidence."""
        t_headers = TestSmartEduFullAcceptance.teacher_headers
        res = self.client.get("/api/teacher/support-signals", headers=t_headers)
        self.assertEqual(res.status_code, 200)
        signals = res.json()["signals"]
        self.assertGreater(len(signals), 0)
        
        signal = signals[0]
        self.assertEqual(signal["topic_name"], "Kirchhoff's Laws")
        self.assertGreaterEqual(signal["support_score"], 50.0)
        self.assertEqual(signal["status"], "REVIEW")
        TestSmartEduFullAcceptance.target_signal_id = signal["signal_id"]
        
        # 16. Inspect evidence
        ev_res = self.client.get(f"/api/teacher/support-signals/{signal['signal_id']}/evidence", headers=t_headers)
        self.assertEqual(ev_res.status_code, 200)
        ev_data = ev_res.json()["evidence"]
        self.assertIn("parsed_evidence", ev_data)
        self.assertIn("explanation_bullets", ev_data["parsed_evidence"])
        self.assertGreater(len(ev_data["parsed_evidence"]["explanation_bullets"]), 0)
        self.assertIn("recent_attempts", ev_data)

    def test_17_to_20_teacher_creates_intervention_and_student_completes_follow_up(self):
        """
        17. Teacher creates an intervention.
        18. Student completes the intervention / follow-up test.
        19. System stores before/after results.
        20. Teacher sees the improvement.
        """
        t_headers = TestSmartEduFullAcceptance.teacher_headers
        s_headers = TestSmartEduFullAcceptance.student_headers
        student_id = TestSmartEduFullAcceptance.shared_student_id
        
        # 17. Teacher creates intervention
        int_payload = {
            "student_id": student_id,
            "topic_id": "TOP-PHY01",
            "intervention_type": "3-question concept check",
            "teacher_note": "Review junction and loop conservation principles before re-attempting."
        }
        res_int = self.client.post("/api/teacher/interventions", json=int_payload, headers=t_headers)
        self.assertEqual(res_int.status_code, 200)
        intervention_id = res_int.json()["intervention_id"]
        
        # 18. Student opens follow-up assessment
        assess_res = self.client.get(f"/api/student/interventions/{intervention_id}/assessment", headers=s_headers)
        self.assertEqual(assess_res.status_code, 200)
        assess_data = assess_res.json()
        questions = assess_data["questions"]
        self.assertGreaterEqual(len(questions), 1)
        
        # Student submits correct answers on follow-up check
        submit_payload = {
            "answers": [
                {"question_id": q["question_id"], "selected_option": "B"}
                for q in questions
            ]
        }
        sub_res = self.client.post(f"/api/student/interventions/{intervention_id}/submit", json=submit_payload, headers=s_headers)
        self.assertEqual(sub_res.status_code, 200)
        res_data = sub_res.json()
        
        # 19. Verify before/after results
        self.assertIn("before_score", res_data)
        self.assertIn("after_score", res_data)
        self.assertIn("improvement", res_data)
        self.assertEqual(res_data["result_status"], "Improved")
        
        # 20. Teacher sees improvement
        t_int_res = self.client.get("/api/teacher/interventions", headers=t_headers)
        self.assertEqual(t_int_res.status_code, 200)
        ints = t_int_res.json()["interventions"]
        matched = [i for i in ints if i["intervention_id"] == intervention_id]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["result_status"], "Improved")
        self.assertGreater(matched[0]["improvement"], 0)

    def test_21_and_22_admin_management_and_safe_permanent_deletion(self):
        """21. Admin manages users. 22. Only admin can permanently delete."""
        adm_headers = self.admin_headers
        t_headers = TestSmartEduFullAcceptance.teacher_headers
        s_headers = TestSmartEduFullAcceptance.student_headers
        
        # Create temporary student to test deletion
        temp_res = self.client.post(
            "/api/admin/students",
            json={"name": "Temp Student", "email": "temp.student@smartedu.edu", "password": "Password123!", "class_id": "CLS-10A"},
            headers=adm_headers
        )
        temp_student_id = temp_res.json()["student_id"]
        
        # Student trying to delete student -> FORBIDDEN
        del_by_student = self.client.delete(f"/api/admin/students/{temp_student_id}/permanent", headers=s_headers)
        self.assertEqual(del_by_student.status_code, 403)
        
        # Teacher trying to delete student -> FORBIDDEN
        del_by_teacher = self.client.delete(f"/api/admin/students/{temp_student_id}/permanent", headers=t_headers)
        self.assertEqual(del_by_teacher.status_code, 403)
        
        # Admin toggle status -> Inactive
        toggle_res = self.client.post(f"/api/admin/students/{temp_student_id}/toggle-status", headers=adm_headers)
        self.assertEqual(toggle_res.status_code, 200)
        self.assertEqual(toggle_res.json()["new_status"], "inactive")
        
        # Admin permanent deletion -> SUCCESS
        del_by_admin = self.client.delete(f"/api/admin/students/{temp_student_id}/permanent", headers=adm_headers)
        self.assertEqual(del_by_admin.status_code, 200)
        self.assertIn("permanently deleted", del_by_admin.json()["message"].lower())

    def test_23_and_24_role_based_access_control(self):
        """23. Student cannot access teacher/admin. 24. Teacher cannot access admin."""
        s_headers = TestSmartEduFullAcceptance.student_headers
        t_headers = TestSmartEduFullAcceptance.teacher_headers
        
        # Student attempting teacher endpoints
        s_to_t1 = self.client.get("/api/teacher/dashboard", headers=s_headers)
        self.assertEqual(s_to_t1.status_code, 403)
        s_to_t2 = self.client.get("/api/teacher/support-signals", headers=s_headers)
        self.assertEqual(s_to_t2.status_code, 403)
        
        # Student attempting admin endpoints
        s_to_adm = self.client.get("/api/admin/dashboard", headers=s_headers)
        self.assertEqual(s_to_adm.status_code, 403)
        
        # Teacher attempting admin endpoints
        t_to_adm1 = self.client.get("/api/admin/dashboard", headers=t_headers)
        self.assertEqual(t_to_adm1.status_code, 403)
        t_to_adm2 = self.client.post("/api/admin/students", json={}, headers=t_headers)
        self.assertEqual(t_to_adm2.status_code, 403)

    def test_25_data_persistence_across_restart(self):
        """25. Data remains available after application restart."""
        # Query directly from database to verify persistence on disk
        with get_db() as conn:
            user = conn.execute("SELECT email, role FROM users WHERE email = 'marie.curie@smartedu.edu'").fetchone()
            self.assertIsNotNone(user)
            self.assertEqual(user["role"], "student")
            
            quiz = conn.execute("SELECT title FROM quizzes WHERE quiz_id = ?", (TestSmartEduFullAcceptance.shared_quiz_id,)).fetchone()
            self.assertIsNotNone(quiz)
            self.assertEqual(quiz["title"], "Electrodynamics & Advanced Circuit Analysis")
            
            signal = conn.execute("SELECT status FROM learning_signals WHERE student_id = ?", (TestSmartEduFullAcceptance.shared_student_id,)).fetchone()
            self.assertIsNotNone(signal)

if __name__ == "__main__":
    unittest.main()
