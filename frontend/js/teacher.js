// SmartEdu Teacher Controller
const TeacherController = {
  currentCurriculum: { subjects: [], chapters: [], topics: [] },

  async initCurriculum() {
    if (this.currentCurriculum.subjects.length === 0) {
      try {
        this.currentCurriculum = await API.getCurriculum();
      } catch (e) {
        console.error("Failed to preload curriculum:", e);
      }
    }
  },

  async loadDashboard() {
    await this.initCurriculum();
    const container = document.getElementById('teacher-view-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading teacher dashboard...</p></div>`;
    
    try {
      const data = await API.getTeacherDashboard();
      this.renderDashboard(container, data);
    } catch (err) {
      container.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  renderDashboard(container, data) {
    const { teacher, stats, recent_signals } = data;
    
    let html = `
      <!-- Teacher Header -->
      <div class="card" style="background: linear-gradient(135deg, #4338CA 0%, #6366F1 100%); color: #fff; border: none;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h2 style="font-size:18px; font-weight:800;">Welcome, ${teacher.name}</h2>
            <p style="font-size:12px; opacity:0.9; margin-top:2px;">
              Department of ${teacher.department || 'Science'} • ${teacher.employee_number || 'TCH'}
            </p>
          </div>
          <span class="badge" style="background:rgba(255,255,255,0.25); color:#fff;">Teacher Portal</span>
        </div>
        <div style="margin-top:12px; font-size:12px; opacity:0.95;">
          Monitor student learning patterns, inspect explainable support signals, and assign personalized academic interventions.
        </div>
      </div>

      <!-- Dashboard Metrics -->
      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-value">${stats.assigned_students}</span>
          <span class="stat-label">Assigned Students</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.active_classes}</span>
          <span class="stat-label">Active Classes</span>
        </div>
        <div class="stat-box">
          <span class="stat-value" style="color: #D97706;">${stats.support_signals}</span>
          <span class="stat-label">Possible Support Signals</span>
        </div>
        <div class="stat-box">
          <span class="stat-value" style="color: #4F46E5;">${stats.active_interventions}</span>
          <span class="stat-label">Active Interventions</span>
        </div>
      </div>

      <!-- Quick Action Buttons -->
      <div style="display:flex; gap:8px;">
        <button class="btn btn-primary btn-sm" style="flex:1;" onclick="TeacherController.loadQuizBuilder()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Create Quiz
        </button>
        <button class="btn btn-secondary btn-sm" style="flex:1;" onclick="TeacherController.loadSupportSignals()">
          Review Signals (${stats.support_signals})
        </button>
      </div>

      <!-- Possible Learning Support Signals List -->
      <div class="card">
        <div class="card-header">
          <div>
            <span class="card-title" style="color:#B45309;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              Possible Academic Support Signals
            </span>
            <div class="card-subtitle">Hidden pattern detected: review evidence below</div>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="TeacherController.loadSupportSignals()">View All</button>
        </div>

        <div style="display:flex; flex-direction:column; gap:10px;">
    `;

    if (!recent_signals || recent_signals.length === 0) {
      html += `<p style="font-size:12px; color:var(--text-muted); padding:10px 0;">No active support signals detected for your classes. All student behavior is within normal parameters.</p>`;
    } else {
      recent_signals.forEach(s => {
        html += `
          <div style="border: 1.5px solid #FDE68A; background: #FFFBEB; border-radius: 10px; padding: 12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:13px; font-weight:700; color:#92400E;">${s.student_name}</div>
              <div style="font-size:11px; color:#78350F; margin-top:2px;">
                ${s.class_name} • ${s.subject_name} • <strong>${s.topic_name}</strong>
              </div>
              <div style="display:flex; gap:6px; margin-top:4px;">
                <span class="badge badge-review" style="font-size:10px;">Support Score: ${s.support_score}</span>
                <span class="badge" style="background:#FEF3C7; color:#92400E; font-size:10px;">Review Recommended</span>
              </div>
            </div>
            <button class="btn btn-sm" style="background:#F59E0B; color:#fff;" onclick="TeacherController.openEvidenceScreen('${s.signal_id}')">
              Inspect Evidence
            </button>
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

  async loadSupportSignals() {
    App.switchTeacherTab('teacher-signals');
    const container = document.getElementById('teacher-signals-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading learning support signals...</p></div>`;
    
    try {
      const data = await API.getSupportSignals();
      let html = `
        <div class="card-header" style="margin-bottom:8px;">
          <div>
            <h3 style="font-size:16px; font-weight:700;">Academic Support Detection</h3>
            <p style="font-size:12px; color:var(--text-muted)">Identified academic patterns where intervention may be appropriate</p>
          </div>
        </div>
        <div style="display:flex; flex-direction:column; gap:12px;">
      `;
      
      if (!data.signals || data.signals.length === 0) {
        html += `<div class="card"><p style="font-size:13px; color:var(--text-muted); text-align:center;">No active signals found.</p></div>`;
      } else {
        data.signals.forEach(s => {
          html += `
            <div class="card" style="border-left: 4px solid #F59E0B;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <h4 style="font-size:15px; font-weight:800; color:var(--text-main);">${s.student_name}</h4>
                  <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">
                    ${s.class_name} • Admission: ${s.admission_number}
                  </div>
                  <div style="margin-top:6px;">
                    <span class="badge badge-topic">${s.subject_name} • ${s.topic_name}</span>
                  </div>
                </div>
                <div style="text-align:right;">
                  <span class="badge badge-review" style="font-size:11px; font-weight:800;">
                    Score: ${s.support_score}
                  </span>
                  <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">${s.status}</div>
                </div>
              </div>

              <!-- Metrics Mini Bar -->
              <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; background:var(--bg-subtle); padding:8px; border-radius:8px; text-align:center; margin-top:4px;">
                <div>
                  <div style="font-size:10px; color:var(--text-muted);">ERRORS</div>
                  <div style="font-size:13px; font-weight:700; color:#B91C1C;">${s.error_frequency}</div>
                </div>
                <div>
                  <div style="font-size:10px; color:var(--text-muted);">ATTEMPTS</div>
                  <div style="font-size:13px; font-weight:700;">${s.repeated_attempts}</div>
                </div>
                <div>
                  <div style="font-size:10px; color:var(--text-muted);">RESP TIME</div>
                  <div style="font-size:13px; font-weight:700;">${Math.round(s.average_response_time)}s</div>
                </div>
                <div>
                  <div style="font-size:10px; color:var(--text-muted);">MISMATCH</div>
                  <div style="font-size:13px; font-weight:700; color:#D97706;">${s.confidence_mismatch}</div>
                </div>
              </div>

              <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:4px;">
                <button class="btn btn-secondary btn-sm" onclick="TeacherController.openEvidenceScreen('${s.signal_id}')">
                  Inspect Evidence
                </button>
                <button class="btn btn-accent btn-sm" onclick="TeacherController.openInterventionModal('${s.student_id}', '${s.topic_id}', '${s.student_name}', '${s.topic_name}')">
                  + Create Intervention
                </button>
              </div>
            </div>
          `;
        });
      }
      
      html += `</div>`;
      container.innerHTML = html;
    } catch (err) {
      container.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  // EXPLAINABLE AI EVIDENCE SCREEN
  async openEvidenceScreen(signalId) {
    App.showModal('evidence-modal');
    const modalContent = document.getElementById('evidence-modal-content');
    modalContent.innerHTML = `<div style="text-align:center; padding: 40px;"><p>Loading explainable evidence...</p></div>`;
    
    try {
      const data = await API.getSignalEvidence(signalId);
      const ev = data.evidence;
      const pEv = ev.parsed_evidence || {};
      const factors = pEv.factors || {};
      const bullets = pEv.explanation_bullets || [];
      const recentAttempts = ev.recent_attempts || [];
      
      let html = `
        <div>
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <span class="badge badge-topic">${ev.subject_name} • ${ev.topic_name}</span>
              <h3 style="font-size:18px; font-weight:800; color:var(--text-main); margin-top:6px;">${ev.student_name}</h3>
              <p style="font-size:12px; color:var(--text-muted);">${ev.class_name} • Admission #${ev.admission_number}</p>
            </div>
            <span class="signal-chip">
              Support Score: ${ev.support_score}
            </span>
          </div>
        </div>

        <!-- Ethical Disclaimer Notice -->
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:10px; font-size:11px; color:#1E40AF; line-height:1.4;">
          <strong>Objective Signal Detection:</strong> This signal communicates a <em>possible academic support need</em> based on response latency, repeated errors, and confidence mismatch. The system does not classify student capability or diagnose difficulties.
        </div>

        <!-- Transparent Algorithmic Factor Breakdown -->
        <div class="factor-metric-row">
          <div class="factor-metric-box">
            <span class="factor-value">${factors.error_count || ev.error_frequency || 0}</span>
            <span class="factor-label">Repeated Errors on Topic</span>
          </div>
          <div class="factor-metric-box">
            <span class="factor-value">${factors.confidence_mismatch_count || ev.confidence_mismatch || 0}</span>
            <span class="factor-label">Confidence Mismatches</span>
          </div>
          <div class="factor-metric-box">
            <span class="factor-value">${factors.avg_response_time_seconds || Math.round(ev.average_response_time)}s</span>
            <span class="factor-label">Avg Response Time (${factors.time_ratio ? `${factors.time_ratio}x baseline` : 'Above baseline'})</span>
          </div>
          <div class="factor-metric-box">
            <span class="factor-value">${factors.max_attempts || ev.repeated_attempts || 1}</span>
            <span class="factor-label">Max Attempts on Concept</span>
          </div>
        </div>

        <!-- Clear Plain-English Evidence Explanations -->
        <div class="evidence-card">
          <div style="font-size:13px; font-weight:700; color:#92400E;">
            Why did the system flag this student?
          </div>
          <div class="bullets-list">
      `;

      if (bullets.length === 0) {
        html += `<div class="bullet-item"><span class="bullet-icon">•</span><span>High response latency and repeated mistakes observed on this specific topic.</span></div>`;
      } else {
        bullets.forEach(b => {
          html += `
            <div class="bullet-item">
              <span class="bullet-icon">⚡</span>
              <span>${b}</span>
            </div>
          `;
        });
      }

      html += `
          </div>
        </div>

        <!-- Question Attempts History -->
        <div>
          <div style="font-size:13px; font-weight:700; margin-bottom:8px;">Recent Question Attempts on this Topic</div>
          <div style="display:flex; flex-direction:column; gap:8px;">
      `;

      recentAttempts.forEach(qa => {
        html += `
          <div style="background:var(--bg-subtle); border:1px solid var(--border-color); border-radius:8px; padding:10px; font-size:12px;">
            <div style="font-weight:600; color:var(--text-main); margin-bottom:4px;">${qa.question_text}</div>
            <div style="display:flex; justify-content:space-between; color:var(--text-muted); font-size:11px;">
              <span>Selected: <strong>${qa.selected_option}</strong> (Correct: ${qa.correct_option})</span>
              <span style="color:${qa.is_correct ? 'var(--status-success-text)' : '#B91C1C'}; font-weight:700;">
                ${qa.is_correct ? 'Correct' : 'Incorrect'}
              </span>
            </div>
            <div style="display:flex; justify-content:space-between; color:var(--text-muted); font-size:11px; margin-top:2px;">
              <span>Time: ${qa.response_time}s</span>
              <span>Confidence: <strong>${qa.confidence_level}</strong></span>
            </div>
          </div>
        `;
      });

      html += `
          </div>
        </div>

        <!-- Action Button to Create Intervention -->
        <div style="margin-top:8px;">
          <button class="btn btn-primary" style="width:100%;" onclick="App.closeModal('evidence-modal'); TeacherController.openInterventionModal('${ev.student_id}', '${ev.topic_id}', '${ev.student_name}', '${ev.topic_name}');">
            + Create Targeted Academic Intervention
          </button>
        </div>
      `;

      modalContent.innerHTML = html;
    } catch (err) {
      modalContent.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  // Intervention Creation Modal
  openInterventionModal(studentId, topicId, studentName, topicName) {
    App.showModal('intervention-create-modal');
    const modalContent = document.getElementById('intervention-create-content');
    
    modalContent.innerHTML = `
      <div>
        <span class="badge badge-topic">Targeted Support</span>
        <h3 style="font-size:16px; font-weight:800; margin-top:4px;">Assign Academic Intervention</h3>
        <p style="font-size:12px; color:var(--text-muted);">
          For <strong>${studentName}</strong> on topic <strong>${topicName}</strong>
        </p>
      </div>

      <form id="create-intervention-form" onsubmit="TeacherController.submitIntervention(event, '${studentId}', '${topicId}')">
        <div class="form-group">
          <label class="form-label">Intervention Type</label>
          <select id="int-type" class="form-select" required>
            <option value="3-question concept check" selected>3-question concept check (Recommended)</option>
            <option value="Concept explanation">Concept explanation</option>
            <option value="Short revision">Short revision</option>
            <option value="Practice worksheet">Practice worksheet</option>
            <option value="Additional quiz">Additional quiz</option>
            <option value="Teacher follow-up">Teacher follow-up</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Teacher Pedagogical Note & Instructions</label>
          <textarea id="int-note" class="form-textarea" rows="3" placeholder="e.g. Review Kirchhoff's loop rule sign convention before attempting advanced circuit questions..." required></textarea>
        </div>

        <button type="submit" class="btn btn-primary" style="width:100%; margin-top:8px;">
          Assign Intervention to Student
        </button>
      </form>
    `;
  },

  async submitIntervention(event, studentId, topicId) {
    event.preventDefault();
    const type = document.getElementById('int-type').value;
    const note = document.getElementById('int-note').value;
    
    try {
      await API.createIntervention({
        student_id: studentId,
        topic_id: topicId,
        intervention_type: type,
        teacher_note: note
      });
      App.closeModal('intervention-create-modal');
      alert("Academic intervention assigned successfully!");
      TeacherController.loadSupportSignals();
    } catch (err) {
      alert(`Error creating intervention: ${err.message}`);
    }
  },

  // Dedicated Quiz Builder Screen (Section 18)
  async loadQuizBuilder() {
    await this.initCurriculum();
    App.switchTeacherTab('teacher-quizzes');
    const container = document.getElementById('teacher-quizzes-content');
    
    let subjectsOpts = this.currentCurriculum.subjects.map(s => `<option value="${s.subject_id}">${s.subject_name}</option>`).join('');
    let topicsOpts = this.currentCurriculum.topics.map(t => `<option value="${t.topic_id}">${t.topic_name}</option>`).join('');

    container.innerHTML = `
      <div class="card-header" style="margin-bottom:8px;">
        <div>
          <h3 style="font-size:16px; font-weight:700;">Dedicated Quiz Builder</h3>
          <p style="font-size:12px; color:var(--text-muted)">Author quizzes and attach topics to track student learning behavior</p>
        </div>
      </div>

      <form id="quiz-builder-form" onsubmit="TeacherController.publishCreatedQuiz(event)">
        <!-- Quiz Meta Details -->
        <div class="card">
          <div class="form-group">
            <label class="form-label">Quiz Title</label>
            <input type="text" id="qb-title" class="form-input" placeholder="e.g. Electrodynamics Masterclass" required>
          </div>
          <div class="form-group">
            <label class="form-label">Subject</label>
            <select id="qb-subject" class="form-select" required>
              ${subjectsOpts}
            </select>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
            <div class="form-group">
              <label class="form-label">Difficulty</label>
              <select id="qb-difficulty" class="form-select">
                <option value="Easy">Easy</option>
                <option value="Medium" selected>Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Time Limit (mins)</label>
              <input type="number" id="qb-timelimit" class="form-input" value="15" min="1" max="180">
            </div>
          </div>
        </div>

        <!-- Questions Section -->
        <div style="margin-top:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="font-size:14px; font-weight:700;">Quiz Questions</h4>
            <button type="button" class="btn btn-secondary btn-sm" onclick="TeacherController.addQuestionField()">
              + Add Question
            </button>
          </div>
          <div id="qb-questions-list" style="display:flex; flex-direction:column; gap:12px;"></div>
        </div>

        <!-- Builder Buttons -->
        <div style="display:flex; gap:8px; margin-top:16px;">
          <button type="submit" class="btn btn-primary" style="flex:1;">
            Publish Quiz
          </button>
        </div>
      </form>
    `;

    // Add initial question field
    this.addQuestionField();
  },

  questionCount: 0,
  addQuestionField() {
    this.questionCount++;
    const idx = this.questionCount;
    const list = document.getElementById('qb-questions-list');
    if (!list) return;

    let topicsOpts = this.currentCurriculum.topics.map(t => `<option value="${t.topic_id}">${t.topic_name}</option>`).join('');

    const qCard = document.createElement('div');
    qCard.className = 'card';
    qCard.id = `qb-qcard-${idx}`;
    qCard.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:13px; font-weight:700;">Question #${idx}</span>
        ${idx > 1 ? `<button type="button" class="btn btn-danger btn-sm" style="padding:2px 8px;" onclick="document.getElementById('qb-qcard-${idx}').remove()">Remove</button>` : ''}
      </div>

      <div class="form-group">
        <label class="form-label">Topic / Concept</label>
        <select class="form-select q-topic" required>
          ${topicsOpts}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Question Text</label>
        <textarea class="form-textarea q-text" rows="2" placeholder="Enter question text..." required></textarea>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <div class="form-group">
          <label class="form-label">Option A</label>
          <input type="text" class="form-input q-opt-a" placeholder="Option A" required>
        </div>
        <div class="form-group">
          <label class="form-label">Option B</label>
          <input type="text" class="form-input q-opt-b" placeholder="Option B" required>
        </div>
        <div class="form-group">
          <label class="form-label">Option C</label>
          <input type="text" class="form-input q-opt-c" placeholder="Option C" required>
        </div>
        <div class="form-group">
          <label class="form-label">Option D</label>
          <input type="text" class="form-input q-opt-d" placeholder="Option D" required>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 2fr; gap:8px;">
        <div class="form-group">
          <label class="form-label">Correct Option</label>
          <select class="form-select q-correct" required>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="D">D</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Explanation</label>
          <input type="text" class="form-input q-expl" placeholder="Pedagogical explanation...">
        </div>
      </div>
    `;
    list.appendChild(qCard);
  },

  async publishCreatedQuiz(event) {
    event.preventDefault();
    const title = document.getElementById('qb-title').value.trim();
    const subjectId = document.getElementById('qb-subject').value;
    const difficulty = document.getElementById('qb-difficulty').value;
    const timeLimit = parseInt(document.getElementById('qb-timelimit').value) || 15;

    const cards = document.querySelectorAll('#qb-questions-list .card');
    const questions = [];

    cards.forEach(card => {
      questions.push({
        topic_id: card.querySelector('.q-topic').value,
        question_text: card.querySelector('.q-text').value.trim(),
        option_a: card.querySelector('.q-opt-a').value.trim(),
        option_b: card.querySelector('.q-opt-b').value.trim(),
        option_c: card.querySelector('.q-opt-c').value.trim(),
        option_d: card.querySelector('.q-opt-d').value.trim(),
        correct_option: card.querySelector('.q-correct').value,
        explanation: card.querySelector('.q-expl').value.trim(),
        difficulty: difficulty
      });
    });

    if (questions.length === 0) {
      alert("Please add at least one question!");
      return;
    }

    try {
      await API.createQuiz({
        title,
        subject_id: subjectId,
        difficulty,
        time_limit: timeLimit,
        status: 'published',
        questions
      });
      alert("Quiz created and published successfully!");
      TeacherController.loadDashboard();
    } catch (err) {
      alert(`Failed to create quiz: ${err.message}`);
    }
  },

  async loadInterventions() {
    App.switchTeacherTab('teacher-interventions');
    const container = document.getElementById('teacher-interventions-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading intervention outcomes...</p></div>`;

    try {
      const data = await API.getTeacherInterventions();
      let html = `
        <div class="card-header" style="margin-bottom:8px;">
          <div>
            <h3 style="font-size:16px; font-weight:700;">Intervention Outcomes & Progress</h3>
            <p style="font-size:12px; color:var(--text-muted)">Measured result cycle: Detect -> Intervene -> Measure Result</p>
          </div>
        </div>
        <div style="display:flex; flex-direction:column; gap:12px;">
      `;

      if (!data.interventions || data.interventions.length === 0) {
        html += `<div class="card"><p style="font-size:12px; color:var(--text-muted); text-align:center;">No interventions assigned yet.</p></div>`;
      } else {
        data.interventions.forEach(i => {
          const isDone = i.status === 'COMPLETED';
          html += `
            <div class="card" style="border-left: 4px solid ${isDone ? 'var(--status-success-border)' : 'var(--accent)'};">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <h4 style="font-size:15px; font-weight:800; color:var(--text-main);">${i.student_name}</h4>
                  <div style="font-size:11px; color:var(--text-muted);">${i.class_name} • ${i.subject_name} • ${i.topic_name}</div>
                </div>
                <span class="badge ${isDone ? 'badge-improved' : 'badge-review'}">
                  ${isDone ? (i.result_status || 'Improved') : 'Assigned'}
                </span>
              </div>

              <div style="background:var(--bg-subtle); border-radius:8px; padding:8px 10px; font-size:12px; color:var(--text-main); font-style:italic;">
                "${i.teacher_note || 'Review key concepts'}"
              </div>

              ${isDone ? `
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:6px; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:10px; text-align:center;">
                  <div>
                    <div style="font-size:10px; color:#166534; font-weight:600;">BEFORE</div>
                    <div style="font-size:14px; font-weight:800; color:#14532D;">${i.before_score}%</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:#166534; font-weight:600;">AFTER</div>
                    <div style="font-size:14px; font-weight:800; color:#14532D;">${i.after_score}%</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:#166534; font-weight:600;">IMPROVEMENT</div>
                    <div style="font-size:14px; font-weight:800; color:#15803D;">+${i.improvement}%</div>
                  </div>
                </div>
              ` : `
                <div style="font-size:11px; color:var(--text-muted); text-align:right;">
                  Awaiting student completion of follow-up assessment
                </div>
              `}
            </div>
          `;
        });
      }

      html += `</div>`;
      container.innerHTML = html;
    } catch (err) {
      container.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  }
};
