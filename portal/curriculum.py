"""
curriculum.py
-------------
Static reference data for the B.E. (CSE) 2025 scheme (Thapar Institute).
Covers all CORE courses from Semester I to VII (before/around elective
selection), the 12 Elective-Focus specialization tracks, the Professional
Elective lists (I-IV) and the Generic Electives.

This is REFERENCE/catalogue data shown in the portal. It is independent of
the ML model (which was trained on a different dataset).
"""

# Each semester: name, credits, and a list of courses.
# course = (code, name, category, "L-T-P", credits)
SEMESTERS = [
    {
        "name": "Semester I", "credits": "18.0",
        "courses": [
            ("UCB009", "Chemistry", "BSC", "3-0-2", "4.0"),
            ("UES103", "Programming for Problem Solving", "ESC", "3-0-2", "4.0"),
            ("UES013", "Electrical & Electronics Engineering", "ESC", "3-1-2", "4.5"),
            ("UEN008", "Energy and Environment", "OTH", "2-0-0", "2.0"),
            ("UMA022", "Calculus for Engineers", "BSC", "3-1-0", "3.5"),
        ],
    },
    {
        "name": "Semester II", "credits": "18.0",
        "courses": [
            ("UPH013", "Physics", "BSC", "3-1-2", "4.5"),
            ("UES101", "Engineering Drawing", "ESC", "2-4-0", "4.0"),
            ("UHU003", "Professional Communication", "HSS", "2-0-2", "3.0"),
            ("UES102", "Manufacturing Processes", "ESC", "2-0-2", "3.0"),
            ("UMA023", "Differential Equations and Linear Algebra", "BSC", "3-1-0", "3.5"),
        ],
    },
    {
        "name": "Semester III", "credits": "24.5",
        "courses": [
            ("UCS303", "Operating System", "PCC", "3-0-2", "4.0"),
            ("UTA018", "Object Oriented Programming", "PCC", "3-0-2", "4.0"),
            ("UCS301", "Data Structures", "PCC", "3-0-2", "4.0"),
            ("UCS405", "Discrete Mathematical Structures", "PCC", "3-1-0", "3.5"),
            ("UTA016", "Engineering Design Project I", "ESC", "1-0-2", "3.0"),
            ("UMA021", "Numerical Linear Algebra", "BSC", "3-0-2", "4.0"),
            ("UHU052", "Evolutionary Basis of Human Behaviour", "HSS", "1-0-0", "1.0"),
            ("UCS320", "Intro to Sustainable Green Computing", "PCC", "1-0-0", "1.0"),
        ],
    },
    {
        "name": "Semester IV", "credits": "24.0",
        "courses": [
            ("UCS415", "Design and Analysis of Algorithms", "PCC", "3-0-2", "4.0"),
            ("UCS310", "Database Management Systems", "PCC", "3-0-2", "4.0"),
            ("UCS414", "Computer Networks", "PCC", "3-0-2", "4.0"),
            ("UCS321", "AI for Engineers", "ESC", "2-0-2", "3.0"),
            ("UMA401", "Probability and Statistics", "BSC", "3-0-2", "4.0"),
            ("UTA024", "Engineering Design Project II", "PCC", "1-0-4", "3.0"),
            ("UTD003", "Aptitude Skills Building", "HSS", "2-0-0", "2.0"),
        ],
    },
    {
        "name": "Semester V", "credits": "26.0",
        "courses": [
            ("UML501", "Machine Learning", "PCC", "3-0-2", "4.0"),
            ("UCS420", "Cognitive Computing", "PCC", "2-0-2", "3.0"),
            ("UCS553", "Enterprise Web Application", "PCC", "3-0-2", "4.0"),
            ("UCS503", "Software Engineering", "PCC", "3-0-2", "4.0"),
            ("UCS510", "Computer Architecture and Organization", "PCC", "3-0-0", "3.0"),
            ("—", "Elective-I (Professional Elective)", "PE", "2-0-2", "3.0"),
            ("—", "Generic Elective", "GE", "2-0-0", "2.0"),
            ("UCS421", "Ethics and Risk Mitigation in AI", "ESC", "3-0-0", "3.0"),
        ],
    },
    {
        "name": "Semester VI", "credits": "23.5",
        "courses": [
            ("UCS701", "Theory of Computation", "CP", "3-1-0", "3.5"),
            ("UMA071", "Optimization Techniques", "CF", "3-0-2", "4.0"),
            ("UCS619", "Quantum Computing", "CP", "3-0-2", "4.0"),
            ("UTA025", "Innovation and Entrepreneurship", "PR", "1-0-2", "3.0"),
            ("—", "Elective-II (Professional Elective)", "PE", "2-0-2", "3.0"),
            ("—", "Elective-III (Professional Elective)", "PE", "2-0-2", "3.0"),
            ("UCS797", "Capstone Project (starts)", "PR", "1-0-2", "—"),
            ("UCSXXX", "Domain Specific Applications / Minor Project", "PCC", "2-0-2", "3.0"),
        ],
    },
    {
        "name": "Semester VII", "credits": "21.0",
        "courses": [
            ("UCS802", "Compiler Construction", "CP", "3-0-2", "4.0"),
            ("UHU005", "Humanities for Engineers", "CF", "2-0-2", "3.0"),
            ("UCS714", "Agentic AI", "PCC", "2-0-2", "3.0"),
            ("—", "Elective-IV (Professional Elective)", "PE", "2-0-2", "3.0"),
            ("UCS797", "Capstone Project", "PR", "0-0-2", "8.0"),
        ],
    },
]

