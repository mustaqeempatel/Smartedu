// SmartEdu Student Controller
const StudentController = {
  currentQuizState: {
    quizId: null,
    quizTitle: null,
    questions: [],
    currentIndex: 0,
    attemptId: null,
    questionStartTime: 0,
    selectedOption: null,
    selectedConfidence: null,
    timerInterval: null,
    remainingSeconds: 0
  },

  async loadDashboard() {
    const container = document.getElementById('student-view-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading your learning dashboard...</p></div>`;
    
    try {
      const data = await API.getStudentDashboard();
      this.renderDashboard(container, data);
    } catch (err) {
      container.innerHTML = `<div class="card" style="border-color: #FECACA; background: #FEF2F2; color: #991B1B;"><p>Error loading dashboard: ${err.message}</p></div>`;
    }
  },

  renderDashboard(container, data) {
    const { student, class_info, stats, quizzes, active_interventions, recent_attempts } = data;
    
    let html = `
      <!-- Greeting & Class Badge -->
      <div class="card" style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: #fff; border: none;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h2 style="font-size:18px; font-weight:800;">Hello, ${student.name}!</h2>
            <p style="font-size:12px; opacity:0.9; margin-top:2px;">
              ${class_info ? `${class_info.class_name} - Sec ${class_info.section} (${class_info.academic_year})` : 'Enrolled Student'}
            </p>
          </div>
          <span style="background:rgba(255,255,255,0.2); font-size:11px; padding:3px 8px; border-radius:12px; font-weight:600;">
            ${student.admission_number || 'STU'}
          </span>
        </div>
        <div style="margin-top:12px; font-size:12px; opacity:0.95; line-height:1.4;">
          Your academic practice helps detect concepts where personalized review and targeted guidance will boost your mastery.
        </div>
      </div>

      <!-- Overall Performance Stats Grid -->
      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-value">${stats.average_score}%</span>
          <span class="stat-label">Average Score</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.total_quizzes}</span>
          <span class="stat-label">Quizzes Completed</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.questions_answered}</span>
          <span class="stat-label">Questions Solved</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">${stats.accuracy_percent}%</span>
          <span class="stat-label">Accuracy Rate</span>
        </div>
      </div>
    `;

    // Active Interventions Alert Banner if any
    if (active_interventions && active_interventions.length > 0) {
      html += `
        <div class="card" style="border-left: 4px solid var(--accent); background: #F5F3FF;">
          <div class="card-header">
            <span class="card-title" style="color: var(--accent); font-size: 14px;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Teacher Academic Intervention Assigned
            </span>
            <span class="badge" style="background:#EDE9FE; color:#6D28D9;">Action Required</span>
          </div>
          <div style="font-size:12px; color:#4C1D95; margin-top:4px;">
            Your teacher has prepared targeted review support for <strong>${active_interventions[0].topic_name}</strong>.
          </div>
          <p style="font-size:12px; color:#5B21B6; font-style:italic; background:#fff; padding:8px 10px; border-radius:6px; border:1px solid #DDD6FE;">
            "${active_interventions[0].teacher_note || 'Please review the concepts and take the 3-question check.'}"
          </p>
          <button class="btn btn-accent btn-sm" style="margin-top:4px;" onclick="StudentController.openInterventionAssessment('${active_interventions[0].intervention_id}')">
            Start 3-Question Concept Check
          </button>
        </div>
      `;
    }

    // Assigned Quizzes Card
    html += `
      <div class="card">
        <div class="card-header">
          <span class="card-title">Assigned Quizzes</span>
          <button class="btn btn-secondary btn-sm" onclick="StudentController.loadQuizzesList()">View All</button>
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
    `;

    if (!quizzes || quizzes.length === 0) {
      html += `<p style="font-size:12px; color:var(--text-muted)">No active quizzes assigned right now.</p>`;
    } else {
      quizzes.slice(0, 3).forEach(q => {
        html += `
          <div style="border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; background: var(--bg-surface); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:13px; font-weight:700; color:var(--text-main);">${q.title}</div>
              <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">
                ${q.subject_name} • ${q.difficulty} • ${q.time_limit} mins
              </div>
              ${q.best_score !== null ? `<div style="font-size:11px; color:var(--status-success-text); font-weight:600; margin-top:3px;">Best Score: ${q.best_score}%</div>` : ''}
            </div>
            <button class="btn btn-primary btn-sm" onclick="StudentController.startQuizRunner('${q.quiz_id}')">
              ${q.attempts_count > 0 ? 'Retake' : 'Start'}
            </button>
          </div>
        `;
      });
    }

    html += `
        </div>
      </div>
    `;

    // Recent Attempts
    if (recent_attempts && recent_attempts.length > 0) {
      html += `
        <div class="card">
          <div class="card-header">
            <span class="card-title">Recent Quiz Activity</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px;">
      `;
      recent_attempts.forEach(a => {
        html += `
          <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; padding:8px 0; border-bottom:1px solid var(--border-color);">
            <div>
              <div style="font-weight:600; color:var(--text-main);">${a.title}</div>
              <div style="font-size:11px; color:var(--text-muted);">${a.subject_name}</div>
            </div>
            <span class="badge ${a.score >= 70 ? 'badge-improved' : 'badge-review'}" style="font-size:12px; font-weight:700;">
              ${a.score}%
            </span>
          </div>
        `;
      });
      html += `
          </div>
        </div>
      `;
    }

    container.innerHTML = html;
  },

  async loadQuizzesList() {
    App.switchStudentTab('student-quizzes');
    const container = document.getElementById('student-quizzes-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading available quizzes...</p></div>`;
    
    try {
      const data = await API.getStudentQuizzes();
      let html = `
        <div class="card-header" style="margin-bottom:8px;">
          <h3 style="font-size:16px; font-weight:700;">All Assigned Quizzes</h3>
        </div>
        <div style="display:flex; flex-direction:column; gap:12px;">
      `;
      
      data.quizzes.forEach(q => {
        html += `
          <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
                <span class="badge badge-topic" style="margin-bottom:6px;">${q.subject_name}</span>
                <h4 style="font-size:14px; font-weight:700; color:var(--text-main);">${q.title}</h4>
                <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">${q.description || ''}</p>
              </div>
              <span class="badge" style="background:#F1F5F9; color:#475569;">${q.difficulty}</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:10px; margin-top:4px;">
              <span style="font-size:11px; color:var(--text-muted);">
                ⏱ ${q.time_limit} mins • ${q.question_count} questions
              </span>
              <button class="btn btn-primary btn-sm" onclick="StudentController.startQuizRunner('${q.quiz_id}')">
                ${q.attempts_count > 0 ? 'Retake Quiz' : 'Start Quiz'}
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

  // Interactive Quiz Runner Flow
  async startQuizRunner(quizId) {
    App.showView('student-quiz-runner-view');
    const runnerContainer = document.getElementById('quiz-runner-container');
    runnerContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><p>Preparing questions...</p></div>`;
    
    try {
      const [quizData, startData] = await Promise.all([
        API.getQuizDetails(quizId),
        API.startQuiz(quizId)
      ]);
      
      this.currentQuizState = {
        quizId: quizId,
        quizTitle: quizData.quiz.title,
        questions: quizData.questions,
        currentIndex: 0,
        attemptId: startData.attempt_id,
        questionStartTime: Date.now(),
        selectedOption: null,
        selectedConfidence: null,
        remainingSeconds: (quizData.quiz.time_limit || 15) * 60,
        timerInterval: null
      };
      
      // Start Countdown Timer
      if (this.currentQuizState.timerInterval) clearInterval(this.currentQuizState.timerInterval);
      this.currentQuizState.timerInterval = setInterval(() => {
        this.currentQuizState.remainingSeconds--;
        const timerEl = document.getElementById('quiz-live-timer');
        if (timerEl) {
          const mins = Math.floor(this.currentQuizState.remainingSeconds / 60);
          const secs = this.currentQuizState.remainingSeconds % 60;
          timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        if (this.currentQuizState.remainingSeconds <= 0) {
          clearInterval(this.currentQuizState.timerInterval);
          this.submitQuizFinish();
        }
      }, 1000);
      
      this.renderCurrentQuestion();
    } catch (err) {
      runnerContainer.innerHTML = `<div class="card"><p style="color:red">Failed to start quiz: ${err.message}</p><button class="btn btn-secondary btn-sm" onclick="App.switchStudentTab('student-dashboard')">Return to Dashboard</button></div>`;
    }
  },

  renderCurrentQuestion() {
    const state = this.currentQuizState;
    const q = state.questions[state.currentIndex];
    const total = state.questions.length;
    const runnerContainer = document.getElementById('quiz-runner-container');
    
    state.questionStartTime = Date.now();
    state.selectedOption = null;
    state.selectedConfidence = null;
    
    const progressPercent = Math.round(((state.currentIndex) / total) * 100);
    const mins = Math.floor(state.remainingSeconds / 60);
    const secs = state.remainingSeconds % 60;
    
    runnerContainer.innerHTML = `
      <!-- Quiz Top Bar with Timer & Progress -->
      <div class="quiz-header-bar">
        <div>
          <span style="font-size:11px; font-weight:700; color:var(--text-muted);">QUESTION ${state.currentIndex + 1} OF ${total}</span>
        </div>
        <div class="timer-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span id="quiz-live-timer">${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}</span>
        </div>
      </div>
      <div class="quiz-progress-bar">
        <div class="quiz-progress-fill" style="width: ${progressPercent}%;"></div>
      </div>

      <div class="screen-padding">
        <!-- Question Card -->
        <div class="question-card">
          <div class="question-meta">
            <span class="badge badge-topic">${q.difficulty || 'Medium'}</span>
          </div>
          <div class="question-text">${q.question_text}</div>

          <!-- Multiple Choice Options -->
          <div class="options-list">
            <div class="option-item" id="opt-A" onclick="StudentController.selectOption('A')">
              <div class="option-letter">A</div>
              <div>${q.option_a}</div>
            </div>
            <div class="option-item" id="opt-B" onclick="StudentController.selectOption('B')">
              <div class="option-letter">B</div>
              <div>${q.option_b}</div>
            </div>
            <div class="option-item" id="opt-C" onclick="StudentController.selectOption('C')">
              <div class="option-letter">C</div>
              <div>${q.option_c}</div>
            </div>
            <div class="option-item" id="opt-D" onclick="StudentController.selectOption('D')">
              <div class="option-letter">D</div>
              <div>${q.option_d}</div>
            </div>
          </div>

          <!-- MANDATORY CONFIDENCE SELECTOR -->
          <div class="confidence-section">
            <div class="confidence-header">
              <span class="confidence-title">How confident are you in this answer?</span>
              <span style="font-size:10px; color:var(--text-muted)">Required</span>
            </div>
            <div class="confidence-grid">
              <button type="button" class="conf-btn" id="conf-NotSure" onclick="StudentController.selectConfidence('Not Sure')">
                Not Sure
              </button>
              <button type="button" class="conf-btn" id="conf-SomewhatSure" onclick="StudentController.selectConfidence('Somewhat Sure')">
                Somewhat Sure
              </button>
              <button type="button" class="conf-btn" id="conf-Confident" onclick="StudentController.selectConfidence('Confident')">
                Confident
              </button>
              <button type="button" class="conf-btn" id="conf-VeryConfident" onclick="StudentController.selectConfidence('Very Confident')">
                Very Confident
              </button>
            </div>
          </div>

          <!-- Feedback Box after answer submission -->
          <div id="question-feedback-box" style="display:none; padding:12px; border-radius:8px; font-size:12px;"></div>

          <!-- Submit / Next Button -->
          <button id="submit-answer-btn" class="btn btn-primary" style="margin-top:8px; opacity:0.5; pointer-events:none;" onclick="StudentController.submitAnswer()">
            Submit & Next
          </button>
        </div>
      </div>
    `;
  },

  selectOption(opt) {
    this.currentQuizState.selectedOption = opt;
    ['A', 'B', 'C', 'D'].forEach(letter => {
      const el = document.getElementById(`opt-${letter}`);
      if (el) el.classList.toggle('selected', letter === opt);
    });
    this.updateSubmitButtonState();
  },

  selectConfidence(level) {
    this.currentQuizState.selectedConfidence = level;
    const levels = ['Not Sure', 'Somewhat Sure', 'Confident', 'Very Confident'];
    levels.forEach(lvl => {
      const id = 'conf-' + lvl.replace(/\s+/g, '');
      const el = document.getElementById(id);
      if (el) el.classList.toggle('active', lvl === level);
    });
    this.updateSubmitButtonState();
  },

  updateSubmitButtonState() {
    const btn = document.getElementById('submit-answer-btn');
    if (!btn) return;
    const ready = this.currentQuizState.selectedOption && this.currentQuizState.selectedConfidence;
    btn.style.opacity = ready ? '1' : '0.5';
    btn.style.pointerEvents = ready ? 'auto' : 'none';
  },

  async submitAnswer() {
    const state = this.currentQuizState;
    const q = state.questions[state.currentIndex];
    const elapsedSeconds = Math.max(1.0, Math.round((Date.now() - state.questionStartTime) / 1000));
    
    const submitBtn = document.getElementById('submit-answer-btn');
    submitBtn.textContent = 'Saving...';
    submitBtn.style.pointerEvents = 'none';
    
    try {
      const res = await API.answerQuestion(state.quizId, {
        attempt_id: state.attemptId,
        question_id: q.question_id,
        selected_option: state.selectedOption,
        response_time: elapsedSeconds,
        confidence_level: state.selectedConfidence
      });
      
      // Move to next question or finish quiz
      state.currentIndex++;
      if (state.currentIndex < state.questions.length) {
        this.renderCurrentQuestion();
      } else {
        await this.submitQuizFinish();
      }
    } catch (err) {
      alert(`Error submitting question: ${err.message}`);
      submitBtn.textContent = 'Submit & Next';
      submitBtn.style.pointerEvents = 'auto';
    }
  },

  async submitQuizFinish() {
    const state = this.currentQuizState;
    if (state.timerInterval) clearInterval(state.timerInterval);
    
    const runnerContainer = document.getElementById('quiz-runner-container');
    runnerContainer.innerHTML = `<div style="text-align:center; padding: 50px;"><p>Analyzing responses and updating learning signals...</p></div>`;
    
    try {
      const data = await API.finishQuiz(state.quizId, state.attemptId);
      
      runnerContainer.innerHTML = `
        <div class="screen-padding" style="margin-top:20px;">
          <div class="card" style="text-align:center; padding:24px;">
            <div style="width:64px; height:64px; border-radius:50%; background:#DCFCE7; color:#15803D; display:flex; align-items:center; justify-content:center; margin:0 auto 12px auto;">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <h2 style="font-size:20px; font-weight:800; color:var(--text-main);">Quiz Completed!</h2>
            <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">${state.quizTitle}</p>
            
            <div style="margin:20px 0; background:var(--bg-subtle); padding:16px; border-radius:12px; border:1px solid var(--border-color);">
              <div style="font-size:36px; font-weight:900; color:var(--primary);">${data.score}%</div>
              <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">
                ${data.correct_count} of ${data.total_questions} questions correct
              </div>
            </div>

            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:12px; font-size:12px; color:#166534; text-align:left; line-height:1.4;">
              <strong>Learning Pattern Recorded:</strong> Your confidence selections and response patterns have been securely analyzed. The system identifies concepts where support may be helpful.
            </div>

            <button class="btn btn-primary" style="width:100%; margin-top:20px;" onclick="App.switchStudentTab('student-dashboard')">
              Return to Dashboard
            </button>
          </div>
        </div>
      `;
    } catch (err) {
      runnerContainer.innerHTML = `<div class="card"><p style="color:red">Failed to finalize quiz: ${err.message}</p></div>`;
    }
  },

  // Interventions Screen
  async loadInterventions() {
    App.switchStudentTab('student-interventions');
    const container = document.getElementById('student-interventions-content');
    container.innerHTML = `<div style="text-align:center; padding: 40px;"><p style="color:var(--text-muted)">Loading your support interventions...</p></div>`;
    
    try {
      const data = await API.getStudentInterventions();
      let html = `
        <div class="card-header" style="margin-bottom:8px;">
          <div>
            <h3 style="font-size:16px; font-weight:700;">Academic Interventions</h3>
            <p style="font-size:12px; color:var(--text-muted)">Targeted practice assigned by your teachers based on detected support signals</p>
          </div>
        </div>
        <div style="display:flex; flex-direction:column; gap:12px;">
      `;
      
      if (!data.interventions || data.interventions.length === 0) {
        html += `<div class="card"><p style="font-size:13px; color:var(--text-muted); text-align:center;">No interventions assigned at this time.</p></div>`;
      } else {
        data.interventions.forEach(i => {
          const isDone = i.status === 'COMPLETED';
          html += `
            <div class="card" style="border-left: 4px solid ${isDone ? 'var(--status-success-border)' : 'var(--accent)'};">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <span class="badge badge-topic">${i.subject_name} • ${i.topic_name}</span>
                  <h4 style="font-size:14px; font-weight:700; color:var(--text-main); margin-top:4px;">${i.intervention_type}</h4>
                  <div style="font-size:11px; color:var(--text-muted);">Assigned by ${i.teacher_name}</div>
                </div>
                <span class="badge ${isDone ? 'badge-improved' : 'badge-review'}">
                  ${isDone ? 'Completed' : 'Pending'}
                </span>
              </div>
              
              <div style="background:var(--bg-subtle); border-radius:8px; padding:10px; font-size:12px; color:var(--text-main); font-style:italic; border:1px solid var(--border-color);">
                "${i.teacher_note || 'Complete the targeted concept check to strengthen understanding.'}"
              </div>

              ${isDone ? `
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:10px; text-align:center;">
                  <div>
                    <div style="font-size:10px; color:#166534; font-weight:600;">BEFORE</div>
                    <div style="font-size:14px; font-weight:800; color:#14532D;">${i.before_score}%</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:#166534; font-weight:600;">AFTER</div>
                    <div style="font-size:14px; font-weight:800; color:#14532D;">${i.after_score}%</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:#166534; font-weight:600;">DELTA</div>
                    <div style="font-size:14px; font-weight:800; color:#15803D;">+${i.improvement}%</div>
                  </div>
                </div>
              ` : `
                <button class="btn btn-accent btn-sm" onclick="StudentController.openInterventionAssessment('${i.intervention_id}')">
                  Start Concept Check Assessment
                </button>
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
  },

  async openInterventionAssessment(interventionId) {
    App.showModal('intervention-check-modal');
    const modalContent = document.getElementById('intervention-check-content');
    modalContent.innerHTML = `<div style="text-align:center; padding: 30px;"><p>Loading concept check...</p></div>`;
    
    try {
      const data = await API.getInterventionAssessment(interventionId);
      const { intervention, questions } = data;
      
      let html = `
        <div>
          <span class="badge badge-topic">${intervention.subject_name} • ${intervention.topic_name}</span>
          <h3 style="font-size:16px; font-weight:800; margin-top:6px;">Follow-up Concept Check</h3>
          <p style="font-size:12px; color:var(--text-muted); margin-top:2px;">
            Targeted 3-question evaluation to measure academic improvement.
          </p>
        </div>

        <form id="follow-up-form" onsubmit="StudentController.submitFollowUpAssessment(event, '${interventionId}')">
          <div style="display:flex; flex-direction:column; gap:16px; margin: 16px 0;">
      `;

      questions.forEach((q, idx) => {
        html += `
          <div style="border:1px solid var(--border-color); border-radius:10px; padding:12px; background:var(--bg-subtle);">
            <div style="font-size:13px; font-weight:700; margin-bottom:8px;">Q${idx + 1}. ${q.question_text}</div>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <label style="display:flex; align-items:center; gap:8px; font-size:12px; cursor:pointer;">
                <input type="radio" name="q_${q.question_id}" value="A" required> ${q.option_a}
              </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:12px; cursor:pointer;">
                <input type="radio" name="q_${q.question_id}" value="B"> ${q.option_b}
              </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:12px; cursor:pointer;">
                <input type="radio" name="q_${q.question_id}" value="C"> ${q.option_c}
              </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:12px; cursor:pointer;">
                <input type="radio" name="q_${q.question_id}" value="D"> ${q.option_d}
              </label>
            </div>
          </div>
        `;
      });

      html += `
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;">
            Submit Concept Check
          </button>
        </form>
      `;

      modalContent.innerHTML = html;
    } catch (err) {
      modalContent.innerHTML = `<div class="card"><p style="color:red">Error: ${err.message}</p></div>`;
    }
  },

  async submitFollowUpAssessment(event, interventionId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const answers = [];
    
    for (let [key, val] of formData.entries()) {
      if (key.startsWith('q_')) {
        answers.push({
          question_id: key.replace('q_', ''),
          selected_option: val
        });
      }
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Evaluating results...';
    submitBtn.disabled = true;
    
    try {
      const res = await API.submitInterventionAssessment(interventionId, answers);
      const modalContent = document.getElementById('intervention-check-content');
      
      modalContent.innerHTML = `
        <div style="text-align:center; padding: 20px 0;">
          <div style="width:56px; height:56px; border-radius:50%; background:#DCFCE7; color:#15803D; display:flex; align-items:center; justify-content:center; margin:0 auto 12px auto;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <h3 style="font-size:18px; font-weight:800; color:var(--text-main);">Assessment Completed!</h3>
          <p style="font-size:12px; color:var(--text-muted); margin-top:2px;">Measured Improvement</p>
          
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:16px; margin:20px 0; text-align:center;">
            <div>
              <div style="font-size:11px; color:#166534; font-weight:600;">BEFORE</div>
              <div style="font-size:18px; font-weight:900; color:#14532D;">${res.before_score}%</div>
            </div>
            <div>
              <div style="font-size:11px; color:#166534; font-weight:600;">AFTER</div>
              <div style="font-size:18px; font-weight:900; color:#14532D;">${res.after_score}%</div>
            </div>
            <div>
              <div style="font-size:11px; color:#166534; font-weight:600;">DELTA</div>
              <div style="font-size:18px; font-weight:900; color:#15803D;">+${res.improvement}%</div>
            </div>
          </div>

          <div class="badge badge-improved" style="font-size:13px; padding:6px 14px; margin-bottom:20px;">
            Status: ${res.result_status}
          </div>

          <button class="btn btn-primary" style="width:100%;" onclick="App.closeModal('intervention-check-modal'); StudentController.loadInterventions();">
            Done
          </button>
        </div>
      `;
    } catch (err) {
      alert(`Error submitting follow-up: ${err.message}`);
      submitBtn.textContent = 'Submit Concept Check';
      submitBtn.disabled = false;
    }
  }
};
