// SmartEdu Admin Controller
const AdminController = {
  currentClasses: [],

  async loadDashboard() {
    const container = document.getElementById('admin-view-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading administrative console...</p></div>`;
    
    try {
      const data = await API.getAdminDashboard();
      this.renderDashboard(container, data);
    } catch (err) {
      container.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  renderDashboard(container, data) {
    const { stats, recent_logs } = data;
    
    let html = `
      <div class="card" style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: #fff; border: none;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h2 style="font-size:18px; font-weight:800;">Administrator Console</h2>
            <p style="font-size:12px; opacity:0.85; margin-top:2px;">Complete system oversight, safe user provisioning & audit trails</p>
          </div>
          <span class="badge" style="background:#FEF3C7; color:#B45309;">Admin Root</span>
        </div>
      </div>

      <!-- System Stats Grid -->
      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-value">${stats.students}</span>
          <span class="stat-label">Students</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.teachers}</span>
          <span class="stat-label">Teachers</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.classes}</span>
          <span class="stat-label">Classes</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.subjects}</span>
          <span class="stat-label">Subjects</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.quizzes}</span>
          <span class="stat-label">Total Quizzes</span>
        </div>
        <div class="stat-box">
          <span class="stat-value" style="color:#D97706;">${stats.active_support_signals}</span>
          <span class="stat-label">Active Support Signals</span>
        </div>
      </div>

      <!-- Quick Action Buttons -->
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <button class="btn btn-primary btn-sm" onclick="AdminController.openCreateStudentModal()">
          + Add Student
        </button>
        <button class="btn btn-secondary btn-sm" onclick="AdminController.openCreateTeacherModal()">
          + Add Teacher
        </button>
      </div>

      <!-- Audit Logs Card -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">System Audit Log</span>
          <span class="badge" style="background:#F1F5F9; color:#475569;">Security</span>
        </div>
        <div style="display:flex; flex-direction:column; gap:8px;">
    `;

    if (!recent_logs || recent_logs.length === 0) {
      html += `<p style="font-size:12px; color:var(--text-muted)">No audit log entries recorded yet.</p>`;
    } else {
      recent_logs.forEach(l => {
        html += `
          <div style="font-size:12px; padding:6px 0; border-bottom:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <span class="badge" style="background:#E2E8F0; color:#1E293B; font-size:10px;">${l.action}</span>
              <span style="color:var(--text-main); margin-left:6px;">${l.details || l.target_type}</span>
            </div>
            <span style="font-size:10px; color:var(--text-muted);">${(l.timestamp || '').slice(11, 19)}</span>
          </div>
        `;
      });
    }

    html += `
        </div>
      </div>
    `;

    container.innerHTML = html;
  },

  async loadStudents() {
    App.switchAdminTab('admin-students');
    const container = document.getElementById('admin-students-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading students list...</p></div>`;

    try {
      const [studentsData, classesData] = await Promise.all([
        API.getAdminStudents(),
        API.getClasses()
      ]);
      this.currentClasses = classesData.classes;

      let html = `
        <div class="card-header" style="margin-bottom:8px;">
          <div>
            <h3 style="font-size:16px; font-weight:700;">Students Management</h3>
            <p style="font-size:12px; color:var(--text-muted)">Total ${studentsData.students.length} students enrolled</p>
          </div>
          <button class="btn btn-primary btn-sm" onclick="AdminController.openCreateStudentModal()">+ Add Student</button>
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
      `;

      studentsData.students.forEach(s => {
        const isActive = s.status === 'active';
        html += `
          <div class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
                <h4 style="font-size:14px; font-weight:700;">${s.name}</h4>
                <div style="font-size:11px; color:var(--text-muted);">${s.email} • Adm: ${s.admission_number || 'N/A'}</div>
                <div style="font-size:11px; color:var(--primary); font-weight:600; margin-top:2px;">
                  ${s.class_name ? `${s.class_name} (Sec ${s.section})` : 'Unassigned Class'}
                </div>
              </div>
              <span class="badge ${isActive ? 'badge-improved' : 'badge-review'}" style="font-size:10px;">
                ${s.status}
              </span>
            </div>

            <div style="display:flex; justify-content:flex-end; gap:6px; margin-top:8px; border-top:1px solid var(--border-color); padding-top:8px;">
              <button class="btn btn-secondary btn-sm" style="font-size:11px; padding:4px 8px;" onclick="AdminController.toggleStudent('${s.student_id}')">
                ${isActive ? 'Deactivate' : 'Activate'}
              </button>
              <button class="btn btn-danger btn-sm" style="font-size:11px; padding:4px 8px;" onclick="AdminController.confirmDeleteUser('student', '${s.student_id}', '${s.name}')">
                Delete Permanently
              </button>
            </div>
          </div>
        `;
      });

      html += `</div>`;
      container.innerHTML = html;
    } catch (err) {
      container.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  async loadTeachers() {
    App.switchAdminTab('admin-teachers');
    const container = document.getElementById('admin-teachers-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading teachers list...</p></div>`;

    try {
      const data = await API.getAdminTeachers();

      let html = `
        <div class="card-header" style="margin-bottom:8px;">
          <div>
            <h3 style="font-size:16px; font-weight:700;">Teachers Management</h3>
            <p style="font-size:12px; color:var(--text-muted)">Total ${data.teachers.length} faculty members</p>
          </div>
          <button class="btn btn-primary btn-sm" onclick="AdminController.openCreateTeacherModal()">+ Add Teacher</button>
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
      `;

      data.teachers.forEach(t => {
        const isActive = t.status === 'active';
        html += `
          <div class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
                <h4 style="font-size:14px; font-weight:700;">${t.name}</h4>
                <div style="font-size:11px; color:var(--text-muted);">${t.email} • Emp #${t.employee_number || 'N/A'}</div>
                <div style="font-size:11px; color:var(--text-main); margin-top:2px;">
                  Department: <strong>${t.department}</strong> • Assigned Classes: ${t.assigned_classes_count}
                </div>
              </div>
              <span class="badge ${isActive ? 'badge-improved' : 'badge-review'}" style="font-size:10px;">
                ${t.status}
              </span>
            </div>

            <div style="display:flex; justify-content:flex-end; gap:6px; margin-top:8px; border-top:1px solid var(--border-color); padding-top:8px;">
              <button class="btn btn-secondary btn-sm" style="font-size:11px; padding:4px 8px;" onclick="AdminController.openAssignTeacherModal('${t.teacher_id}', '${t.name}')">
                Assign Class
              </button>
              <button class="btn btn-secondary btn-sm" style="font-size:11px; padding:4px 8px;" onclick="AdminController.toggleTeacher('${t.teacher_id}')">
                ${isActive ? 'Deactivate' : 'Activate'}
              </button>
              <button class="btn btn-danger btn-sm" style="font-size:11px; padding:4px 8px;" onclick="AdminController.confirmDeleteUser('teacher', '${t.teacher_id}', '${t.name}')">
                Delete Permanently
              </button>
            </div>
          </div>
        `;
      });

      html += `</div>`;
      container.innerHTML = html;
    } catch (err) {
      container.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  openCreateStudentModal() {
    App.showModal('admin-action-modal');
    const modalContent = document.getElementById('admin-action-content');
    let classOptions = this.currentClasses.map(c => `<option value="${c.class_id}">${c.class_name} (Sec ${c.section})</option>`).join('');

    modalContent.innerHTML = `
      <h3 style="font-size:16px; font-weight:800; border-bottom:1px solid var(--border-color); padding-bottom:8px;">Add New Student</h3>
      <form id="admin-create-student-form" onsubmit="AdminController.submitCreateStudent(event)">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input type="text" id="cs-name" class="form-input" placeholder="e.g. John Doe" required>
        </div>
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input type="email" id="cs-email" class="form-input" placeholder="john.doe@smartedu.edu" required>
        </div>
        <div class="form-group">
          <label class="form-label">Temporary Password</label>
          <input type="password" id="cs-pwd" class="form-input" value="Password123!" required>
        </div>
        <div style="display:grid; grid-template-columns:2fr 1fr; gap:8px;">
          <div class="form-group">
            <label class="form-label">Class</label>
            <select id="cs-class" class="form-select">
              <option value="">-- Select Class --</option>
              ${classOptions}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Section</label>
            <input type="text" id="cs-sec" class="form-input" value="A">
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%; margin-top:8px;">
          Create Student Account
        </button>
      </form>
    `;
  },

  async submitCreateStudent(event) {
    event.preventDefault();
    const name = document.getElementById('cs-name').value.trim();
    const email = document.getElementById('cs-email').value.trim();
    const password = document.getElementById('cs-pwd').value;
    const classId = document.getElementById('cs-class').value || null;
    const section = document.getElementById('cs-sec').value || 'A';

    try {
      await API.createStudent({
        name,
        email,
        password,
        class_id: classId,
        section
      });
      App.closeModal('admin-action-modal');
      alert("Student created successfully!");
      AdminController.loadStudents();
    } catch (err) {
      alert(`Error creating student: ${err.message}`);
    }
  },

  openCreateTeacherModal() {
    App.showModal('admin-action-modal');
    const modalContent = document.getElementById('admin-action-content');

    modalContent.innerHTML = `
      <h3 style="font-size:16px; font-weight:800; border-bottom:1px solid var(--border-color); padding-bottom:8px;">Add New Teacher</h3>
      <form id="admin-create-teacher-form" onsubmit="AdminController.submitCreateTeacher(event)">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input type="text" id="ct-name" class="form-input" placeholder="e.g. Dr. Alan Turing" required>
        </div>
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input type="email" id="ct-email" class="form-input" placeholder="alan.turing@smartedu.edu" required>
        </div>
        <div class="form-group">
          <label class="form-label">Department</label>
          <input type="text" id="ct-dept" class="form-input" placeholder="e.g. Physics" value="Science" required>
        </div>
        <div class="form-group">
          <label class="form-label">Temporary Password</label>
          <input type="password" id="ct-pwd" class="form-input" value="Password123!" required>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%; margin-top:8px;">
          Create Teacher Account
        </button>
      </form>
    `;
  },

  async submitCreateTeacher(event) {
    event.preventDefault();
    const name = document.getElementById('ct-name').value.trim();
    const email = document.getElementById('ct-email').value.trim();
    const dept = document.getElementById('ct-dept').value.trim();
    const password = document.getElementById('ct-pwd').value;

    try {
      await API.createTeacher({
        name,
        email,
        department: dept,
        password
      });
      App.closeModal('admin-action-modal');
      alert("Teacher created successfully!");
      AdminController.loadTeachers();
    } catch (err) {
      alert(`Error creating teacher: ${err.message}`);
    }
  },

  async openAssignTeacherModal(teacherId, teacherName) {
    App.showModal('admin-action-modal');
    const modalContent = document.getElementById('admin-action-content');

    try {
      const [classesData, currData] = await Promise.all([
        API.getClasses(),
        API.getCurriculum()
      ]);

      let classOpts = classesData.classes.map(c => `<option value="${c.class_id}">${c.class_name} (Sec ${c.section})</option>`).join('');
      let subOpts = currData.subjects.map(s => `<option value="${s.subject_id}">${s.subject_name}</option>`).join('');

      modalContent.innerHTML = `
        <h3 style="font-size:16px; font-weight:800; border-bottom:1px solid var(--border-color); padding-bottom:8px;">
          Assign Class & Subject
        </h3>
        <p style="font-size:12px; color:var(--text-muted); margin: 6px 0;">Teacher: <strong>${teacherName}</strong></p>

        <form onsubmit="AdminController.submitAssignTeacher(event, '${teacherId}')">
          <div class="form-group">
            <label class="form-label">Select Class</label>
            <select id="at-class" class="form-select" required>
              ${classOpts}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Select Subject</label>
            <select id="at-subject" class="form-select" required>
              ${subOpts}
            </select>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%; margin-top:8px;">
            Confirm Assignment
          </button>
        </form>
      `;
    } catch (err) {
      modalContent.innerHTML = `<p style="color:red">Failed to load assignment data: ${err.message}</p>`;
    }
  },

  async submitAssignTeacher(event, teacherId) {
    event.preventDefault();
    const classId = document.getElementById('at-class').value;
    const subjectId = document.getElementById('at-subject').value;

    try {
      await API.assignTeacherToClass({
        teacher_id: teacherId,
        class_id: classId,
        subject_id: subjectId
      });
      App.closeModal('admin-action-modal');
      alert("Teacher successfully assigned to class and subject!");
      AdminController.loadTeachers();
    } catch (err) {
      alert(`Error assigning teacher: ${err.message}`);
    }
  },

  async toggleStudent(studentId) {
    try {
      await API.toggleStudentStatus(studentId);
      AdminController.loadStudents();
    } catch (err) {
      alert(err.message);
    }
  },

  async toggleTeacher(teacherId) {
    try {
      await API.toggleTeacherStatus(teacherId);
      AdminController.loadTeachers();
    } catch (err) {
      alert(err.message);
    }
  },

  // SAFE PERMANENT DELETION MODAL (Section 14)
  confirmDeleteUser(role, id, name) {
    App.showModal('admin-action-modal');
    const modalContent = document.getElementById('admin-action-content');

    modalContent.innerHTML = `
      <div style="text-align:center; padding: 10px 0;">
        <div style="width:50px; height:50px; border-radius:50%; background:#FEE2E2; color:#B91C1C; display:flex; align-items:center; justify-content:center; margin:0 auto 12px auto;">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <h3 style="font-size:16px; font-weight:800; color:var(--text-main);">Permanently delete this ${role} and associated data?</h3>
        <p style="font-size:12px; color:var(--text-muted); margin: 8px 0;">
          Target: <strong>${name}</strong> (${id})
        </p>
        <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px; font-size:11px; color:#991B1B; text-align:left; margin:12px 0;">
          Warning: This action is permanent and cannot be undone. All attempts, signals, and credentials will be permanently erased.
        </div>

        <div style="display:flex; gap:8px; margin-top:16px;">
          <button class="btn btn-secondary" style="flex:1;" onclick="App.closeModal('admin-action-modal')">
            Cancel
          </button>
          <button class="btn btn-danger" style="flex:1;" onclick="AdminController.executePermanentDeletion('${role}', '${id}')">
            Delete Permanently
          </button>
        </div>
      </div>
    `;
  },

  async executePermanentDeletion(role, id) {
    try {
      if (role === 'student') {
        await API.deleteStudentPermanently(id);
        App.closeModal('admin-action-modal');
        AdminController.loadStudents();
      } else {
        await API.deleteTeacherPermanently(id);
        App.closeModal('admin-action-modal');
        AdminController.loadTeachers();
      }
      alert(`Record permanently deleted.`);
    } catch (err) {
      alert(`Deletion failed: ${err.message}`);
    }
  }
};
