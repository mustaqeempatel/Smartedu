// SmartEdu Main App Controller & State Manager
const App = {
  currentUser: null,
  currentView: 'auth-view',
  studentCurrentTab: 'student-dashboard',
  teacherCurrentTab: 'teacher-dashboard',
  adminCurrentTab: 'admin-dashboard',

  async init() {
    this.initClock();
    this.bindEvents();

    const token = API.getToken();
    if (token) {
      try {
        const data = await API.getMe();
        this.currentUser = data.user;
        API.setUser(data.user);
        this.renderAuthenticatedApp();
      } catch (e) {
        console.warn("Session expired or invalid:", e);
        API.logout();
        this.showView('auth-view');
      }
    } else {
      this.showView('auth-view');
    }
  },

  initClock() {
    const updateTime = () => {
      const now = new Date();
      const hrs = now.getHours().toString().padStart(2, '0');
      const mins = now.getMinutes().toString().padStart(2, '0');
      const el = document.getElementById('phone-clock');
      if (el) el.textContent = `${hrs}:${mins}`;
    };
    updateTime();
    setInterval(updateTime, 30000);
  },

  bindEvents() {
    // Mode toggle between mobile frame and full view
    const toggleBtn = document.getElementById('toggle-view-mode-btn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('full-mode');
        const isFull = document.body.classList.contains('full-mode');
        toggleBtn.textContent = isFull ? 'Switch to Phone Frame' : 'Switch to Responsive View';
        const bar = document.querySelector('.view-mode-bar');
        if (bar) bar.classList.toggle('expanded-bar', isFull);
      });
    }

    // Login Form Submit
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const errBox = document.getElementById('login-error-box');
        const submitBtn = loginForm.querySelector('button[type="submit"]');

        errBox.style.display = 'none';
        submitBtn.textContent = 'Authenticating...';
        submitBtn.disabled = true;

        try {
          const res = await API.login(email, password);
          this.currentUser = res.user;
          this.renderAuthenticatedApp();
        } catch (err) {
          errBox.textContent = err.message;
          errBox.style.display = 'block';
        } finally {
          submitBtn.textContent = 'Sign In';
          submitBtn.disabled = false;
        }
      });
    }
  },

  async fastDemoLogin(role) {
    const errBox = document.getElementById('login-error-box');
    if (errBox) errBox.style.display = 'none';

    try {
      const res = await API.demoLogin(role);
      this.currentUser = res.user;
      this.renderAuthenticatedApp();
    } catch (err) {
      if (errBox) {
        errBox.textContent = err.message;
        errBox.style.display = 'block';
      } else {
        alert(err.message);
      }
    }
  },

  logout() {
    API.logout();
    this.currentUser = null;
    this.showView('auth-view');
  },

  renderAuthenticatedApp() {
    const user = this.currentUser;
    if (!user) return;

    // Update Header
    document.getElementById('header-user-tag').textContent = user.role;
    document.getElementById('header-user-tag').className = `user-role-tag role-${user.role}`;
    document.getElementById('app-header-bar').style.display = 'flex';

    if (user.role === 'student') {
      this.showView('student-view');
      document.getElementById('student-bottom-nav').style.display = 'flex';
      document.getElementById('teacher-bottom-nav').style.display = 'none';
      this.switchStudentTab('student-dashboard');
    } else if (user.role === 'teacher') {
      this.showView('teacher-view');
      document.getElementById('student-bottom-nav').style.display = 'none';
      document.getElementById('teacher-bottom-nav').style.display = 'flex';
      this.switchTeacherTab('teacher-dashboard');
    } else if (user.role === 'admin') {
      this.showView('admin-view');
      document.getElementById('student-bottom-nav').style.display = 'none';
      document.getElementById('teacher-bottom-nav').style.display = 'none';
      this.switchAdminTab('admin-dashboard');
    }
  },

  showView(viewId) {
    this.currentView = viewId;
    const views = ['auth-view', 'student-view', 'student-quiz-runner-view', 'teacher-view', 'admin-view'];
    views.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = (id === viewId) ? 'flex' : 'none';
    });

    if (viewId === 'auth-view') {
      document.getElementById('app-header-bar').style.display = 'none';
      document.getElementById('student-bottom-nav').style.display = 'none';
      document.getElementById('teacher-bottom-nav').style.display = 'none';
    }
  },

  switchStudentTab(tabId) {
    this.studentCurrentTab = tabId;
    this.showView('student-view');

    // Update bottom nav active state
    ['student-dashboard', 'student-quizzes', 'student-interventions'].forEach(tab => {
      const btn = document.getElementById(`nav-${tab}`);
      if (btn) btn.classList.toggle('active', tab === tabId);

      const content = document.getElementById(`${tab}-content`);
      if (content) content.style.display = (tab === tabId) ? 'block' : 'none';
    });

    if (tabId === 'student-dashboard') StudentController.loadDashboard();
    else if (tabId === 'student-quizzes') StudentController.loadQuizzesList();
    else if (tabId === 'student-interventions') StudentController.loadInterventions();
  },

  switchTeacherTab(tabId) {
    this.teacherCurrentTab = tabId;
    this.showView('teacher-view');

    // Update bottom nav active state
    ['teacher-dashboard', 'teacher-signals', 'teacher-quizzes', 'teacher-interventions'].forEach(tab => {
      const btn = document.getElementById(`nav-${tab}`);
      if (btn) btn.classList.toggle('active', tab === tabId);

      const content = document.getElementById(`${tab}-content`);
      if (content) content.style.display = (tab === tabId) ? 'block' : 'none';
    });

    if (tabId === 'teacher-dashboard') TeacherController.loadDashboard();
    else if (tabId === 'teacher-signals') TeacherController.loadSupportSignals();
    else if (tabId === 'teacher-quizzes') TeacherController.loadQuizBuilder();
    else if (tabId === 'teacher-interventions') TeacherController.loadInterventions();
  },

  switchAdminTab(tabId) {
    this.adminCurrentTab = tabId;
    this.showView('admin-view');

    ['admin-dashboard', 'admin-students', 'admin-teachers'].forEach(tab => {
      const btn = document.getElementById(`subtab-${tab}`);
      if (btn) btn.classList.toggle('active', tab === tabId);

      const content = document.getElementById(`${tab}-content`);
      if (content) content.style.display = (tab === tabId) ? 'block' : 'none';
    });

    if (tabId === 'admin-dashboard') AdminController.loadDashboard();
    else if (tabId === 'admin-students') AdminController.loadStudents();
    else if (tabId === 'admin-teachers') AdminController.loadTeachers();
  },

  showModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('active');
  },

  closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove('active');
  }
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
