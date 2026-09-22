import base64
import hashlib
import hmac
import json
import os
import time
from starlette.responses import JSONResponse
from backend.database import get_db

SECRET_KEY = os.environ.get("SMARTEDU_SECRET_KEY", "smartedu-super-secret-production-key-2026")

def hash_password(password: str, salt_hex: str = None) -> tuple[str, str]:
    if salt_hex is None:
        salt = os.urandom(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return key.hex(), salt_hex

def verify_password(password: str, stored_hash: str, salt_hex: str) -> bool:
    new_hash, _ = hash_password(password, salt_hex)
    return hmac.compare_digest(new_hash, stored_hash)

def create_token(user_id: str, email: str, role: str, expires_in_seconds: int = 86400) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + expires_in_seconds
    }
    payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')
    
    signature = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"

def verify_token(token: str) -> dict | None:
    if not token or '.' not in token:
        return None
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return None
        
        # Add padding back if necessary
        padded = payload_b64 + '=' * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8')
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

def get_current_user(request):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    elif "token" in request.query_params:
        token = request.query_params["token"]
        
    if not token:
        return None
        
    payload = verify_token(token)
    if not payload:
        return None
        
    user_id = payload.get("user_id")
    with get_db() as conn:
        user = conn.execute("SELECT id, email, role, status FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user or user["status"] != "active":
            return None
            
        user_dict = dict(user)
        # Load role specific profile
        if user["role"] == "student":
            stu = conn.execute(
                "SELECT student_id, name, class_id, section, admission_number FROM students WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            if stu:
                user_dict["student"] = dict(stu)
        elif user["role"] == "teacher":
            tch = conn.execute(
                "SELECT teacher_id, name, department, employee_number FROM teachers WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            if tch:
                user_dict["teacher"] = dict(tch)
                # Fetch assigned classes
                classes = conn.execute(
                    """
                    SELECT tc.class_id, tc.subject_id, c.class_name, c.section, s.subject_name
                    FROM teacher_classes tc
                    JOIN classes c ON tc.class_id = c.class_id
                    JOIN subjects s ON tc.subject_id = s.subject_id
                    WHERE tc.teacher_id = ?
                    """,
                    (tch["teacher_id"],)
                ).fetchall()
                user_dict["assigned_classes"] = [dict(c) for c in classes]
                
        return user_dict

def can_teacher_access_class(teacher_id: str, class_id: str) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM teacher_classes WHERE teacher_id = ? AND class_id = ?",
            (teacher_id, class_id)
        ).fetchone()
        return bool(row)

def can_teacher_access_student(teacher_id: str, student_id: str) -> bool:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM students s
            JOIN teacher_classes tc ON s.class_id = tc.class_id
            WHERE s.student_id = ? AND tc.teacher_id = ?
            """,
            (student_id, teacher_id)
        ).fetchone()
        return bool(row)
