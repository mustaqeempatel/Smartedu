// SmartEdu API Client
const API = {
  getToken() {
    return localStorage.getItem('smartedu_token');
  },
  
  setToken(token) {
    if (token) {
      localStorage.setItem('smartedu_token', token);
    } else {
      localStorage.removeItem('smartedu_token');
    }
  },
  
  getUser() {
    try {
      return JSON.parse(localStorage.getItem('smartedu_user'));
    } catch {
      return null;
    }
  },
  
  setUser(user) {
    if (user) {
      localStorage.setItem('smartedu_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('smartedu_user');
    }
  },
  
  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const url = path.startsWith('http') ? path : path;
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      if (response.status === 401 && !path.includes('/auth/login')) {
        this.setToken(null);
        this.setUser(null);
        window.location.reload();
      }
      throw new Error(data.error || `Request failed with status ${response.status}`);
    }
    
    return data;
  },

  // Authentication
  async login(email, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.setToken(data.token);
    this.setUser(data.user);
    return data;
  },
  
  async demoLogin(role) {
    const data = await this.request('/api/auth/demo-login', {
      method: 'POST',
      body: JSON.stringify({ role })
    });
    this.setToken(data.token);
    this.setUser(data.user);
    return data;
  },
  
  async getMe() {
    return this.request('/api/auth/me');
  },
  
  logout() {
    this.setToken(null);
    this.setUser(null);
  },

  // Student Endpoints
  async getStudentDashboard() {
    return this.request('/api/student/dashboard');
  },
  
  async getStudentQuizzes() {
    return this.request('/api/student/quizzes');
  },
  
  async getQuizDetails(quizId) {
    return this.request(`/api/student/quizzes/${quizId}`);
  },
  
  async startQuiz(quizId) {
    return this.request(`/api/student/quizzes/${quizId}/start`, { method: 'POST' });
  },
  
  async answerQuestion(quizId, payload) {
    return this.request(`/api/student/quizzes/${quizId}/answer`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async finishQuiz(quizId, attemptId) {
    return this.request(`/api/student/quizzes/${quizId}/finish`, {
      method: 'POST',
      body: JSON.stringify({ attempt_id: attemptId })
    });
  },
  
  async getStudentInterventions() {
    return this.request('/api/student/interventions');
  },
  
  async getInterventionAssessment(interventionId) {
    return this.request(`/api/student/interventions/${interventionId}/assessment`);
  },
  
  async submitInterventionAssessment(interventionId, answers) {
    return this.request(`/api/student/interventions/${interventionId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers })
    });
  },

  // Teacher Endpoints
  async getTeacherDashboard() {
    return this.request('/api/teacher/dashboard');
  },
  
  async getAssignedClasses() {
    return this.request('/api/teacher/classes');
  },
  
  async getClassStudents(classId) {
    return this.request(`/api/teacher/classes/${classId}/students`);
  },
  
  async getTeacherQuizzes() {
    return this.request('/api/teacher/quizzes');
  },
  
  async createQuiz(payload) {
    return this.request('/api/teacher/quizzes', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async addQuestions(quizId, questions) {
    return this.request(`/api/teacher/quizzes/${quizId}/questions`, {
      method: 'POST',
      body: JSON.stringify({ questions })
    });
  },
  
  async deleteQuiz(quizId) {
    return this.request(`/api/teacher/quizzes/${quizId}`, { method: 'DELETE' });
  },
  
  async getSupportSignals() {
    return this.request('/api/teacher/support-signals');
  },
  
  async getSignalEvidence(signalId) {
    return this.request(`/api/teacher/support-signals/${signalId}/evidence`);
  },
  
  async createIntervention(payload) {
    return this.request('/api/teacher/interventions', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async getTeacherInterventions() {
    return this.request('/api/teacher/interventions');
  },

  // Admin Endpoints
  async getAdminDashboard() {
    return this.request('/api/admin/dashboard');
  },
  
  async getAdminStudents() {
    return this.request('/api/admin/students');
  },
  
  async createStudent(payload) {
    return this.request('/api/admin/students', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async toggleStudentStatus(studentId) {
    return this.request(`/api/admin/students/${studentId}/toggle-status`, { method: 'POST' });
  },
  
  async deleteStudentPermanently(studentId) {
    return this.request(`/api/admin/students/${studentId}/permanent`, { method: 'DELETE' });
  },
  
  async getAdminTeachers() {
    return this.request('/api/admin/teachers');
  },
  
  async createTeacher(payload) {
    return this.request('/api/admin/teachers', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async toggleTeacherStatus(teacherId) {
    return this.request(`/api/admin/teachers/${teacherId}/toggle-status`, { method: 'POST' });
  },
  
  async deleteTeacherPermanently(teacherId) {
    return this.request(`/api/admin/teachers/${teacherId}/permanent`, { method: 'DELETE' });
  },
  
  async assignTeacherToClass(payload) {
    return this.request('/api/admin/assign-teacher', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async assignStudentToClass(payload) {
    return this.request('/api/admin/assign-student', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async getClasses() {
    return this.request('/api/admin/classes');
  },
  
  async createClass(payload) {
    return this.request('/api/admin/classes', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  
  async getCurriculum() {
    return this.request('/api/admin/curriculum');
  }
};