# The 10/12 Elective-Focus (EFB) specialization tracks.
# Each: name, an emoji, and 4 courses (code, name) spread across the EFB slots.
ELECTIVE_FOCUS = [
    {"name": "High Performance Computing", "icon": "⚡", "tag": "Systems",
     "courses": [("UCS531", "Cloud Computing"), ("UCS635", "GPU Computing"),
                 ("UCS645", "Parallel & Distributed Computing"), ("UCS751", "Simulation & Modelling")]},
    {"name": "Computer Animation and Gaming", "icon": "🎮", "tag": "Graphics",
     "courses": [("UCS532", "Computer Vision"), ("UCS636", "3D Modelling and Animation"),
                 ("UCS646", "Game Design & Development"), ("UCS752", "Augmented and Virtual Reality")]},
    {"name": "Information and Cyber Security", "icon": "🔐", "tag": "Security",
     "courses": [("UCS534", "Computer & Network Security"), ("UCS638", "Secure Coding"),
                 ("UCS648", "Cyber Forensics"), ("UCS754", "Blockchain Technology and Applications")]},
    {"name": "Mathematics and Computing", "icon": "📐", "tag": "Maths",
     "courses": [("UMC513", "Linear Algebra for AI & ML"), ("UMC632", "Financial Mathematics"),
                 ("UMC633", "Mathematics for Quantum Computing"), ("UMC744", "Cryptography and Coding Theory")]},
    {"name": "Data Science", "icon": "📊", "tag": "AI/Data",
     "courses": [("UCS548", "Foundation of Data Science"), ("UCS654", "Predictive Analytics using Statistics"),
                 ("UCS761", "Deep Learning"), ("UCS772", "Data Science: Computer Vision & NLP")]},
    {"name": "Financial Derivative", "icon": "💹", "tag": "Finance",
     "courses": [("UCS539", "Finance, Accounting and Valuation"), ("UCS675", "Financial Markets and Portfolio Theory"),
                 ("UCS658", "Derivatives Pricing, Trading & Strategies"), ("UMC743", "Quantitative & Statistical Methods for Finance")]},
    {"name": "DevOps and Continuous Delivery", "icon": "🔁", "tag": "DevOps",
     "courses": [("UCS537", "Source Code Management"), ("UCS659", "Build and Release Management"),
                 ("UCS660", "Continuous Integration & Deployment"), ("UCS758", "System Provisioning & Config Management")]},
    {"name": "Full Stack", "icon": "🖥️", "tag": "Web",
     "courses": [("UCS542", "UI & UX Specialist"), ("UCS677", "Data Engineering"),
                 ("UCS662", "Test Automation"), ("UCS745", "Cloud & DevOps")]},
    {"name": "Conversational AI", "icon": "🗣️", "tag": "AI/NLP",
     "courses": [("UCS551", "Accelerated Data Science"), ("UCS664", "Natural Language Processing"),
                 ("UCS749", "Speech Processing & Synthesis"), ("UCS748", "Generative AI")]},
    {"name": "Robotics and Edge AI", "icon": "🤖", "tag": "Robotics",
     "courses": [("UCS668", "Edge AI & Robotics: Data Centre Vision"), ("UCS547", "Edge AI & Robotics: Accelerated Data Science"),
                 ("UCS671", "Edge AI & Robotics: Embedded Vision"), ("UCS760", "Edge AI & Robotics: RL & Conversational AI")]},
    {"name": "Cyber Forensics & Ethical Hacking", "icon": "🕵️", "tag": "Security",
     "courses": [("UCS550", "Network Defence"), ("UCS673", "Ethical Hacking-1"),
                 ("UCS674", "Ethical Hacking-2"), ("UCS750", "Computer Hacking & Forensic Investigation")]},
    {"name": "Intelligent Transport Systems", "icon": "🚗", "tag": "ITS",
     "courses": [("UEC646", "Network & Communication for Connected Vehicles"), ("UCS678", "Intelligent Transportation Systems"),
                 ("UCS679", "Data Analytics in Automobile Engineering"), ("UCS762", "Cyber security for Mobility Systems")]},
]

