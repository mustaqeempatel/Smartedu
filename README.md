# 🎓 SMARTEDU

## AI-Powered Hidden Academic Support Detection System

SmartEdu is a full-stack intelligent education platform designed to connect **Students, Teachers, and Administrators** in one centralized system.

The platform provides authentication, role-based dashboards, academic support tools, monitoring features, and an intelligent approach to identifying students who may need additional academic assistance.

---

## 🌐 Live Demo

🚀 **Live Application:**

https://smartedu-ljiz.onrender.com/

The application is deployed using **Render** and is accessible through HTTPS.

---

## 📌 Project Overview

SmartEdu aims to create a smarter and more supportive academic environment by bringing students, teachers, and administrators together through a single platform.

The system provides different experiences based on the user's role:

- 👨‍🎓 Student
- 👨‍🏫 Teacher
- 🛡️ Administrator

The platform is designed to help educational institutions manage academic activities while supporting early identification of students who may require additional academic attention.

---

## ✨ Key Features

### 👨‍🎓 Student Module

- Student authentication
- Student dashboard
- Academic support system
- Access to learning resources
- Academic information management
- Personalized student experience

### 👨‍🏫 Teacher Module

- Teacher authentication
- Teacher dashboard
- Student monitoring
- Academic support management
- Access to student-related information
- Teacher-focused management tools

### 🛡️ Admin Module

- Administrator authentication
- Admin dashboard
- User management
- System monitoring
- Academic data management
- Platform administration

---

## 🤖 Smart Academic Support

One of the main objectives of SmartEdu is to identify students who may require additional academic support.

The system can be extended to analyze academic indicators and help teachers or administrators provide appropriate support at an early stage.

This approach focuses on:

- 📊 Academic monitoring
- 🔎 Student support detection
- 📈 Performance analysis
- 👨‍🏫 Teacher intervention
- 🎯 Personalized academic assistance

---

## 🏗️ Project Architecture

```text
SMARTEDU
│
├── Frontend
│   ├── HTML
│   ├── CSS
│   └── JavaScript
│
├── Backend
│   ├── Authentication
│   ├── Database
│   ├── API Routes
│   ├── Student Routes
│   ├── Teacher Routes
│   └── Admin Routes
│
├── Database
│   └── SQLite
│
└── Deployment
    └── Render
📂 Project Structure
smartedu/
│
├── backend/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── engine.py
│   ├── routes_admin.py
│   ├── routes_auth.py
│   ├── routes_student.py
│   ├── routes_teacher.py
│   ├── seed_data.py
│   └── server.py
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── presentation.html
│   └── ...
│
├── tests/
│   └── test_smartedu.py
│
├── generate_pptx.py
├── requirements.txt
├── run.py
├── smartedu.db
├── .gitignore
└── README.md

🛠️ Technology Stack
Frontend
HTML5
CSS3
JavaScript
Backend
Python
Starlette
Uvicorn
Database
SQLite
Testing
Python Testing
Starlette TestClient
Deployment
Render
HTTPS
Version Control
Git
GitHub
🔐 Authentication

SmartEdu provides role-based authentication for different users.
                 SMARTEDU
                    │
        ┌───────────┼───────────┐
        │           │           │
     Student     Teacher       Admin
        │           │           │
    Dashboard   Dashboard   Dashboard
        │           │           │
        └───────────┼───────────┘
                    │
             SmartEdu System
🚀 Running the Project Locally
1. Clone the Repository
git clone https://github.com/mustaqeempat/Smartedu.git
2. Navigate to the Project
cd Smartedu
3. Create a Virtual Environment
python -m venv .venv
4. Activate the Virtual Environment
Windows
.venv\Scripts\activate
Linux / macOS
source .venv/bin/activate
5. Install Dependencies
pip install -r requirements.txt
6. Start the Backend
uvicorn backend.server:app --host 0.0.0.0 --port 8000
7. Open the Application
http://localhost:8000
🌍 Production Deployment

SmartEdu is deployed on Render.

Production URL
https://smartedu-ljiz.onrender.com/
Render Start Command
uvicorn backend.server:app --host 0.0.0.0 --port $PORT
Build Command
pip install -r requirements.txt
🧪 Testing

The project contains automated tests for important SmartEdu functionality.

Run the tests using:

pytest

or:

python -m pytest
📊 Main Modules
| Module         | Purpose                                  |
| -------------- | ---------------------------------------- |
| Authentication | Login and user authentication            |
| Student        | Student dashboard and academic support   |
| Teacher        | Student monitoring and teacher functions |
| Admin          | System and user administration           |
| Database       | Data storage and management              |
| Engine         | Smart academic-support logic             |
| API            | Backend communication                    |
| Testing        | Automated application testing            |

🎯 Project Objectives

The major objectives of SmartEdu are:

Create a centralized educational platform.
Provide separate interfaces for Students, Teachers, and Administrators.
Improve communication between academic stakeholders.
Support early identification of students who may need academic assistance.
Provide a scalable foundation for intelligent education systems.
Make academic monitoring easier and more organized.
🔮 Future Enhancements

Possible future improvements include:

🤖 Advanced AI-based student support detection
📊 Interactive analytics dashboards
📈 Student performance prediction
🔔 Automated academic alerts
💬 Teacher-student communication
📚 Learning resource management
🧠 Personalized learning recommendations
📱 Mobile application
☁️ Cloud database integration
🔐 Enhanced security and authentication
📊 Advanced academic reports
💡 Why SmartEdu?

Traditional educational systems may focus mainly on grades and attendance.

SmartEdu aims to go further by creating a system that can help identify students who may require additional academic support and make it easier for educators to respond.

Student Data
     │
     ▼
Academic Analysis
     │
     ▼
Support Detection
     │
     ▼
Teacher / Admin
     │
     ▼
Academic Intervention
     │
     ▼
Better Student Support
🖥️ Live Application

🚀 Try SmartEdu Online:

https://smartedu-ljiz.onrender.com/

👨‍💻 Developer

Mustaqeem Patel

GitHub:

https://github.com/mustaqeempat/Smartedu

📜 License

This project is developed for educational and demonstration purposes.

⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

🎓 SMARTEDU
AI-Powered Hidden Academic Support Detection System

Learn • Detect • Support • Improve

🌐 Live: https://smartedu-ljiz.onrender.com/
