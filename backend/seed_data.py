import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import uuid
from backend.database import get_db, init_db
from backend.auth import hash_password
from backend.engine import analyze_student_learning_signals

DEFAULT_PASSWORD = "Password123!"

def seed_database(db_path=None):
    init_db(db_path)
    
    with get_db(db_path) as conn:
        # Check if already seeded
        admin_exists = conn.execute("SELECT id FROM users WHERE email = 'admin@smartedu.edu'").fetchone()
        if admin_exists:
            print("Database already contains seed data.")
            return

        print("Seeding SmartEdu database with realistic synthetic educational data...")
        
        # 1. Admin User
        admin_id = "USR-ADMIN01"
        admin_pwd, admin_salt = hash_password("Admin123!")
        conn.execute(
            "INSERT INTO users (id, email, password_hash, salt, role, status) VALUES (?, ?, ?, ?, 'admin', 'active')",
            (admin_id, "admin@smartedu.edu", admin_pwd, admin_salt)
        )
        
        # 2. Classes (3 classes)
        classes_data = [
            ("CLS-10A", "Grade 10", "A", "2026-2027"),
            ("CLS-11SCI", "Grade 11", "Science-A", "2026-2027"),
            ("CLS-12ADV", "Grade 12", "Advanced STEM", "2026-2027")
        ]
        for cid, cname, sec, yr in classes_data:
            conn.execute(
                "INSERT INTO classes (class_id, class_name, section, academic_year) VALUES (?, ?, ?, ?)",
                (cid, cname, sec, yr)
            )
            
        # 3. Subjects (4 subjects)
        subjects_data = [
            ("SUB-PHY", "Physics", "Fundamentals of mechanics, electromagnetism, and modern physics"),
            ("SUB-CHM", "Chemistry", "Atomic structure, chemical reactions, bonding, and thermodynamics"),
            ("SUB-MTH", "Mathematics", "Calculus, analytical geometry, and advanced functions"),
            ("SUB-BIO", "Biology", "Cellular biology, genetics, physiology, and ecosystems")
        ]
        for sid, sname, sdesc in subjects_data:
            conn.execute(
                "INSERT INTO subjects (subject_id, subject_name, description) VALUES (?, ?, ?)",
                (sid, sname, sdesc)
            )
            
        # 4. Chapters (10 chapters) & Topics (30 topics)
        curriculum = [
            # Physics
            ("CHP-PHY01", "SUB-PHY", "Current Electricity", [
                ("TOP-PHY01", "Kirchhoff's Laws"),
                ("TOP-PHY02", "Ohm's Law & Resistance"),
                ("TOP-PHY03", "Wheatstone Bridge & Potentiometer")
            ]),
            ("CHP-PHY02", "SUB-PHY", "Wave Optics", [
                ("TOP-PHY04", "Huygens Principle"),
                ("TOP-PHY05", "Interference of Light"),
                ("TOP-PHY06", "Diffraction & Polarization")
            ]),
            ("CHP-PHY03", "SUB-PHY", "Modern Physics", [
                ("TOP-PHY07", "Photoelectric Effect"),
                ("TOP-PHY08", "Bohr Atomic Model"),
                ("TOP-PHY09", "Nuclear Fission & Fusion")
            ]),
            # Chemistry
            ("CHP-CHM01", "SUB-CHM", "Chemical Bonding", [
                ("TOP-CHM01", "Ionic Bonding & Lattice Energy"),
                ("TOP-CHM02", "Covalent Bonding & Hybridization"),
                ("TOP-CHM03", "Molecular Orbital Theory")
            ]),
            ("CHP-CHM02", "SUB-CHM", "Thermodynamics", [
                ("TOP-CHM04", "Enthalpy & First Law"),
                ("TOP-CHM05", "Entropy & Spontaneity"),
                ("TOP-CHM06", "Gibbs Free Energy")
            ]),
            ("CHP-CHM03", "SUB-CHM", "Organic Chemistry", [
                ("TOP-CHM07", "Hydrocarbons & Isomerism"),
                ("TOP-CHM08", "Alcohols & Ethers"),
                ("TOP-CHM09", "Carbonyl Compounds")
            ]),
            # Mathematics
            ("CHP-MTH01", "SUB-MTH", "Differential Calculus", [
                ("TOP-MTH01", "Limits & Continuity"),
                ("TOP-MTH02", "Chain Rule & Implicit Differentiation"),
                ("TOP-MTH03", "Applications of Derivatives")
            ]),
            ("CHP-MTH02", "SUB-MTH", "Integral Calculus", [
                ("TOP-MTH04", "Indefinite Integrals"),
                ("TOP-MTH05", "Definite Integrals & Areas"),
                ("TOP-MTH06", "Differential Equations")
            ]),
            # Biology
            ("CHP-BIO01", "SUB-BIO", "Cell Biology", [
                ("TOP-BIO01", "Cell Membrane & Transport"),
                ("TOP-BIO02", "Cell Organelles & Energy"),
                ("TOP-BIO03", "Mitosis & Cell Cycle")
            ]),
            ("CHP-BIO02", "SUB-BIO", "Genetics & Inheritance", [
                ("TOP-BIO04", "Mendelian Genetics"),
                ("TOP-BIO05", "DNA Replication & Structure"),
                ("TOP-BIO06", "Transcription & Translation")
            ])
        ]
        
        for chp_id, sub_id, chp_name, topics in curriculum:
            conn.execute(
                "INSERT INTO chapters (chapter_id, subject_id, chapter_name) VALUES (?, ?, ?)",
                (chp_id, sub_id, chp_name)
            )
            for top_id, top_name in topics:
                conn.execute(
                    "INSERT INTO topics (topic_id, chapter_id, topic_name) VALUES (?, ?, ?)",
                    (top_id, chp_id, top_name)
                )
                
        # 5. Teachers (5 teachers)
        teachers_data = [
            ("TCH-01", "sarah.jenkins@smartedu.edu", "Dr. Sarah Jenkins", "Physics", "EMP-PHY101", [("CLS-11SCI", "SUB-PHY"), ("CLS-12ADV", "SUB-PHY")]),
            ("TCH-02", "robert.miller@smartedu.edu", "Prof. Robert Miller", "Chemistry", "EMP-CHM202", [("CLS-11SCI", "SUB-CHM"), ("CLS-10A", "SUB-CHM")]),
            ("TCH-03", "elena.rostova@smartedu.edu", "Dr. Elena Rostova", "Mathematics", "EMP-MTH303", [("CLS-11SCI", "SUB-MTH"), ("CLS-12ADV", "SUB-MTH")]),
            ("TCH-04", "alan.turing@smartedu.edu", "Alan Turing", "Computer Science", "EMP-CS404", [("CLS-10A", "SUB-PHY"), ("CLS-12ADV", "SUB-MTH")]),
            ("TCH-05", "maria.garcia@smartedu.edu", "Maria Garcia", "Biology", "EMP-BIO505", [("CLS-10A", "SUB-BIO"), ("CLS-11SCI", "SUB-BIO")])
        ]
        
        for tid, email, name, dept, emp_no, assigned in teachers_data:
            uid = f"USR-{tid}"
            p_hash, salt = hash_password(DEFAULT_PASSWORD)
            conn.execute(
                "INSERT INTO users (id, email, password_hash, salt, role, status) VALUES (?, ?, ?, ?, 'teacher', 'active')",
                (uid, email, p_hash, salt)
            )
            conn.execute(
                "INSERT INTO teachers (teacher_id, user_id, name, department, employee_number, status) VALUES (?, ?, ?, ?, ?, 'active')",
                (tid, uid, name, dept, emp_no)
            )
            for cid, sid in assigned:
                conn.execute(
                    "INSERT INTO teacher_classes (id, teacher_id, class_id, subject_id) VALUES (?, ?, ?, ?)",
                    (f"TC-{tid}-{cid}-{sid}", tid, cid, sid)
                )

        # 6. Students (20 students)
        students_raw = [
            ("STU-101", "alex.morgan@smartedu.edu", "Alex Morgan", "CLS-11SCI", "A", "ADM-2026-001"), # Primary demo student
            ("STU-102", "priya.sharma@smartedu.edu", "Priya Sharma", "CLS-11SCI", "A", "ADM-2026-002"), # Demo student with completed intervention
            ("STU-103", "liam.chen@smartedu.edu", "Liam Chen", "CLS-11SCI", "A", "ADM-2026-003"),
            ("STU-104", "emily.davis@smartedu.edu", "Emily Davis", "CLS-11SCI", "A", "ADM-2026-004"),
            ("STU-105", "noah.wilson@smartedu.edu", "Noah Wilson", "CLS-11SCI", "A", "ADM-2026-005"),
            ("STU-106", "sophia.taylor@smartedu.edu", "Sophia Taylor", "CLS-11SCI", "A", "ADM-2026-006"),
            ("STU-107", "lucas.martinez@smartedu.edu", "Lucas Martinez", "CLS-11SCI", "A", "ADM-2026-007"),
            ("STU-108", "mia.anderson@smartedu.edu", "Mia Anderson", "CLS-10A", "A", "ADM-2026-008"),
            ("STU-109", "ethan.thomas@smartedu.edu", "Ethan Thomas", "CLS-10A", "A", "ADM-2026-009"),
            ("STU-110", "harper.jackson@smartedu.edu", "Harper Jackson", "CLS-10A", "A", "ADM-2026-010"),
            ("STU-111", "mason.white@smartedu.edu", "Mason White", "CLS-10A", "A", "ADM-2026-011"),
            ("STU-112", "evelyn.harris@smartedu.edu", "Evelyn Harris", "CLS-10A", "A", "ADM-2026-012"),
            ("STU-113", "oliver.martin@smartedu.edu", "Oliver Martin", "CLS-10A", "A", "ADM-2026-013"),
            ("STU-114", "charlotte.lee@smartedu.edu", "Charlotte Lee", "CLS-12ADV", "A", "ADM-2026-014"),
            ("STU-115", "elijah.walker@smartedu.edu", "Elijah Walker", "CLS-12ADV", "A", "ADM-2026-015"),
            ("STU-116", "amelia.hall@smartedu.edu", "Amelia Hall", "CLS-12ADV", "A", "ADM-2026-016"),
            ("STU-117", "james.allen@smartedu.edu", "James Allen", "CLS-12ADV", "A", "ADM-2026-017"),
            ("STU-118", "harper.young@smartedu.edu", "Harper Young", "CLS-12ADV", "A", "ADM-2026-018"),
            ("STU-119", "benjamin.king@smartedu.edu", "Benjamin King", "CLS-12ADV", "A", "ADM-2026-019"),
            ("STU-120", "isabella.scott@smartedu.edu", "Isabella Scott", "CLS-12ADV", "A", "ADM-2026-020")
        ]
        
        for sid, email, name, cid, sec, adm_no in students_raw:
            uid = f"USR-{sid}"
            p_hash, salt = hash_password(DEFAULT_PASSWORD)
            conn.execute(
                "INSERT INTO users (id, email, password_hash, salt, role, status) VALUES (?, ?, ?, ?, 'student', 'active')",
                (uid, email, p_hash, salt)
            )
            conn.execute(
                "INSERT INTO students (student_id, user_id, name, class_id, section, admission_number, status) VALUES (?, ?, ?, ?, ?, ?, 'active')",
                (sid, uid, name, cid, sec, adm_no)
            )

        # 7. Quizzes (10 quizzes) & Questions (100+ questions)
        quizzes_info = [
            ("QZ-PHY01", "Circuits & Current Electricity Masterclass", "In-depth review of electric current, Ohm's law, and Kirchhoff's loop and junction rules.", "SUB-PHY", "CHP-PHY01", "TCH-01", "Medium", 20),
            ("QZ-PHY02", "Wave Optics & Interference Phenomena", "Analyzing coherent light sources, double-slit patterns, and diffraction limits.", "SUB-PHY", "CHP-PHY02", "TCH-01", "Hard", 25),
            ("QZ-PHY03", "Photoelectric Effect & Quantum Physics", "Photon energy, work function, stopping potential, and Einstein's equations.", "SUB-PHY", "CHP-PHY03", "TCH-01", "Medium", 15),
            ("QZ-CHM01", "Chemical Bonding & Hybridization Analysis", "Molecular orbital theory, sigma/pi bonds, and resonance structures.", "SUB-CHM", "CHP-CHM01", "TCH-02", "Medium", 20),
            ("QZ-CHM02", "Thermodynamics & Spontaneity Rules", "Enthalpy, entropy changes, and Gibbs free energy calculations.", "SUB-CHM", "CHP-CHM02", "TCH-02", "Hard", 25),
            ("QZ-CHM03", "Organic Chemistry: Functional Groups & Reactions", "Nomenclature, electrophilic additions, and oxidation pathways.", "SUB-CHM", "CHP-CHM03", "TCH-02", "Medium", 20),
            ("QZ-MTH01", "Calculus: Differentiation & Curve Sketching", "Derivatives, inflection points, and optimization problems.", "SUB-MTH", "CHP-MTH01", "TCH-03", "Hard", 30),
            ("QZ-MTH02", "Definite Integrals & Area Calculations", "Fundamental theorem of calculus and area between intersecting curves.", "SUB-MTH", "CHP-MTH02", "TCH-03", "Hard", 25),
            ("QZ-BIO01", "Cell Biology & Membrane Transport", "Osmosis, active transport mechanisms, and organelle functions.", "SUB-BIO", "CHP-BIO01", "TCH-05", "Easy", 15),
            ("QZ-BIO02", "Molecular Genetics & DNA Replication", "Helicase, DNA polymerase, leading/lagging strand synthesis, and codons.", "SUB-BIO", "CHP-BIO02", "TCH-05", "Medium", 20)
        ]
        
        for qid, title, desc, sid, cid, tid, diff, tlim in quizzes_info:
            conn.execute(
                """
                INSERT INTO quizzes (quiz_id, title, description, subject_id, chapter_id, teacher_id, difficulty, time_limit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'published')
                """,
                (qid, title, desc, sid, cid, tid, diff, tlim)
            )

        # Questions template generator (10 questions per quiz = 100 questions total)
        question_templates = {
            "QZ-PHY01": [
                ("TOP-PHY01", "What fundamental physical conservation law forms the basis of Kirchhoff's Current Law (Junction Rule)?", "Conservation of Energy", "Conservation of Electric Charge", "Conservation of Momentum", "Conservation of Mass", "B", "Kirchhoff's Current Law states that total current entering a junction equals current leaving it, conserving electric charge."),
                ("TOP-PHY01", "In a multi-loop circuit, Kirchhoff's Voltage Law (Loop Rule) states that the sum of potential differences around any closed loop must equal:", "Total EMF squared", "Zero", "The highest resistor value", "The total current times total resistance only", "B", "KVL reflects the principle of conservation of energy: the total work done moving charge around a closed loop is zero."),
                ("TOP-PHY01", "When traversing a resistor of resistance R in the direction of current I, the potential change according to Kirchhoff's sign convention is:", "+IR (potential rise)", "-IR (potential drop)", "Zero", "Independent of current direction", "B", "Moving along the current vector through a resistive element causes a potential drop: -IR."),
                ("TOP-PHY01", "Two ideal batteries of 12V and 6V are connected in opposition in a single closed circuit with a 3 Ohm resistor. What is the current in the loop?", "6.0 A", "2.0 A", "4.0 A", "18.0 A", "B", "Net EMF = 12V - 6V = 6V. Using loop rule: 6V - I(3) = 0 => I = 2.0 A."),
                ("TOP-PHY01", "Which of the following equations correctly represents the junction where currents I1 and I2 enter, while I3 and I4 leave?", "I1 + I3 = I2 + I4", "I1 + I2 - I3 - I4 = 0", "I1 + I2 + I3 + I4 = 0", "I1 * I2 = I3 * I4", "B", "Sum of currents entering equals sum leaving: I1 + I2 = I3 + I4, or I1 + I2 - I3 - I4 = 0."),
                ("TOP-PHY02", "Ohm's law is fundamentally valid for:", "All conductors under all temperatures", "Ohmic conductors with constant physical conditions and temperature", "Diodes and transistors at room temperature", "Electrolytes during electrolysis", "B", "Ohm's law applies to metallic conductors provided temperature and physical state remain constant."),
                ("TOP-PHY02", "If a wire of resistance R is stretched uniformly to double its original length, its new resistance will be:", "2R", "4R", "R/2", "R/4", "B", "Doubling length while conserving volume halves the cross-sectional area: R' = rho * (2L) / (A/2) = 4R."),
                ("TOP-PHY02", "The resistivity of a typical semiconductor:", "Increases linearly with temperature", "Decreases exponentially with temperature", "Is independent of temperature", "Remains zero up to critical temperature", "B", "In semiconductors, thermal agitation frees charge carriers, decreasing resistivity as temperature rises."),
                ("TOP-PHY03", "A Wheatstone bridge is most sensitive when:", "All four arms have equal resistance", "The galvanometer has infinite resistance", "The battery voltage is very small", "Two opposite arms have near-zero resistance", "A", "Sensitivity is maximized when the four resistive arms are of comparable magnitude."),
                ("TOP-PHY03", "A potentiometer is preferred over a traditional voltmeter for measuring cell EMF because:", "It draws heavy current from the cell", "It measures EMF at the null deflection point without drawing current", "It has lower internal resistance", "It is smaller and more portable", "B", "At null balance, no current flows from the test cell, preventing internal voltage drops.")
            ],
            "QZ-PHY02": [
                ("TOP-PHY04", "According to Huygens' principle, every point on a primary wavefront acts as:", "A photon absorber", "A source of secondary spherical wavelets", "A point of absolute dark fringe", "A reflector of transverse oscillations", "B", "Each wavefront point serves as an omnidirectional source of secondary spherical wavelets."),
                ("TOP-PHY04", "The geometric envelope tangent to secondary wavelets at any subsequent instant represents:", "The ray trajectory", "The new wavefront", "The diffraction angle", "The polarization axis", "B", "The forward envelope of the secondary wavelets traces the next position of the wavefront."),
                ("TOP-PHY05", "In Young's double slit experiment, if the distance between slits is halved and screen distance doubled, fringe width beta becomes:", "Same", "Twice", "Four times", "One-fourth", "C", "Fringe width beta = (lambda * D) / d. If D doubles and d halves: beta' = 4 * beta."),
                ("TOP-PHY05", "Two light sources are defined as mutually coherent if they maintain:", "Identical amplitude only", "A constant phase relationship over time", "Equal wavelength but opposite polarization", "Random phase differences", "B", "Coherence requires constant phase difference over the measurement duration."),
                ("TOP-PHY05", "The central fringe in Young's interference pattern using monochromatic light is always:", "Dark", "Bright", "Colored with red edges", "Invisible", "B", "At the geometric center, the optical path difference between the two symmetric slits is zero, producing constructive interference."),
                ("TOP-PHY06", "Diffraction is fundamentally explained as:", "Bending of light around sharp edges and apertures", "Total internal reflection in dense media", "Complete absorption of high-frequency components", "Rotational polarization through crystals", "A", "Diffraction refers to the deviation of wave propagation from straight geometric rays when encountering obstacles."),
                ("TOP-PHY06", "In Fraunhofer single-slit diffraction, the angular width of the central maximum is:", "lambda / a", "2 * lambda / a", "lambda / (2a)", "a / lambda", "B", "The central maximum extends from -lambda/a to +lambda/a, having an angular width of 2*lambda/a."),
                ("TOP-PHY06", "Brewster's angle theta_p satisfies which relationship with the refractive index n of the dielectric?", "sin(theta_p) = n", "tan(theta_p) = n", "cos(theta_p) = n", "cot(theta_p) = n", "B", "Brewster's law states tan(theta_p) = n2 / n1; reflected light is totally linearly polarized."),
                ("TOP-PHY05", "If white light is used in Young's double slit experiment, the central fringe is:", "Black", "White", "Red", "Violet", "B", "At zero path difference, all wavelengths interfere constructively, producing a crisp white central fringe."),
                ("TOP-PHY06", "Which phenomenon conclusively demonstrates the transverse nature of light waves?", "Interference", "Diffraction", "Polarization", "Refraction", "C", "Polarization can only occur in transverse oscillations, proving electromagnetic waves are transverse.")
            ],
            "QZ-PHY03": [
                ("TOP-PHY07", "In the photoelectric effect, increasing the intensity of incident light above threshold frequency increases:", "Maximum kinetic energy of photoelectrons", "The photoelectric saturation current", "The stopping potential", "The threshold frequency", "B", "Higher intensity delivers more photons per second, liberating more electrons per unit time."),
                ("TOP-PHY07", "The work function phi of a metallic emitter represents:", "The maximum energy an electron can have", "The minimum energy required to eject an electron from the surface", "The thermal kinetic energy at 0 Kelvin", "The energy released during electron capture", "B", "Work function is the binding energy barrier holding conduction electrons within the cathode metal."),
                ("TOP-PHY07", "Einstein's photoelectric equation states that K_max equals:", "h*nu + phi", "h*nu - phi", "phi - h*nu", "h*nu / phi", "B", "Conservation of energy dictates: h*nu = phi + K_max, so K_max = h*nu - phi."),
                ("TOP-PHY08", "According to Bohr's postulate, electrons orbit the nucleus in stationary orbits where orbital angular momentum is:", "Integral multiple of h / (2*pi)", "Any arbitrary real number", "Proportional to velocity squared", "Inversely proportional to Planck's constant", "A", "Bohr quantization condition: L = m*v*r = n*h / (2*pi)."),
                ("TOP-PHY08", "The radius of the nth Bohr orbit in a hydrogen-like atom varies as:", "n", "n^2", "1/n", "1/n^2", "B", "Radius r_n = (n^2 * h^2 * epsilon_0) / (pi * m * e^2) proportional to n^2."),
                ("TOP-PHY08", "When an electron transitions from n = 3 to n = 2 in atomic hydrogen, the emitted photon belongs to the:", "Lyman series", "Balmer series", "Paschen series", "Brackett series", "B", "Transitions ending on principal quantum level n = 2 form the visible Balmer series."),
                ("TOP-PHY09", "In nuclear fission of Uranium-235 by thermal neutrons, the average number of prompt neutrons released per event is roughly:", "0", "1.0", "2.5", "10.0", "C", "On average, 2.4 to 2.5 fast neutrons are released per fission of U-235, enabling chain reactions."),
                ("TOP-PHY09", "Mass defect Delta m in a nucleus accounts for:", "Electrostatic repulsion energy", "The nuclear binding energy holding nucleons together", "Gravitational self-energy", "Beta decay neutrino loss", "B", "By Einstein's mass-energy relation E_b = Delta m * c^2, mass defect manifests as binding energy."),
                ("TOP-PHY07", "The stopping potential in a photoelectric experiment depends strictly on:", "Target distance and area", "Frequency of incident radiation and cathode material", "Illumination time", "Cathode thickness", "B", "e * V_s = h*nu - phi, so stopping potential depends on incident frequency and cathode work function."),
                ("TOP-PHY09", "Which moderator material is commonly utilized in thermal nuclear reactors to slow down neutrons?", "Boron steel", "Heavy water (D2O)", "Lead", "Cadmium", "B", "Heavy water and graphite are light non-absorbing nuclei ideal for thermalizing fast neutrons.")
            ],
            "QZ-CHM01": [
                ("TOP-CHM01", "Lattice energy of an ionic solid is directly proportional to:", "Product of ionic charges and inversely proportional to internuclear distance", "Sum of ionic radii only", "Electronegativity difference squared", "Atomic mass of the cation", "A", "Born-Lande equation shows lattice energy U proportional to (q1 * q2) / r0."),
                ("TOP-CHM01", "Which of the following compounds exhibits the highest ionic lattice energy?", "NaCl", "MgO", "CsCl", "KBr", "B", "Mg2+ and O2- possess +2/-2 charges and small ionic radii, yielding vastly higher lattice energy than singly charged salts."),
                ("TOP-CHM02", "What is the hybridization and geometric shape of the central carbon in methane (CH4)?", "sp2, Trigonal planar", "sp3, Tetrahedral", "sp, Linear", "dsp2, Square planar", "B", "Methane has 4 bonding pairs and 0 lone pairs around carbon, adopting sp3 hybridization with 109.5 degree angles."),
                ("TOP-CHM02", "The bond order in an oxygen molecule (O2) calculated from Molecular Orbital Theory is:", "1", "2", "2.5", "3", "B", "O2 has 10 bonding electrons and 6 antibonding electrons: Bond Order = (10 - 6) / 2 = 2."),
                ("TOP-CHM02", "According to Molecular Orbital Theory, the paramagnetism of O2 is attributed to:", "Unpaired electrons in bonding sigma orbitals", "Two unpaired electrons in degenerate pi* antibonding orbitals", "Lone pairs on oxygen atoms", "Empty pi orbitals", "B", "O2 has two degenerate pi*2px and pi*2py antibonding orbitals containing one unpaired electron each according to Hund's rule."),
                ("TOP-CHM03", "Which diatomic species has a bond order of 3 and is diamagnetic?", "O2+", "N2", "NO", "C2", "B", "N2 has 10 valence electrons in bonding MOs and 4 in antibonding: Bond order = (10 - 4)/2 = 3 with zero unpaired electrons."),
                ("TOP-CHM02", "In ethylene (C2H4), the carbon atoms exhibit which hybridization?", "sp", "sp2", "sp3", "sp3d", "B", "Each carbon in ethylene forms three sigma bonds (trigonal planar) and one unhybridized p orbital forming a pi bond, hence sp2."),
                ("TOP-CHM01", "Fajans' rules predict increased covalent character in an ionic bond when:", "Cation is small and highly charged with a large anion", "Both cation and anion are exceptionally large", "Cation charge is +1 with noble gas core", "Lattice energy is minimal", "A", "High polarizing power (small, highly charged cation) distorting a polarizable large anion induces covalency."),
                ("TOP-CHM02", "The bond angle in a water molecule (H2O) is approximately 104.5 degrees rather than the ideal 109.5 due to:", "Sigma-pi resonance", "Lone pair - lone pair repulsion being greater than bond pair - bond pair repulsion", "Hydrogen bonding in gas phase", "Electronegativity of hydrogen", "B", "VSEPR theory explains that lone pairs exert greater electrostatic repulsion, compressing the H-O-H bond angle."),
                ("TOP-CHM03", "A molecule with zero net dipole moment despite possessing polar bonds is:", "H2O", "NH3", "BF3", "SO2", "C", "BF3 is trigonal planar (sp2); the three identical B-F bond dipoles sum to zero symmetrically.")
            ],
            "QZ-CHM02": [
                ("TOP-CHM04", "The first law of thermodynamics is mathematically stated as:", "Delta U = q + w", "Delta G = Delta H - T*Delta S", "Delta S_univ >= 0", "q = C_p * Delta T", "A", "Internal energy change Delta U equals heat supplied q plus work done on the system w."),
                ("TOP-CHM04", "For an isothermal expansion of an ideal gas into a vacuum (free expansion), the work done w is:", "Positive", "Negative", "Zero", "Dependent on gas pressure", "C", "Expansion against zero opposing external pressure (P_ext = 0) performs zero work: w = -P_ext * Delta V = 0."),
                ("TOP-CHM05", "The standard entropy change Delta S_system for the condensation of steam to liquid water is:", "Positive", "Negative", "Zero", "Indeterminate without temperature", "B", "Gas molecules possess far higher configurational disorder than liquid; transition to liquid decreases system entropy."),
                ("TOP-CHM05", "The second law of thermodynamics establishes that for any spontaneous real process, the total entropy of the universe:", "Remains constant", "Decreases strictly", "Increases strictly (Delta S_univ > 0)", "Oscillates about equilibrium", "C", "Spontaneous processes invariably generate net positive universal entropy."),
                ("TOP-CHM06", "A chemical reaction is guaranteed to be spontaneous at all temperatures if:", "Delta H < 0 and Delta S > 0", "Delta H > 0 and Delta S < 0", "Delta H > 0 and Delta S > 0", "Delta H < 0 and Delta S < 0", "A", "In Delta G = Delta H - T*Delta S, if Delta H is negative and -T*Delta S is negative, Delta G is negative at all T."),
                ("TOP-CHM06", "At dynamic chemical equilibrium under constant temperature and pressure, the Gibbs free energy change Delta G is:", "Maximum positive", "Zero", "Equal to standard enthalpy", "Negative infinity", "B", "Equilibrium represents the minimum in the free energy curve where Delta G = 0."),
                ("TOP-CHM04", "Hess's Law states that total enthalpy change during a reaction is:", "Dependent on the reaction pathway", "Independent of the pathway and depends only on initial and final states", "Equal to temperature times entropy", "Inversely proportional to moles reacted", "B", "Enthalpy is a state function; enthalpy change depends solely on initial reactants and final products."),
                ("TOP-CHM05", "Which of the following substances has absolute entropy S = 0 at 0 Kelvin according to the Third Law of Thermodynamics?", "A perfectly ordered crystalline pure solid", "Liquid helium II", "Gaseous hydrogen", "An amorphous glass", "A", "The Third Law asserts entropy of a perfect pure crystal approaches zero as temperature reaches absolute zero."),
                ("TOP-CHM06", "The relationship between standard Gibbs free energy Delta G_circ and equilibrium constant K_eq is:", "Delta G_circ = -R * T * ln(K_eq)", "Delta G_circ = R * T * K_eq", "K_eq = Delta G_circ / (R*T)", "Delta G_circ = ln(K_eq) / (R*T)", "A", "Thermodynamic equilibrium constant relates to standard free energy via Delta G_circ = -R * T * ln(K_eq)."),
                ("TOP-CHM04", "Standard enthalpy of formation Delta H_f_circ is defined as zero at 298 K for:", "H2O(l)", "O2(g) in its standard state", "CO2(g)", "NO(g)", "B", "By convention, pure elements in their most stable thermodynamic allotrope at 298 K have Delta H_f_circ = 0.")
            ],
            "QZ-CHM03": [
                ("TOP-CHM07", "The IUPAC name of (CH3)2CH-CH2-CH3 is:", "2-Methylbutane", "Isopentane", "3-Methylbutane", "Pentane", "A", "Longest continuous carbon chain is 4 carbons (butane) with a methyl substituent at carbon-2."),
                ("TOP-CHM07", "Which pair of molecules represents constitutional (structural) isomers?", "But-1-ene and But-2-ene", "cis-But-2-ene and trans-But-2-ene", "D-Lactic acid and L-Lactic acid", "Ethene and Ethane", "A", "But-1-ene and But-2-ene share the formula C4H8 but differ in the connectivity/position of the double bond."),
                ("TOP-CHM08", "Primary alcohols on controlled catalytic oxidation using Pyridinium Chlorochromate (PCC) yield:", "Carboxylic acids", "Aldehydes", "Ketones", "Alkenes", "B", "PCC in anhydrous CH2Cl2 selectively oxidizes primary alcohols to aldehydes without over-oxidation to carboxylic acids."),
                ("TOP-CHM08", "The boiling point of ethanol (CH3CH2OH) is significantly higher than dimethyl ether (CH3OCH3) primarily due to:", "Higher molecular weight", "Intermolecular hydrogen bonding", "Dipole-induced dipole forces", "Strong covalent bonds inside the molecule", "B", "The polar O-H bond enables extensive intermolecular hydrogen bonding among ethanol molecules."),
                ("TOP-CHM09", "The reaction of an aldehyde with Tollens' reagent (ammoniacal silver nitrate) produces:", "A yellow precipitate of lead iodide", "A bright silver mirror on the tube walls", "A deep blue copper complex", "Effervescence of CO2 gas", "B", "Aldehydes reduce Ag+ to metallic silver, forming a classic silver mirror test for aldehydes."),
                ("TOP-CHM09", "Ketones are resistant to mild oxidation because:", "They possess no alpha hydrogens", "Oxidation requires cleaving a relatively inert carbon-carbon sigma bond", "They are highly acidic", "They are shielded by double bonds", "B", "Unlike aldehydes which have a oxidizable C-H bond on the carbonyl carbon, ketones require breaking C-C bonds."),
                ("TOP-CHM07", "Markovnikov's rule predicts that addition of HBr to propene yields primarily:", "1-Bromopropane", "2-Bromopropane", "1,2-Dibromopropane", "Cyclopropane", "B", "The electrophilic H+ adds to the less substituted carbon, producing the more stable secondary carbocation."),
                ("TOP-CHM08", "Phenol is noticeably more acidic than cyclohexanol because:", "Phenol contains an aromatic ring that withdraws electrons via resonance stabilizing the phenoxide anion", "Cyclohexanol has more hydrogen atoms", "Phenol is completely nonpolar", "Phenol cannot form hydrogen bonds", "A", "Delocalization of negative charge into the aromatic pi system stabilizes the conjugate phenoxide base."),
                ("TOP-CHM09", "Nucleophilic addition to a carbonyl carbon is facilitated by:", "The partial positive charge (electrophilicity) on the sp2 carbonyl carbon", "The steric bulk of adjacent alkyl groups", "The basicity of oxygen", "Non-polar solvent interactions", "A", "Electronegative oxygen polarizes the C=O bond, making the carbonyl carbon an electrophilic center."),
                ("TOP-CHM07", "Which catalyst is traditionally utilized in the catalytic hydrogenation of alkenes to alkanes?", "Palladium or Nickel (Pd/C or Ni)", "Aluminum chloride (AlCl3)", "Sulfuric acid (H2SO4)", "Potassium permanganate (KMnO4)", "A", "Finely divided Ni, Pd, or Pt surfaces adsorb H2 and alkenes for heterogeneous addition.")
            ],
            "QZ-MTH01": [
                ("TOP-MTH01", "The limit as x approaches 0 of sin(x) / x is:", "0", "1", "Infinity", "Does not exist", "B", "Standard fundamental trigonometric limit: lim x->0 sin(x)/x = 1."),
                ("TOP-MTH01", "A function f(x) is continuous at x = c if and only if:", "f(c) exists, lim x->c f(x) exists, and lim x->c f(x) = f(c)", "f'(c) exists only", "f(x) is defined on both sides of c", "f(c) > 0", "A", "Continuity requires value existence, two-sided limit existence, and their exact equality."),
                ("TOP-MTH02", "If y = ln(cos(x)), then dy/dx equals:", "1 / cos(x)", "-tan(x)", "tan(x)", "-sin(x)", "B", "By the chain rule: dy/dx = (1/cos(x)) * (-sin(x)) = -tan(x)."),
                ("TOP-MTH02", "The derivative of e^(3x^2) with respect to x is:", "e^(3x^2)", "6x * e^(3x^2)", "3x * e^(3x^2)", "6 * e^(3x)", "B", "Using exponential and chain rules: d/dx(e^u) = e^u * du/dx = e^(3x^2) * (6x)."),
                ("TOP-MTH03", "At an inflection point of a twice-differentiable function y = f(x):", "f'(x) = 0 strictly", "f''(x) = 0 or does not exist, and f''(x) changes sign", "f(x) must be zero", "The function attains an absolute global maximum", "B", "Inflection points correspond to curvature changes where concavity reverses sign."),
                ("TOP-MTH03", "A rectangle has fixed perimeter 40 cm. The dimensions that maximize its area are:", "Length 15 cm, Width 5 cm", "Length 10 cm, Width 10 cm (a square)", "Length 12 cm, Width 8 cm", "Length 19 cm, Width 1 cm", "B", "P = 2(x+y)=40 => y = 20-x. Area A = x(20-x) = 20x - x^2. dA/dx = 20 - 2x = 0 => x = 10, y = 10."),
                ("TOP-MTH02", "If x^2 + y^2 = 25, the slope of the tangent line at point (3, 4) is:", "-3/4", "3/4", "-4/3", "4/3", "A", "Implicit differentiation: 2x + 2y(dy/dx) = 0 => dy/dx = -x/y. At (3,4), slope = -3/4."),
                ("TOP-MTH01", "The limit as x approaches infinity of (3x^2 + 5x) / (2x^2 - 7) is:", "0", "3/2", "5/2", "Infinity", "B", "Divide numerator and denominator by highest power x^2: limit evaluates to 3/2."),
                ("TOP-MTH03", "By the Mean Value Theorem, for f(x) = x^2 on [0, 2], the point c where f'(c) equals the average rate of change is:", "0.5", "1.0", "1.5", "2.0", "B", "Average rate = (4 - 0)/(2 - 0) = 2. f'(c) = 2c = 2 => c = 1.0."),
                ("TOP-MTH02", "What is the derivative of arcsin(x) with respect to x?", "1 / (1 + x^2)", "1 / sqrt(1 - x^2)", "-1 / sqrt(1 - x^2)", "1 / (x * sqrt(x^2 - 1))", "B", "Standard inverse trigonometric derivative: d/dx(arcsin x) = 1/sqrt(1 - x^2).")
            ],
            "QZ-MTH02": [
                ("TOP-MTH04", "The indefinite integral of (3x^2 + 4x - 5) dx is:", "x^3 + 2x^2 - 5x + C", "6x + 4 + C", "3x^3 + 4x^2 - 5x + C", "x^3 + 4x^2 - 5 + C", "A", "Integrate term by term: 3(x^3/3) + 4(x^2/2) - 5x + C = x^3 + 2x^2 - 5x + C."),
                ("TOP-MTH04", "Using substitution u = x^2 + 1, the integral of 2x * sqrt(x^2 + 1) dx is:", "(2/3)*(x^2 + 1)^(3/2) + C", "(1/2)*(x^2 + 1)^(3/2) + C", "sqrt(x^2 + 1) + C", "(x^2 + 1)^2 + C", "A", "Integral of sqrt(u) du = (2/3)*u^(3/2) + C = (2/3)*(x^2 + 1)^(3/2) + C."),
                ("TOP-MTH05", "The definite integral of cos(x) dx evaluated from 0 to pi/2 is:", "0", "1", "-1", "pi/2", "B", "[sin(x)] from 0 to pi/2 = sin(pi/2) - sin(0) = 1 - 0 = 1."),
                ("TOP-MTH05", "The area bounded by the curve y = x^2 and the line y = 4 in the first quadrant is:", "8/3", "16/3", "4", "16", "B", "Integral from 0 to 2 of (4 - x^2) dx = [4x - x^3/3] from 0 to 2 = 8 - 8/3 = 16/3."),
                ("TOP-MTH06", "The general solution to the first-order separable differential equation dy/dx = 2xy is:", "y = C * e^(x^2)", "y = x^2 + C", "y = C * e^(2x)", "y = ln(x^2) + C", "A", "dy/y = 2x dx => ln|y| = x^2 + C1 => y = C * e^(x^2)."),
                ("TOP-MTH04", "Integration by parts formula is formulated as:", "Integral u dv = u*v - Integral v du", "Integral u dv = u*v + Integral v du", "Integral u dv = u'*v - u*v'", "Integral u dv = (u*v) / 2", "A", "Product rule integration: integral u dv = uv - integral v du."),
                ("TOP-MTH05", "If f(x) is an odd continuous function on [-a, a], the value of Integral from -a to a of f(x) dx is:", "2 * Integral from 0 to a of f(x) dx", "0", "f(a) - f(-a)", "a^2", "B", "Symmetry dictates the integral of any odd function over symmetric bounds [-a, a] is zero."),
                ("TOP-MTH06", "The order and degree of the differential equation (d^2y/dx^2)^3 + dy/dx + y = 0 are:", "Order 3, Degree 2", "Order 2, Degree 3", "Order 2, Degree 1", "Order 1, Degree 3", "B", "Highest derivative is 2nd order (d^2y/dx^2) raised to power 3, so order 2, degree 3."),
                ("TOP-MTH04", "The integral of 1 / (1 + x^2) dx is:", "ln(1 + x^2) + C", "arctan(x) + C", "arcsin(x) + C", "-1 / (1 + x)^2 + C", "B", "Standard integral evaluates to arctan(x) + C."),
                ("TOP-MTH05", "The average value of f(x) = 2x on the interval [0, 4] is:", "2", "4", "8", "16", "B", "Average = 1/(4-0) * Integral from 0 to 4 of 2x dx = 1/4 * [x^2] from 0 to 4 = 1/4 * 16 = 4.")
            ],
            "QZ-BIO01": [
                ("TOP-BIO01", "The fluid mosaic model of cell membrane structure proposes that membranes consist of:", "A rigid protein sheet sandwiching lipids", "A phospholipid bilayer with embedded floating proteins", "Pure carbohydrate meshes", "Monolayers of nucleic acids", "B", "Singer and Nicolson described the membrane as a dynamic 2D fluid lipid bilayer with mobile proteins."),
                ("TOP-BIO01", "Active transport across a biological membrane differs from passive diffusion in that it:", "Requires metabolic ATP and moves solutes against concentration gradients", "Always moves water molecules only", "Does not utilize carrier proteins", "Follows the natural thermodynamic gradient passively", "A", "Active transport pumps solutes uphill against chemical gradients using metabolic energy (ATP)."),
                ("TOP-BIO02", "Which organelle is recognized as the primary site of aerobic cellular respiration and ATP synthesis?", "Golgi apparatus", "Mitochondria", "Lysosome", "Peroxisome", "B", "Mitochondria host the Krebs cycle and oxidative phosphorylation electron transport chain generating ATP."),
                ("TOP-BIO02", "Ribosomes are subcellular cellular complexes composed of:", "Lipids and steroids", "Ribosomal RNA (rRNA) and proteins", "Deoxyribonucleic acid only", "Glycoproteins and cellulose", "B", "Ribosomes consist of large and small ribonucleoprotein subunits synthesizing polypeptides."),
                ("TOP-BIO03", "During which stage of mitosis do sister chromatids disjoin and migrate to opposite spindle poles?", "Prophase", "Metaphase", "Anaphase", "Telophase", "C", "Anaphase commences with centromere cleavage, allowing microtubules to draw daughter chromosomes apart."),
                ("TOP-BIO03", "The primary checkpoint verifying DNA integrity prior to entering the mitotic phase occurs at:", "G1/S transition", "G2/M boundary", "Metaphase/Anaphase", "Cytokinesis", "B", "The G2/M checkpoint ensures DNA replication is complete and undamaged before triggering mitosis."),
                ("TOP-BIO01", "Plant cell walls achieve mechanical rigidity primarily through interwoven fibers of:", "Chitin", "Cellulose", "Glycogen", "Keratin", "B", "Cellulose microfibrils provide tensile strength against internal turgor pressure."),
                ("TOP-BIO02", "Lysosomes contain high concentrations of:", "Acid hydrolase enzymes active at low pH", "Photosynthetic pigments", "Histone storage proteins", "DNA polymerases", "A", "Lysosomes are acidic digestive compartments containing acid hydrolases for degrading macromolecules."),
                ("TOP-BIO03", "Cytokinesis in higher plant cells is achieved via the formation of a:", "Cleavage furrow", "Cell plate arising from fused Golgi vesicles", "Contractile actomyosin ring", "Nuclear pore complex", "B", "Plant cell walls prevent furrowing; Golgi vesicles coalesce at the phragmoplast to form a cell plate."),
                ("TOP-BIO01", "Facilitated diffusion of glucose across erythrocyte membranes occurs via:", "Simple dissolution across lipids", "Carrier/channel proteins without metabolic energy expenditure", "ATP-hydrolyzing pumps", "Pinocytosis vesicles", "B", "GLUT uniporters facilitate downhill passive transport without requiring ATP.")
            ],
            "QZ-BIO02": [
                ("TOP-BIO04", "According to Mendel's Law of Segregation, the two alleles for a heritable trait:", "Fuse irreversibly in the F1 hybrid", "Separate during gamete formation so each gamete carries only one allele", "Are always co-expressed equally", "Mutate during meiosis", "B", "Segregation ensures homologous chromosomes part during meiosis, placing one allele in each haploid gamete."),
                ("TOP-BIO04", "In a monohybrid cross between two heterozygous individuals (Aa x Aa), the expected phenotypic ratio under complete dominance is:", "1:2:1", "3:1", "9:3:3:1", "1:1", "B", "Genotypes 1 AA : 2 Aa : 1 aa produce 3 dominant phenotypes to 1 recessive phenotype."),
                ("TOP-BIO05", "The enzyme responsible for unwinding the double helix at the DNA replication fork is:", "DNA Ligase", "DNA Helicase", "RNA Polymerase", "Topoisomerase", "B", "Helicase breaks hydrogen bonds holding complementary base pairs together to open the replication fork."),
                ("TOP-BIO05", "On the lagging DNA strand during replication, synthesis proceeds discontinuously creating:", "Okazaki fragments", "Promoter sequences", "Centromeric repeats", "Introns", "A", "Because DNA polymerase only synthesizes 5' to 3', the lagging strand is laid down in discrete Okazaki fragments."),
                ("TOP-BIO06", "The central dogma of molecular biology outlines the directional flow of genetic information as:", "Protein -> RNA -> DNA", "DNA -> RNA -> Protein", "RNA -> DNA -> Protein", "Lipid -> Protein -> RNA", "B", "Crick's dogma details transcription of DNA to RNA followed by ribosomal translation to polypeptide."),
                ("TOP-BIO06", "During transcription in eukaryotes, the enzyme synthesizing mRNA from a DNA template is:", "DNA Polymerase III", "RNA Polymerase II", "Reverse Transcriptase", "Peptidyl transferase", "B", "RNA Polymerase II is dedicated to transcribing protein-coding messenger RNAs in eukaryotic nuclei."),
                ("TOP-BIO05", "According to Chargaff's rules for double-stranded DNA:", "A + G = T + C (purines equal pyrimidines)", "A = G and T = C", "A + T = G + C always", "Purines exceed pyrimidines by 50%", "A", "Complementary pairing (A-T and G-C) mandates the sum of purines equals pyrimidines."),
                ("TOP-BIO06", "A transfer RNA (tRNA) molecule recognizes the codon on mRNA using its complementary triplet termed:", "Operon", "Anticodon", "Promoter", "Enhancer", "B", "The tRNA anticodon loop base-pairs antiparallel to the mRNA codon during ribosomal translation."),
                ("TOP-BIO04", "Phenotypic expression where both alleles are simultaneously and fully expressed in a heterozygote (e.g., AB blood type) is called:", "Incomplete dominance", "Codominance", "Pleiotropy", "Polygenic inheritance", "B", "Codominance displays both maternal and paternal alleles distinctly without blending."),
                ("TOP-BIO06", "The universal start codon signaling the initiation of translation is:", "UAA", "AUG (coding for Methionine)", "UGA", "UAG", "B", "AUG serves as the universal translation initiation codon encoding methionine in eukaryotes.")
            ]
        }
        
        for qz_id, questions in question_templates.items():
            for idx, (top_id, q_text, opt_a, opt_b, opt_c, opt_d, cor_opt, expl) in enumerate(questions):
                q_id = f"Q-{qz_id[3:]}-{idx+1:02d}"
                conn.execute(
                    """
                    INSERT INTO questions (
                        question_id, quiz_id, topic_id, question_text,
                        option_a, option_b, option_c, option_d,
                        correct_option, explanation, difficulty
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Medium')
                    """,
                    (q_id, qz_id, top_id, q_text, opt_a, opt_b, opt_c, opt_d, cor_opt, expl)
                )

        # 8. Seed Realistic Attempts & Student Alex Morgan's Flagged Pattern!
        # Specification scenario:
        # Student Alex Morgan (STU-101) took Physics Quiz 1 (QZ-PHY01).
        # Overall score: 82% (passed, looks fine on the surface!).
        # BUT on "Kirchhoff's Laws" (TOP-PHY01), Alex repeatedly failed:
        # 5 repeated mistakes, 3 attempts, response time high (47.5s vs 22s baseline),
        # and 4 confidence mismatches ("Very Confident" on wrong answers!).
        
        # 8a. Baseline attempts for Alex across other quizzes to establish baseline response time (approx 21-22 seconds)
        alex_id = "STU-101"
        
        # Physics Quiz 1 attempt for Alex
        attempt_id_alex = "ATT-ALEX-PHY01"
        conn.execute(
            "INSERT INTO quiz_attempts (attempt_id, quiz_id, student_id, start_time, end_time, score, completed) VALUES (?, 'QZ-PHY01', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 82.0, 1)",
            (attempt_id_alex, alex_id)
        )
        
        # Questions in QZ-PHY01:
        # Q-PHY01-01 to Q-PHY01-05 are TOP-PHY01 (Kirchhoff's Laws)
        # Q-PHY01-06 to Q-PHY01-10 are TOP-PHY02 & TOP-PHY03
        
        # Alex answered Q-PHY01-06 through Q-PHY01-10 correctly with normal response times (18-22s) and 'Confident'
        for q_num in range(6, 11):
            q_id = f"Q-PHY01-{q_num:02d}"
            # Fetch correct answer
            q_row = conn.execute("SELECT correct_option FROM questions WHERE question_id = ?", (q_id,)).fetchone()
            c_opt = q_row["correct_option"] if q_row else "B"
            conn.execute(
                """
                INSERT INTO question_attempts (id, attempt_id, student_id, question_id, selected_option, is_correct, response_time, confidence_level, attempt_number)
                VALUES (?, ?, ?, ?, ?, 1, 20.5, 'Confident', 1)
                """,
                (f"QA-ALEX-{q_num}", attempt_id_alex, alex_id, q_id, c_opt)
            )
            
        # Alex answered Q-PHY01-01 through Q-PHY01-05 (Kirchhoff's Laws) with repeated errors, high response time (45-50s), and 'Very Confident' (Confidence mismatch!)
        # We record multiple attempts on these questions to reflect 5 errors and 3 attempts
        kirchhoff_attempts = [
            ("Q-PHY01-01", "A", 0, 48.0, "Very Confident", 1), # Incorrect (Correct is B)
            ("Q-PHY01-01", "C", 0, 45.0, "Very Confident", 2), # Repeated attempt, still wrong!
            ("Q-PHY01-02", "A", 0, 49.5, "Very Confident", 1), # Incorrect (Correct is B)
            ("Q-PHY01-03", "A", 0, 46.0, "Confident", 1),      # Incorrect (Correct is B)
            ("Q-PHY01-04", "A", 0, 47.0, "Very Confident", 1), # Incorrect (Correct is B)
        ]
        for idx, (qid, sel_opt, is_cor, r_time, conf, att_no) in enumerate(kirchhoff_attempts):
            conn.execute(
                """
                INSERT INTO question_attempts (id, attempt_id, student_id, question_id, selected_option, is_correct, response_time, confidence_level, attempt_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (f"QA-ALEX-K{idx+1}", attempt_id_alex, alex_id, qid, sel_opt, is_cor, r_time, conf, att_no)
            )
            
        # 8b. Priya Sharma (STU-102) completed Chemistry Quiz and completed an intervention
        priya_id = "STU-102"
        attempt_id_priya = "ATT-PRIYA-CHM01"
        conn.execute(
            "INSERT INTO quiz_attempts (attempt_id, quiz_id, student_id, start_time, end_time, score, completed) VALUES (?, 'QZ-CHM01', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 78.0, 1)",
            (attempt_id_priya, priya_id)
        )
        # Record attempts for Priya
        for q_num in range(1, 11):
            q_id = f"Q-CHM01-{q_num:02d}"
            q_row = conn.execute("SELECT correct_option FROM questions WHERE question_id = ?", (q_id,)).fetchone()
            c_opt = q_row["correct_option"] if q_row else "B"
            # 2 errors on Covalent bonding (TOP-CHM02)
            is_cor = 0 if q_num in (3, 4) else 1
            sel = "A" if is_cor == 0 else c_opt
            conf = "Very Confident" if is_cor == 0 else "Confident"
            conn.execute(
                """
                INSERT INTO question_attempts (id, attempt_id, student_id, question_id, selected_option, is_correct, response_time, confidence_level, attempt_number)
                VALUES (?, ?, ?, ?, ?, ?, 24.0, ?, 1)
                """,
                (f"QA-PRIYA-{q_num}", attempt_id_priya, priya_id, q_id, sel, is_cor, conf)
            )

        # 8c. Seed remaining students with normal attempts across other quizzes
        for s_idx in range(3, 11):
            stu_id = f"STU-{100+s_idx}"
            att_id = f"ATT-NORM-{s_idx}"
            score_val = 75.0 + (s_idx % 4) * 5.0
            conn.execute(
                "INSERT INTO quiz_attempts (attempt_id, quiz_id, student_id, start_time, end_time, score, completed) VALUES (?, 'QZ-PHY01', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, 1)",
                (att_id, stu_id, score_val)
            )
            for q_num in range(1, 11):
                q_id = f"Q-PHY01-{q_num:02d}"
                conn.execute(
                    """
                    INSERT INTO question_attempts (id, attempt_id, student_id, question_id, selected_option, is_correct, response_time, confidence_level, attempt_number)
                    VALUES (?, ?, ?, ?, 'B', 1, 22.0, 'Confident', 1)
                    """,
                    (f"QA-NORM-{s_idx}-{q_num}", att_id, stu_id, q_id)
                )

        print("Running Learning Support Signal Engine on seed dataset...")
        
    # Analyze learning signals for seeded students to populate learning_signals table
    analyze_student_learning_signals("STU-101", "QZ-PHY01")
    analyze_student_learning_signals("STU-102", "QZ-CHM01")
    
    # 9. Seed Interventions and Follow-up Results
    with get_db(db_path) as conn:
        # Priya Sharma has a completed intervention with measured improvement!
        # Topic: TOP-CHM02 (Covalent Bonding)
        # Teacher: TCH-02 (Prof. Robert Miller)
        int_id_priya = "INT-PRIYA-001"
        conn.execute(
            """
            INSERT INTO interventions (
                intervention_id, student_id, teacher_id, topic_id,
                intervention_type, teacher_note, status, assigned_at, completed_at
            ) VALUES (?, 'STU-102', 'TCH-02', 'TOP-CHM02', '3-question concept check',
                      'Reviewed hybridization rules and bond angle distortions before the follow-up concept check.',
                      'COMPLETED', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (int_id_priya,)
        )
        
        # Follow-up result: Before 40%, After 80%, Improvement +40%, Status 'Improved'!
        conn.execute(
            """
            INSERT INTO follow_up_results (
                result_id, intervention_id, before_score, after_score, improvement, result_status, completed_at
            ) VALUES ('RES-PRIYA-001', ?, 40.0, 80.0, 40.0, 'Improved', CURRENT_TIMESTAMP)
            """,
            (int_id_priya,)
        )
        
        # Update learning signal status for Priya to RESOLVED
        conn.execute(
            "UPDATE learning_signals SET status = 'RESOLVED' WHERE student_id = 'STU-102' AND topic_id = 'TOP-CHM02'"
        )
        
        # Alex Morgan has an assigned intervention currently active or ready for review
        # Topic: TOP-PHY01 (Kirchhoff's Laws)
        # Teacher: TCH-01 (Dr. Sarah Jenkins)
        int_id_alex = "INT-ALEX-001"
        conn.execute(
            """
            INSERT INTO interventions (
                intervention_id, student_id, teacher_id, topic_id,
                intervention_type, teacher_note, status, assigned_at
            ) VALUES (?, 'STU-101', 'TCH-01', 'TOP-PHY01', 'Concept explanation',
                      'Review Kirchhoffs loop rule sign convention (+IR vs -IR) and junction rule before advanced multi-loop circuit problems.',
                      'ASSIGNED', CURRENT_TIMESTAMP)
            """,
            (int_id_alex,)
        )
        
    print("Seeding completed successfully! Default test password for all demo accounts is 'Password123!' (Admin is 'Admin123!')")

if __name__ == "__main__":
    seed_database()