# Professional Elective baskets (students pick one course from each basket).
PROFESSIONAL_ELECTIVES = {
    "Elective I": [
        ("UCS531", "Cloud Computing"), ("UCS532", "Computer Vision"),
        ("UCS534", "Computer & Network Security"), ("UMC513", "Linear Algebra for AI & ML"),
        ("UCS548", "Foundation of Data Science"), ("UCS539", "Finance, Accounting and Valuation"),
        ("UCS537", "Source Code Management"), ("UCS542", "UI & UX Specialist"),
        ("UCS551", "Conversational AI: Accelerated Data Science"), ("UCS547", "Edge AI & Robotics: Accelerated Data Science"),
        ("UCS550", "Network Defence"), ("UEC646", "Network & Communication for Connected Vehicles"),
    ],
    "Elective II": [
        ("UCS635", "GPU Computing"), ("UCS636", "3D Modelling and Animation"),
        ("UCS638", "Secure Coding"), ("UMC622", "Matrix Computation"),
        ("UCS654", "Predictive Analytics using Statistics"), ("UCS675", "Financial Markets and Portfolio Theory"),
        ("UCS659", "Build and Release Management"), ("UCS661", "Database Engineer"),
        ("UCS664", "Conversational AI: NLP"), ("UCS668", "Edge AI & Robotics: Data Centre Vision"),
        ("UCS673", "Ethical Hacking-1"), ("UCS678", "Intelligent Transportation Systems"),
    ],
    "Elective III": [
        ("UCS645", "Parallel & Distributed Computing"), ("UCS646", "Game Design & Development"),
        ("UCS648", "Cyber Forensics"), ("UMC633", "Mathematics for Quantum Computing"),
        ("UCS761", "Deep Learning"), ("UCS658", "Derivatives Pricing, Trading & Strategies"),
        ("UCS660", "Continuous Integration & Deployment"), ("UCS662", "Test Automation"),
        ("UCS749", "Conversational AI: Speech Processing & Synthesis"), ("UCS671", "Edge AI & Robotics: Embedded Vision"),
        ("UCS674", "Ethical Hacking-II"), ("UCS679", "Data Analytics in Automobile Engineering"),
    ],
    "Elective IV": [
        ("UCS751", "Simulation & Modelling"), ("UCS752", "Augmented and Virtual Reality"),
        ("UCS754", "Blockchain Technology and Applications"), ("UMC744", "Cryptography and Coding Theory"),
        ("UCS772", "Data Science: Computer Vision & NLP"), ("UMC743", "Quantitative & Statistical Methods for Finance"),
        ("UCS758", "System Provisioning & Config Management"), ("UCS745", "Cloud & DevOps"),
        ("UCS748", "Generative AI"), ("UCS760", "Edge AI & Robotics: RL & Conversational AI"),
        ("UCS750", "Computer Hacking & Forensic Investigation"), ("UCS762", "Cyber security for Mobility Systems"),
    ],
}

GENERIC_ELECTIVES = [
    ("UHU016", "Introductory Course in French"),
    ("UHU017", "Introduction to Cognitive Science"),
    ("UHU018", "Introduction to Corporate Finance"),
    ("UCS002", "Introduction to Cyber Security"),
    ("UPH064", "Nanoscience and Nanomaterials"),
    ("UEN006", "Technologies for Sustainable Development"),
    ("UMA069", "Graph Theory and Applications"),
    ("UBT510", "Biology for Engineers"),
    ("UMA070", "Advanced Numerical Methods"),
    ("UTD004", "Campus 2 Corporate"),
]

# Friendly names for course categories (for a legend).
CATEGORY_NAMES = {
    "BSC": "Basic Science", "ESC": "Engineering Science", "HSS": "Humanities & Social Science",
    "PCC": "Professional Core", "PE": "Professional Elective", "GE": "Generic Elective",
    "OTH": "Other", "CP": "Compulsory (Prof.)", "CF": "Compulsory Foundation", "PR": "Project",
}
