import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # Set 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank slide

    # Design System Colors
    COLOR_NAVY = RGBColor(15, 23, 42)       # #0F172A Dark Slate/Navy
    COLOR_PRIMARY = RGBColor(30, 58, 138)    # #1E3A8A Deep Blue
    COLOR_ACCENT = RGBColor(79, 70, 229)     # #4F46E5 Indigo
    COLOR_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    COLOR_CARD_BG = RGBColor(255, 255, 255)  # White
    COLOR_BORDER = RGBColor(226, 232, 240)   # #E2E8F0
    COLOR_TEXT = RGBColor(15, 23, 42)        # #0F172A
    COLOR_MUTED = RGBColor(100, 116, 139)    # #64748B
    COLOR_AMBER = RGBColor(217, 119, 6)      # #D97706
    COLOR_GREEN = RGBColor(21, 128, 61)      # #15803D
    COLOR_WHITE = RGBColor(255, 255, 255)

    def add_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, category, title, dark=False):
        # Category / Team tag
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"TEAM INFINITY X  •  {category.upper()}"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT if not dark else RGBColor(147, 197, 253)

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY if not dark else COLOR_WHITE

    def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: Title Slide (Dark Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1, COLOR_NAVY)

    # Gradient-like accent bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_ACCENT
    top_bar.line.fill.background()

    # Team Badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.2), Inches(3.2), Inches(0.5))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_PRIMARY
    badge.line.color.rgb = COLOR_ACCENT
    p_badge = badge.text_frame.paragraphs[0]
    p_badge.text = "⚡ HACKATHON PITCH DECK"
    p_badge.font.size = Pt(12)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_WHITE
    p_badge.alignment = PP_ALIGN.CENTER

    # Main Title
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.3), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "SmartEdu"
    p1.font.size = Pt(54)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "AI-Powered Hidden Academic Support Detection System"
    p1_sub.font.size = Pt(24)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = RGBColor(147, 197, 253)

    p1_desc = tf1.add_paragraph()
    p1_desc.text = "Detecting subtle academic distress before grades collapse through multi-signal response latency, repeated mistakes, and confidence mismatch tracking."
    p1_desc.font.size = Pt(15)
    p1_desc.font.color.rgb = RGBColor(203, 213, 225)

    # Footer Card on Title Slide
    team_card = add_card(s1, 1.0, 5.0, 11.3, 1.5, bg_color=RGBColor(30, 41, 59), border_color=COLOR_ACCENT)
    tf_tc = team_card.text_frame
    tf_tc.word_wrap = True
    p_tc1 = tf_tc.paragraphs[0]
    p_tc1.text = "TEAM: INFINITY X"
    p_tc1.font.size = Pt(16)
    p_tc1.font.bold = True
    p_tc1.font.color.rgb = RGBColor(250, 204, 21) # Yellow-gold

    p_tc2 = tf_tc.add_paragraph()
    p_tc2.text = "Core Principle: DETECT  →  EXPLAIN  →  INTERVENE  →  MEASURE"
    p_tc2.font.size = Pt(14)
    p_tc2.font.bold = True
    p_tc2.font.color.rgb = COLOR_WHITE

    p_tc3 = tf_tc.add_paragraph()
    p_tc3.text = "Mobile-First Application Architecture • Real Persistent Relational Engine • Zero-Deficit Explainable AI"
    p_tc3.font.size = Pt(12)
    p_tc3.font.color.rgb = RGBColor(148, 163, 184)

    # ==========================================
    # SLIDE 2: The Core Problem (The Illusion of the Passing Grade)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2, COLOR_LIGHT_BG)
    add_header(s2, "Problem Statement", "The Fallacy of the Passing Grade")

    # Left Column: The Trap
    card_l = add_card(s2, 0.8, 1.8, 5.6, 5.0)
    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    p_l1 = tf_l.paragraphs[0]
    p_l1.text = "The Traditional Blindspot ❌"
    p_l1.font.size = Pt(18)
    p_l1.font.bold = True
    p_l1.font.color.rgb = RGBColor(185, 28, 28)

    points_l = [
        "Traditional LMS & grading tools only measure aggregate scores (e.g. '82% - Passing Grade').",
        "Students attend class, submit homework, and appear academically fine on the surface.",
        "Behind the scenes, the student might have critical conceptual gaps, repeated failures on prerequisite topics, or high hesitation.",
        "By the time exams arrive, these hidden cracks widen into catastrophic failure."
    ]
    for pt in points_l:
        p = tf_l.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT

    # Right Column: The Real Example
    card_r = add_card(s2, 6.9, 1.8, 5.6, 5.0, bg_color=RGBColor(254, 242, 242), border_color=RGBColor(254, 202, 202))
    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    p_r1 = tf_r.paragraphs[0]
    p_r1.text = "The SmartEdu Discovery: Alex Morgan 🔍"
    p_r1.font.size = Pt(18)
    p_r1.font.bold = True
    p_r1.font.color.rgb = COLOR_PRIMARY

    p_score = tf_r.add_paragraph()
    p_score.text = "Overall Quiz Score: 82% (Looks completely safe!)"
    p_score.font.size = Pt(14)
    p_score.font.bold = True
    p_score.font.color.rgb = COLOR_GREEN

    points_r = [
        "5 repeated errors on 'Kirchhoff's Laws' concept questions.",
        "3 repeated attempts on the same questions without score improvement.",
        "Response time: 48 seconds (2.2x higher than Alex's 22s baseline).",
        "4 Confidence Mismatches: Alex marked 'Very Confident' on wrong answers (severe conceptual misconception!)."
    ]
    for pt in points_r:
        p = tf_r.add_paragraph()
        p.text = "⚡ " + pt
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT

    p_conc = tf_r.add_paragraph()
    p_conc.text = "Result: SmartEdu flags a 'Possible Support Signal' BEFORE Alex falls behind."
    p_conc.font.size = Pt(13)
    p_conc.font.bold = True
    p_conc.font.color.rgb = COLOR_AMBER

    # ==========================================
    # SLIDE 3: Non-Deficit Pedagogical Philosophy
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3, COLOR_LIGHT_BG)
    add_header(s3, "Ethics & AI Governance", "Non-Deficit, Constructive AI Philosophy")

    # 3 Horizontal Pillars
    c1 = add_card(s3, 0.8, 1.8, 3.6, 4.8, bg_color=RGBColor(254, 242, 242), border_color=RGBColor(254, 202, 202))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "WHAT WE NEVER DO ⛔"
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(185, 28, 28)
    no_points = [
        "Never display derogatory labels ('This student is weak').",
        "Never diagnose learning disabilities or make psychological claims.",
        "Never make black-box automated decisions without human teacher review.",
        "Never expose student data publicly or cross-student."
    ]
    for np in no_points:
        p = tf1.add_paragraph()
        p.text = "❌ " + np
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    c2 = add_card(s3, 4.8, 1.8, 3.6, 4.8, bg_color=RGBColor(240, 253, 244), border_color=RGBColor(187, 247, 208))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "WHAT WE COMMUNICATE ✅"
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_GREEN
    yes_points = [
        "'Possible academic support signal detected.'",
        "'Review Recommended on Kirchhoff's Laws.'",
        "'Confidence mismatch observed: student feels confident but selected misconception.'",
        "Targeted academic support tailored to specific learning behavior."
    ]
    for yp in yes_points:
        p = tf2.add_paragraph()
        p.text = "✔ " + yp
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    c3 = add_card(s3, 8.8, 1.8, 3.7, 4.8, bg_color=RGBColor(238, 242, 255), border_color=RGBColor(199, 210, 254))
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "TEACHER AGENCY 🧑‍🏫"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_ACCENT
    t_points = [
        "The AI provides transparent, verifiable evidence.",
        "Teacher inspects every response, time metric, and error cluster.",
        "Teacher decides whether and how to intervene.",
        "Teacher selects intervention strategy: concept review, practice sheet, or 3-question check."
    ]
    for tp in t_points:
        p = tf3.add_paragraph()
        p.text = "💡 " + tp
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    # ==========================================
    # SLIDE 4: The Closed-Loop Educational Cycle
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4, COLOR_LIGHT_BG)
    add_header(s4, "Core Product Architecture", "The End-to-End Educational Feedback Loop")

    loop_steps = [
        ("1. Student Learning", "Student takes quiz, answers MCQs with response timer."),
        ("2. Data Collection", "Stores question ID, chosen option, response time, confidence level."),
        ("3. Pattern Analysis", "Signal engine evaluates error rate, latency contrast, and mismatches."),
        ("4. Support Signal", "Support Score computed (0-100). If >= 45, status set to REVIEW."),
        ("5. Teacher Review", "Teacher inspects transparent evidence drawer explaining WHY flagged."),
        ("6. Intervention", "Teacher assigns targeted action (e.g. 3-question concept check)."),
        ("7. Follow-up Test", "Student completes targeted check to re-verify concept grasp."),
        ("8. Measured Result", "System computes delta (+40% improvement, status: Improved).")
    ]

    for idx, (stitle, sdesc) in enumerate(loop_steps):
        row = idx // 4
        col = idx % 4
        left = 0.8 + (col * 2.95)
        top = 1.8 + (row * 2.5)
        
        card = add_card(s4, left, top, 2.75, 2.2, bg_color=COLOR_CARD_BG)
        tf = card.text_frame
        tf.word_wrap = True
        p_num = tf.paragraphs[0]
        p_num.text = stitle
        p_num.font.size = Pt(14)
        p_num.font.bold = True
        p_num.font.color.rgb = COLOR_PRIMARY

        p_body = tf.add_paragraph()
        p_body.text = sdesc
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = COLOR_MUTED

    # ==========================================
    # SLIDE 5: The Confidence Mismatch Engine (Novelty)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5, COLOR_LIGHT_BG)
    add_header(s5, "Innovation Spotlight", "The 4-Tier Confidence Mismatch Matrix")

    # Left: Explanation
    card_info = add_card(s5, 0.8, 1.8, 4.5, 5.0)
    tf_ci = card_info.text_frame
    tf_ci.word_wrap = True
    p_ci = tf_ci.paragraphs[0]
    p_ci.text = "Why Confidence Matters"
    p_ci.font.size = Pt(18)
    p_ci.font.bold = True
    p_ci.font.color.rgb = COLOR_PRIMARY

    bullets_ci = [
        "In SmartEdu, after selecting an answer, students MUST rate their confidence:",
        "• Not Sure",
        "• Somewhat Sure",
        "• Confident",
        "• Very Confident",
        "Crucial Insight: A student who answers incorrectly while being 'Very Confident' is fundamentally different from a student who guessed.",
        "Overconfidence on errors reveals deep misconceptions. Underconfidence on correct answers reveals hesitation."
    ]
    for b in bullets_ci:
        p = tf_ci.add_paragraph()
        p.text = b
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    # Right: 2x2 Matrix
    matrix_cells = [
        ("CORRECT + HIGH CONFIDENCE", "Mastery Demonstrated 🌟", "Student understands concept and correctly applies principles with certainty.", RGBColor(240, 253, 244), COLOR_GREEN, 5.6, 1.8),
        ("INCORRECT + HIGH CONFIDENCE", "Critical Misconception ⚠️", "Strongest support signal! Student has a false belief in an incorrect rule.", RGBColor(254, 242, 242), RGBColor(185, 28, 28), 9.4, 1.8),
        ("CORRECT + LOW CONFIDENCE", "Hesitation / Low Efficacy ❓", "Student gets it right but doubts their ability. Reassurance needed.", RGBColor(254, 249, 195), COLOR_AMBER, 5.6, 4.4),
        ("INCORRECT + LOW CONFIDENCE", "Knowledge Gap (Guessing) 📉", "Student recognizes they don't know the material. Needs first-time instruction.", RGBColor(241, 245, 249), COLOR_MUTED, 9.4, 4.4)
    ]

    for title, badge, desc, bg, txt_col, l, t in matrix_cells:
        mc = add_card(s5, l, t, 3.6, 2.4, bg_color=bg)
        tf = mc.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = txt_col

        p_b = tf.add_paragraph()
        p_b.text = badge
        p_b.font.size = Pt(13)
        p_b.font.bold = True
        p_b.font.color.rgb = txt_col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_TEXT

    # ==========================================
    # SLIDE 6: Support Signal Algorithm & Evidence Engine
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6, COLOR_LIGHT_BG)
    add_header(s6, "Algorithmic Grounding", "Learning Support Signal Scoring Engine")

    factors = [
        ("1. Error Frequency (0-35 pts)", "Measures error concentration on a specific topic. If error rate on concept >= 60%, flags high distress.", COLOR_PRIMARY),
        ("2. Repeated Attempts (0-20 pts)", "Tracks repeated tries on questions within the same topic without score stabilization.", COLOR_ACCENT),
        ("3. Response Latency Contrast (0-25 pts)", "Compares average topic latency against the student's personal baseline across other topics. Ratio > 1.3x triggers struggle flag.", COLOR_AMBER),
        ("4. Confidence Mismatches (0-25 pts)", "Overconfidence on errors weighted heavily (10 pts each). Detects conceptual misconceptions over lucky guesses.", COLOR_GREEN)
    ]

    for idx, (ftitle, fdesc, fcol) in enumerate(factors):
        l = 0.8 + (idx * 2.95)
        c = add_card(s6, l, 1.8, 2.75, 4.8)
        tf = c.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = ftitle
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = fcol

        p2 = tf.add_paragraph()
        p2.text = fdesc
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_TEXT

        p3 = tf.add_paragraph()
        p3.text = "\nComposite Formula:\nScore = min(100, Σ Factors)\n\nThreshold:\nScore ≥ 45 ➜ REVIEW"
        p3.font.size = Pt(11)
        p3.font.bold = True
        p3.font.color.rgb = COLOR_MUTED

    # ==========================================
    # SLIDE 7: Teacher Review & Transparent Evidence
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7, COLOR_LIGHT_BG)
    add_header(s7, "Teacher Experience", "Transparent Evidence: No Black-Box AI")

    # Left: Mock Evidence Screen Card
    mock = add_card(s7, 0.8, 1.8, 6.2, 5.0, bg_color=RGBColor(255, 251, 235), border_color=RGBColor(252, 211, 77))
    tf_m = mock.text_frame
    tf_m.word_wrap = True
    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "EVIDENCE DRAWER: ALEX MORGAN (82% OVERALL)"
    p_m1.font.size = Pt(14)
    p_m1.font.bold = True
    p_m1.font.color.rgb = RGBColor(146, 64, 14)

    evidence_bullets = [
        "Topic: Kirchhoff's Laws | Subject: Physics | Support Score: 71.1 (REVIEW)",
        "------------------------------------------------------------------",
        "• 5 repeated mistakes recorded on 'Kirchhoff's Laws'.",
        "• 4 confidence mismatches: Student selected 'Very Confident' on wrong answers (conceptual misconception).",
        "• Average response time (48s) is 2.2x higher than Alex's baseline (22s).",
        "• 3 repeated attempts without score stabilization.",
        "------------------------------------------------------------------",
        "Recent Question: 'Kirchhoff's loop rule expresses conservation of...'",
        "Alex selected: [A] Electric charge (Wrong!) | Confidence: Very Confident",
        "Correct Answer: [B] Energy | Latency: 48.0s"
    ]
    for eb in evidence_bullets:
        p = tf_m.add_paragraph()
        p.text = eb
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT

    # Right: Targeted Interventions
    card_act = add_card(s7, 7.3, 1.8, 5.2, 5.0)
    tf_act = card_act.text_frame
    tf_act.word_wrap = True
    p_act = tf_act.paragraphs[0]
    p_act.text = "Targeted Interventions in 1 Click 🎯"
    p_act.font.size = Pt(18)
    p_act.font.bold = True
    p_act.font.color.rgb = COLOR_PRIMARY

    actions = [
        ("3-Question Concept Check", "Rapid targeted micro-assessment to evaluate if the core misconception is cleared."),
        ("Concept Explanation", "Teacher provides specialized notes and circuit convention diagrams."),
        ("Practice Worksheet", "Structured progressive circuit exercises focusing on junction rules."),
        ("Teacher Guidance Note", "e.g. 'Review Kirchhoff's loop rule sign convention (+IR vs -IR) before attempting advanced circuits.'")
    ]
    for atitle, adesc in actions:
        p_t = tf_act.add_paragraph()
        p_t.text = "✔ " + atitle
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_ACCENT

        p_d = tf_act.add_paragraph()
        p_d.text = adesc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_MUTED

    # ==========================================
    # SLIDE 8: Follow-up Assessment & Measured Results
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8, COLOR_LIGHT_BG)
    add_header(s8, "Measured Impact", "Closing the Loop: Quantified Improvement")

    # 3 Stat Cards showing Before, After, Delta
    sc1 = add_card(s8, 0.8, 1.8, 3.6, 2.2, bg_color=RGBColor(254, 242, 242), border_color=RGBColor(254, 202, 202))
    tf_sc1 = sc1.text_frame
    tf_sc1.word_wrap = True
    p = tf_sc1.paragraphs[0]
    p.text = "BEFORE INTERVENTION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(185, 28, 28)
    p_num = tf_sc1.add_paragraph()
    p_num.text = "40%"
    p_num.font.size = Pt(40)
    p_num.font.bold = True
    p_num.font.color.rgb = RGBColor(185, 28, 28)
    p_sub = tf_sc1.add_paragraph()
    p_sub.text = "Initial accuracy on concept questions"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_MUTED

    sc2 = add_card(s8, 4.8, 1.8, 3.6, 2.2, bg_color=RGBColor(240, 253, 244), border_color=RGBColor(187, 247, 208))
    tf_sc2 = sc2.text_frame
    tf_sc2.word_wrap = True
    p = tf_sc2.paragraphs[0]
    p.text = "AFTER INTERVENTION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p_num = tf_sc2.add_paragraph()
    p_num.text = "80%"
    p_num.font.size = Pt(40)
    p_num.font.bold = True
    p_num.font.color.rgb = COLOR_GREEN
    p_sub = tf_sc2.add_paragraph()
    p_sub.text = "3-Question Concept Check accuracy"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_MUTED

    sc3 = add_card(s8, 8.8, 1.8, 3.7, 2.2, bg_color=RGBColor(238, 242, 255), border_color=RGBColor(199, 210, 254))
    tf_sc3 = sc3.text_frame
    tf_sc3.word_wrap = True
    p = tf_sc3.paragraphs[0]
    p.text = "MEASURED DELTA"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p_num = tf_sc3.add_paragraph()
    p_num.text = "+40%"
    p_num.font.size = Pt(40)
    p_num.font.bold = True
    p_num.font.color.rgb = COLOR_ACCENT
    p_sub = tf_sc3.add_paragraph()
    p_sub.text = "Status: 'Improved' (Signal Resolved)"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_MUTED

    # Bottom Detailed Summary
    card_bot = add_card(s8, 0.8, 4.3, 11.7, 2.5)
    tf_b = card_bot.text_frame
    tf_b.word_wrap = True
    p_bt = tf_b.paragraphs[0]
    p_bt.text = "Objective Progression Rules (Configurable & Reproducible)"
    p_bt.font.size = Pt(16)
    p_bt.font.bold = True
    p_bt.font.color.rgb = COLOR_PRIMARY

    rules = [
        "Improvement ≥ +25% ➜ Result Status: 'Improved' (Support signal marked RESOLVED).",
        "Improvement between +10% and +24% ➜ Result Status: 'Partially Improved'.",
        "Improvement < +10% ➜ Result Status: 'Further Review Recommended' (Flag retained on Teacher Dashboard).",
        "All before/after results permanently stored in follow_up_results table for longitudinal growth tracking."
    ]
    for r in rules:
        p = tf_b.add_paragraph()
        p.text = "• " + r
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    # ==========================================
    # SLIDE 9: Technology Stack & Architectural Integrity
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9, COLOR_LIGHT_BG)
    add_header(s9, "Technical Implementation", "Production-Ready Full-Stack Architecture")

    tech_cards = [
        ("Mobile-First Frontend 📱", [
            "Native Android viewport shell with speaker notch & status bar.",
            "Responsive full-width toggle for desktop presentation.",
            "Touch targets >= 44x44px, bottom tab navigation.",
            "Zero bloated frameworks: Clean HTML5, Vanilla CSS tokens & ES6 JavaScript."
        ], 0.8, 1.8),
        ("REST Backend & RBAC 🛡️", [
            "Python Starlette ASGI server with Uvicorn engine.",
            "HMAC-SHA256 cryptographically signed session tokens.",
            "PBKDF2-HMAC-SHA256 password hashing (100,000 rounds, unique salts).",
            "Role-Based Access Control on every API endpoint."
        ], 4.8, 1.8),
        ("Persistent Relational Database 💾", [
            "Real disk-backed SQLite database (smartedu.db) with WAL mode.",
            "Strict foreign keys (PRAGMA foreign_keys = ON) & cascade rules.",
            "16 structured tables covering users, curriculum, quizzes, and signals.",
            "Survives application restarts, logout/login, and deployments."
        ], 8.8, 1.8)
    ]

    for title, bullets, l, t in tech_cards:
        c = add_card(s9, l, t, 3.7, 5.0)
        tf = c.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_PRIMARY

        for b in bullets:
            p = tf.add_paragraph()
            p.text = "• " + b
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_TEXT

    # ==========================================
    # SLIDE 10: Rigorous Acceptance Testing & Demo
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10, COLOR_LIGHT_BG)
    add_header(s10, "Verification & Validation", "All 25 Acceptance Criteria Verified & Passing")

    # Left: Acceptance Test Results
    card_test = add_card(s10, 0.8, 1.8, 5.6, 5.0)
    tf_t = card_test.text_frame
    tf_t.word_wrap = True
    p_tt = tf_t.paragraphs[0]
    p_tt.text = "Automated Test Suite (100% Green) ✅"
    p_tt.font.size = Pt(16)
    p_tt.font.bold = True
    p_tt.font.color.rgb = COLOR_GREEN

    test_items = [
        "1-4: Admin creates teachers, students, & assigns classes/subjects.",
        "5-6: Teacher authors multi-question quizzes with topic mapping.",
        "7-10: Student takes quiz with live timer & confidence selection.",
        "11-14: Question attempts saved, engine triggers support signal.",
        "15-16: Teacher inspects transparent explainable evidence.",
        "17-20: Teacher assigns intervention, student completes check (+40%).",
        "21-22: Only admin can permanently delete records safely.",
        "23-24: Student blocked from teacher/admin; Teacher blocked from admin.",
        "25: Data persists across database reconnection & restarts."
    ]
    for ti in test_items:
        p = tf_t.add_paragraph()
        p.text = "✔ " + ti
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT

    # Right: Seed Dataset
    card_seed = add_card(s10, 6.9, 1.8, 5.6, 5.0, bg_color=RGBColor(238, 242, 255), border_color=RGBColor(199, 210, 254))
    tf_s = card_seed.text_frame
    tf_s.word_wrap = True
    p_st = tf_s.paragraphs[0]
    p_st.text = "Comprehensive Synthetic Demo Data 📊"
    p_st.font.size = Pt(16)
    p_st.font.bold = True
    p_st.font.color.rgb = COLOR_ACCENT

    seed_items = [
        "5 Faculty Teachers (Physics, Chemistry, Math, CS, Biology).",
        "20 Enrolled Students across Grade 10-A, Grade 11-Sci, Grade 12-Adv.",
        "4 Subjects, 10 Chapters, 30 Topics.",
        "10 Published Quizzes with 100+ high-quality academic questions.",
        "Real Seeded Scenarios:",
        "  • Alex Morgan: 82% overall, flagged on Kirchhoff's Laws.",
        "  • Priya Sharma: Completed intervention, +40% measured improvement.",
        "1-Click Evaluator Fast-Login Bar for instant role testing during demo."
    ]
    for si in seed_items:
        p = tf_s.add_paragraph()
        p.text = "• " + si
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT

    # ==========================================
    # SLIDE 11: Conclusion & The Vision
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_background(s11, COLOR_NAVY)

    tb_end = s11.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(4.5))
    tf_e = tb_end.text_frame
    tf_e.word_wrap = True

    p_e1 = tf_e.paragraphs[0]
    p_e1.text = "Transforming Education Through Proactive Care"
    p_e1.font.size = Pt(40)
    p_e1.font.bold = True
    p_e1.font.color.rgb = COLOR_WHITE

    p_e2 = tf_e.add_paragraph()
    p_e2.text = "Traditional grading is an autopsy of past performance.\nSmartEdu is preventive healthcare for academic learning."
    p_e2.font.size = Pt(22)
    p_e2.font.color.rgb = RGBColor(147, 197, 253)

    p_e3 = tf_e.add_paragraph()
    p_e3.text = "\nBy combining latency, repeated errors, and confidence mismatch with explainable AI and teacher agency, we ensure NO student silently falls behind."
    p_e3.font.size = Pt(16)
    p_e3.font.color.rgb = RGBColor(203, 213, 225)

    card_foot = add_card(s11, 1.0, 5.2, 11.3, 1.4, bg_color=RGBColor(30, 41, 59), border_color=COLOR_ACCENT)
    tf_cf = card_foot.text_frame
    tf_cf.word_wrap = True
    p_cf1 = tf_cf.paragraphs[0]
    p_cf1.text = "THANK YOU!  •  TEAM INFINITY X"
    p_cf1.font.size = Pt(18)
    p_cf1.font.bold = True
    p_cf1.font.color.rgb = RGBColor(250, 204, 21)

    p_cf2 = tf_cf.add_paragraph()
    p_cf2.text = "Live Web App: http://127.0.0.1:8000/  •  Presentation Deck: http://127.0.0.1:8000/presentation.html"
    p_cf2.font.size = Pt(13)
    p_cf2.font.color.rgb = COLOR_WHITE

    # Save presentation
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smartedu_hackathon_presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_presentation()
