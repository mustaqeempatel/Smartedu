import json
import uuid
from starlette.responses import JSONResponse
from backend.auth import hash_password, verify_password, create_token, get_current_user
from backend.database import get_db

async def login(request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    
    if not email or not password:
        return JSONResponse({"error": "Email and password are required"}, status_code=400)
        
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, email, password_hash, salt, role, status FROM users WHERE LOWER(email) = ?",
            (email,)
        ).fetchone()
        
        if not user:
            return JSONResponse({"error": "Invalid email or password"}, status_code=401)
            
        if user["status"] != "active":
            return JSONResponse({"error": "Account is deactivated. Please contact an administrator."}, status_code=403)
            
        if not verify_password(password, user["password_hash"], user["salt"]):
            return JSONResponse({"error": "Invalid email or password"}, status_code=401)
            
        token = create_token(user["id"], user["email"], user["role"])
        
        user_info = {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"]
        }
        
        if user["role"] == "student":
            stu = conn.execute("SELECT student_id, name, class_id, section, admission_number FROM students WHERE user_id = ?", (user["id"],)).fetchone()
            if stu:
                user_info["student"] = dict(stu)
        elif user["role"] == "teacher":
            tch = conn.execute("SELECT teacher_id, name, department, employee_number FROM teachers WHERE user_id = ?", (user["id"],)).fetchone()
            if tch:
                user_info["teacher"] = dict(tch)
                
        return JSONResponse({
            "message": "Login successful",
            "token": token,
            "user": user_info
        })

async def demo_login(request):
    """Allows rapid 1-click evaluator login for demonstration and testing."""
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    target_role = body.get("role", "teacher").lower()
    
    with get_db() as conn:
        if target_role == "student":
            # Pick demo student Alex Morgan (or first active student)
            user = conn.execute(
                """
                SELECT u.id, u.email, u.role, u.status 
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.role = 'student' AND u.status = 'active'
                ORDER BY CASE WHEN s.name LIKE '%Alex Morgan%' THEN 0 ELSE 1 END, s.created_at ASC
                LIMIT 1
                """
            ).fetchone()
        elif target_role == "teacher":
            # Pick demo teacher Dr. Sarah Jenkins (or first active teacher)
            user = conn.execute(
                """
                SELECT u.id, u.email, u.role, u.status 
                FROM users u
                JOIN teachers t ON u.id = t.user_id
                WHERE u.role = 'teacher' AND u.status = 'active'
                ORDER BY CASE WHEN t.name LIKE '%Sarah Jenkins%' THEN 0 ELSE 1 END, t.created_at ASC
                LIMIT 1
                """
            ).fetchone()
        else: # admin
            user = conn.execute(
                "SELECT id, email, role, status FROM users WHERE role = 'admin' AND status = 'active' LIMIT 1"
            ).fetchone()
            
        if not user:
            return JSONResponse({"error": f"No active {target_role} demo account found"}, status_code=404)
            
        token = create_token(user["id"], user["email"], user["role"])
        
        user_info = {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"]
        }
        
        if user["role"] == "student":
            stu = conn.execute("SELECT student_id, name, class_id, section, admission_number FROM students WHERE user_id = ?", (user["id"],)).fetchone()
            if stu:
                user_info["student"] = dict(stu)
        elif user["role"] == "teacher":
            tch = conn.execute("SELECT teacher_id, name, department, employee_number FROM teachers WHERE user_id = ?", (user["id"],)).fetchone()
            if tch:
                user_info["teacher"] = dict(tch)
                
        return JSONResponse({
            "message": f"Demo login as {target_role} successful",
            "token": token,
            "user": user_info
        })

async def me(request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Unauthorized or session expired"}, status_code=401)
    return JSONResponse({"user": user})

async def logout(request):
    return JSONResponse({"message": "Logged out successfully"})
