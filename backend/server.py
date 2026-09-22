import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.seed_data import seed_database
import backend.routes_auth as auth_routes
import backend.routes_student as student_routes
import backend.routes_teacher as teacher_routes
import backend.routes_admin as admin_routes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

async def index_handler(request):
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_file)

async def presentation_handler(request):
    pres_file = os.path.join(FRONTEND_DIR, "presentation.html")
    return FileResponse(pres_file)

async def download_pptx_handler(request):
    pptx_file = os.path.join(BASE_DIR, "smartedu_hackathon_presentation.pptx")
    return FileResponse(pptx_file, filename="smartedu_hackathon_presentation.pptx", media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")

async def health_handler(request):
    return JSONResponse({"status": "healthy", "service": "SmartEdu API", "version": "1.0.0"})

routes = [
    # Health check & presentations
    Route("/api/health", health_handler, methods=["GET"]),
    Route("/presentation.html", presentation_handler, methods=["GET"]),
    Route("/presentation", presentation_handler, methods=["GET"]),
    Route("/api/download/presentation", download_pptx_handler, methods=["GET"]),
    
    # Auth endpoints
    Route("/api/auth/login", auth_routes.login, methods=["POST"]),
    Route("/api/auth/demo-login", auth_routes.demo_login, methods=["POST"]),
    Route("/api/auth/me", auth_routes.me, methods=["GET"]),
    Route("/api/auth/logout", auth_routes.logout, methods=["POST"]),
    
    # Student endpoints
    Route("/api/student/dashboard", student_routes.get_dashboard, methods=["GET"]),
    Route("/api/student/quizzes", student_routes.list_quizzes, methods=["GET"]),
    Route("/api/student/quizzes/{quiz_id}", student_routes.get_quiz_details, methods=["GET"]),
    Route("/api/student/quizzes/{quiz_id}/start", student_routes.start_quiz, methods=["POST"]),
    Route("/api/student/quizzes/{quiz_id}/answer", student_routes.answer_question, methods=["POST"]),
    Route("/api/student/quizzes/{quiz_id}/finish", student_routes.finish_quiz, methods=["POST"]),
    Route("/api/student/interventions", student_routes.list_interventions, methods=["GET"]),
    Route("/api/student/interventions/{intervention_id}/assessment", student_routes.get_intervention_assessment, methods=["GET"]),
    Route("/api/student/interventions/{intervention_id}/submit", student_routes.submit_intervention_assessment, methods=["POST"]),
    
    # Teacher endpoints
    Route("/api/teacher/dashboard", teacher_routes.get_dashboard, methods=["GET"]),
    Route("/api/teacher/classes", teacher_routes.list_assigned_classes, methods=["GET"]),
    Route("/api/teacher/classes/{class_id}/students", teacher_routes.list_class_students, methods=["GET"]),
    Route("/api/teacher/quizzes", teacher_routes.list_quizzes, methods=["GET"]),
    Route("/api/teacher/quizzes", teacher_routes.create_quiz, methods=["POST"]),
    Route("/api/teacher/quizzes/{quiz_id}/questions", teacher_routes.add_questions_to_quiz, methods=["POST"]),
    Route("/api/teacher/quizzes/{quiz_id}", teacher_routes.delete_quiz, methods=["DELETE"]),
    Route("/api/teacher/support-signals", teacher_routes.list_support_signals, methods=["GET"]),
    Route("/api/teacher/support-signals/{signal_id}/evidence", teacher_routes.get_signal_evidence, methods=["GET"]),
    Route("/api/teacher/interventions", teacher_routes.list_interventions, methods=["GET"]),
    Route("/api/teacher/interventions", teacher_routes.create_intervention, methods=["POST"]),
    
    # Admin endpoints
    Route("/api/admin/dashboard", admin_routes.get_dashboard, methods=["GET"]),
    Route("/api/admin/students", admin_routes.list_students, methods=["GET"]),
    Route("/api/admin/students", admin_routes.create_student, methods=["POST"]),
    Route("/api/admin/students/{student_id}", admin_routes.update_student, methods=["PUT"]),
    Route("/api/admin/students/{student_id}/toggle-status", admin_routes.toggle_student_status, methods=["POST"]),
    Route("/api/admin/students/{student_id}/permanent", admin_routes.delete_student_permanently, methods=["DELETE"]),
    Route("/api/admin/teachers", admin_routes.list_teachers, methods=["GET"]),
    Route("/api/admin/teachers", admin_routes.create_teacher, methods=["POST"]),
    Route("/api/admin/teachers/{teacher_id}/toggle-status", admin_routes.toggle_teacher_status, methods=["POST"]),
    Route("/api/admin/teachers/{teacher_id}/permanent", admin_routes.delete_teacher_permanently, methods=["DELETE"]),
    Route("/api/admin/assign-teacher", admin_routes.assign_teacher_to_class, methods=["POST"]),
    Route("/api/admin/assign-student", admin_routes.assign_student_to_class, methods=["POST"]),
    Route("/api/admin/classes", admin_routes.list_classes, methods=["GET"]),
    Route("/api/admin/classes", admin_routes.create_class, methods=["POST"]),
    Route("/api/admin/curriculum", admin_routes.get_curriculum, methods=["GET"]),
    
    # Static files and root route
    Route("/", index_handler, methods=["GET"]),
    Mount("/css", app=StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css"),
    Mount("/js", app=StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js"),
    Mount("/static", app=StaticFiles(directory=FRONTEND_DIR), name="static"),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

def startup():
    init_db()
    seed_database()

if __name__ == "__main__":
    import uvicorn
    startup()
    uvicorn.run(app, host="127.0.0.1", port=8000)
