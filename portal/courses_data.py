"""
courses_data.py
---------------
Course catalogue + learning content for the portal's "Courses" hub and the
per-course detail pages. Built on top of curriculum.py (which has the official
scheme) and enriched here with syllabus topics, textbooks and curated free
learning resources.

Any course without rich content still gets a working page with its basic info
plus auto-generated 'search' resources.
"""
import urllib.parse
from curriculum import SEMESTERS, ELECTIVE_FOCUS, CATEGORY_NAMES
from thapar_map import TARGET_INFO


# ---------------------------------------------------------------------------
# Rich content for the most important courses.
# code -> {objective, topics[], textbooks[], resources[]}
# resources: {label, url, icon}
# ---------------------------------------------------------------------------
def _yt(q):
    return {"label": "YouTube lectures", "icon": "🎥",
            "url": "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q)}

def _nptel(q):
    return {"label": "NPTEL / Swayam", "icon": "🎓",
            "url": "https://www.google.com/search?q=" + urllib.parse.quote("NPTEL " + q)}

def _gfg(q):
    return {"label": "GeeksforGeeks", "icon": "📄",
            "url": "https://www.geeksforgeeks.org/?s=" + urllib.parse.quote(q)}

def _link(label, url, icon="🔗"):
    return {"label": label, "url": url, "icon": icon}

def _coursera(q):
    return {"label": "Coursera courses", "icon": "🎓",
            "url": "https://www.coursera.org/search?query=" + urllib.parse.quote(q)}

def _edx(q):
    return {"label": "edX courses", "icon": "🎓",
            "url": "https://www.edx.org/search?q=" + urllib.parse.quote(q)}

def _udemy(q):
    return {"label": "Udemy courses", "icon": "🎓",
            "url": "https://www.udemy.com/courses/search/?q=" + urllib.parse.quote(q)}

def mooc_links(name):
    """Online-course platform search links added to every course."""
    return [_coursera(name), _edx(name), _udemy(name)]


COURSE_CONTENT = {
    "UES103": {
        "objective": "Solve real-world problems using the C programming language.",
        "topics": ["Computer fundamentals & algorithms", "Data types, operators, I/O",
                   "Decision making & loops", "Functions & recursion", "Arrays & strings",
                   "Pointers & dynamic memory", "Structures & unions", "File handling"],
        "textbooks": ["The C Programming Language — Kernighan & Ritchie",
                      "Programming in ANSI C — E. Balagurusamy"],
        "resources": [_yt("C programming full course"), _nptel("Programming in C"),
                      _link("learn-c.org interactive", "https://www.learn-c.org/", "💻")],
    },
    "UCS301": {
        "objective": "Understand data structures and their applications.",
        "topics": ["Algorithm analysis & complexity", "Arrays & strings",
                   "Linked lists (singly/doubly/circular)", "Stacks & queues",
                   "Hash tables", "Trees: BST, AVL, B-Tree", "Heaps & priority queues",
                   "Graphs: BFS/DFS, shortest path, MST"],
        "textbooks": ["Introduction to Algorithms — Cormen (CLRS)",
                      "Data Structures & Algorithms in C++ — Sahni"],
        "resources": [_yt("Abdul Bari data structures"), _gfg("data structures"),
                      _link("VisuAlgo (visualize DS)", "https://visualgo.net/en", "💻")],
    },
    "UTA018": {
        "objective": "Apply object-oriented programming concepts using C++.",
        "topics": ["Classes & objects", "Constructors & destructors",
                   "Inheritance", "Polymorphism (overloading/overriding)",
                   "Virtual functions & abstract classes", "Templates & STL",
                   "Exception handling"],
        "textbooks": ["C++: The Complete Reference — H. Schildt",
                      "Object Oriented Programming with C++ — Balagurusamy"],
        "resources": [_yt("OOP in C++ full course"), _gfg("cpp oops"),
                      _link("learncpp.com", "https://www.learncpp.com/", "📘")],
    },
    "UCS303": {
        "objective": "Understand the role, responsibilities and algorithms of an OS.",
        "topics": ["Processes & threads", "CPU scheduling", "Synchronization & deadlocks",
                   "Memory management & paging", "Virtual memory", "File systems",
                   "Disk scheduling", "Protection & security"],
        "textbooks": ["Operating System Concepts — Silberschatz, Galvin, Gagne",
                      "Operating Systems — W. Stallings"],
        "resources": [_yt("Operating System Gate Smashers"), _nptel("Operating Systems"),
                      _gfg("operating systems")],
    },
    "UCS405": {
        "objective": "Overview of discrete mathematical structures for CS.",
        "topics": ["Sets, relations, functions", "Growth of functions (Big-O)",
                   "Graph theory", "Propositional & predicate logic",
                   "Recurrence relations", "Algebraic structures (groups, rings)",
                   "Number theory & congruences"],
        "textbooks": ["Discrete Mathematics and its Applications — K. Rosen",
                      "Discrete Mathematical Structures — Tremblay & Manohar"],
        "resources": [_yt("Discrete mathematics full course"), _nptel("Discrete Mathematics"),
                      _gfg("discrete mathematics")],
    },
    "UCS310": {
        "objective": "Design databases using E-R modelling, normalization and SQL.",
        "topics": ["DBMS & 3-schema architecture", "Relational model & algebra",
                   "E-R modelling", "Normalization (1NF–BCNF)",
                   "SQL (DDL, DML, joins, sub-queries)", "PL/SQL (triggers, procedures)",
                   "Transactions & concurrency control", "Recovery management"],
        "textbooks": ["Database System Concepts — Silberschatz, Korth, Sudarshan",
                      "Fundamentals of Database Systems — Elmasri & Navathe"],
        "resources": [_yt("DBMS Gate Smashers"), _nptel("Database Management System"),
                      _link("SQLBolt (practice SQL)", "https://sqlbolt.com/", "💻")],
    },
    "UCS414": {
        "objective": "Learn computer networks through layered models.",
        "topics": ["OSI & TCP/IP models", "LAN, Ethernet, MAC protocols",
                   "Error detection & flow control", "Routing (Distance-Vector, Link-State)",
                   "IP addressing & subnetting", "TCP/UDP, congestion control",
                   "DNS, HTTP, email, applications"],
        "textbooks": ["Data Communication and Networking — Forouzan",
                      "Computer Networks — Tanenbaum"],
        "resources": [_yt("Computer Networks full course"), _nptel("Computer Networks"),
                      _link("Kurose & Ross interactive", "https://gaia.cs.umass.edu/kurose_ross/", "📘")],
    },
    "UCS415": {
        "objective": "Design and analyse algorithms for computational problems.",
        "topics": ["Complexity & recurrences", "Divide & conquer", "Greedy algorithms",
                   "Dynamic programming", "Backtracking", "Branch & bound",
                   "Graph algorithms & max-flow", "String matching", "P, NP, NP-complete"],
        "textbooks": ["Introduction to Algorithms — CLRS",
                      "Fundamentals of Computer Algorithms — Horowitz & Sahni"],
        "resources": [_yt("Abdul Bari algorithms"), _nptel("Design and Analysis of Algorithms"),
                      _link("LeetCode (practice)", "https://leetcode.com/", "💻")],
    },
    "UMA401": {
        "objective": "Probability & statistics for CS models and decisions.",
        "topics": ["Descriptive statistics", "Probability & Bayes' theorem",
                   "Random variables & distributions", "Special distributions",
                   "Sampling & Central Limit Theorem", "Estimation",
                   "Hypothesis testing", "Regression & correlation"],
        "textbooks": ["Probability & Statistics for Engineers — Walpole, Myers",
                      "Intro to Probability & Statistics — Rohatgi & Saleh"],
        "resources": [_yt("Probability and statistics full course"),
                      _nptel("Probability and Statistics"), _gfg("probability")],
    },
    "UCS321": {
        "objective": "Foundational AI with practical, engineering-relevant problem solving.",
        "topics": ["AI/ML/DL/RL definitions", "Data & preprocessing",
                   "Supervised learning (regression, trees, RF)",
                   "Unsupervised learning (K-Means, PCA)",
                   "Neural networks (MLP, CNN intro)", "Time-series (ARIMA, LSTM)",
                   "Python toolchain (pandas, scikit-learn)"],
        "textbooks": ["Machine Learning — Tom Mitchell",
                      "Hands-On ML with Scikit-Learn & TensorFlow — A. Géron"],
        "resources": [_yt("AI for everyone"), _nptel("Artificial Intelligence"),
                      _link("Kaggle Learn", "https://www.kaggle.com/learn", "💻")],
    },
    "UML501": {
        "objective": "Broad introduction to machine learning & pattern recognition.",
        "topics": ["ML types & data preprocessing", "Linear & polynomial regression",
                   "Logistic regression & decision trees", "Random forest & Naïve Bayes",
                   "KNN & SVM", "Clustering (K-Means, hierarchical, DBSCAN)",
                   "Association rules (Apriori)", "Artificial neural networks"],
        "textbooks": ["Machine Learning — Tom Mitchell",
                      "Pattern Recognition and ML — C. Bishop"],
        "resources": [_yt("Andrew Ng Machine Learning"), _nptel("Machine Learning"),
                      _link("scikit-learn docs", "https://scikit-learn.org/stable/", "📘")],
    },
    "UCS503": {
        "objective": "Plan and manage large-scale software; learn modern SE trends.",
        "topics": ["Software process models", "Requirements engineering & SRS",
                   "Design principles (coupling/cohesion, MVC)",
                   "UML modelling", "Testing (black/white box, V&V)",
                   "Agile, Scrum, XP", "Project management (scope, cost)"],
        "textbooks": ["Software Engineering: A Practitioner's Approach — Pressman",
                      "Software Engineering — I. Sommerville"],
        "resources": [_yt("Software engineering full course"), _nptel("Software Engineering"),
                      _gfg("software engineering")],
    },
    "UCS510": {
        "objective": "Architecture & organization of the basic computer modules.",
        "topics": ["Number systems & logic gates", "Register transfer & micro-ops",
                   "Basic computer organization", "CPU & addressing modes",
                   "Pipelining & computer arithmetic", "Memory hierarchy & cache",
                   "I/O organization & multiprocessors"],
        "textbooks": ["Computer System Architecture — M. Morris Mano",
                      "Computer Organization and Architecture — W. Stallings"],
        "resources": [_yt("Computer Organization Gate Smashers"),
                      _nptel("Computer Architecture"), _gfg("computer organization")],
    },
    "UCS701": {
        "objective": "Formal methods of computation; computability & complexity.",
        "topics": ["Regular languages & finite automata", "Regular expressions, DFA/NFA",
                   "Pumping lemma", "Context-free grammars & PDA",
                   "Chomsky/Greibach normal forms", "Turing machines",
                   "Halting problem & decidability"],
        "textbooks": ["Intro to Automata Theory — Hopcroft, Ullman, Motwani",
                      "Intro to the Theory of Computation — M. Sipser"],
        "resources": [_yt("Theory of computation full course"),
                      _nptel("Theory of Computation"), _gfg("theory of computation")],
    },
    "UCS802": {
        "objective": "Work through the major phases of compilation.",
        "topics": ["Phases of a compiler", "Lexical analysis (LEX/Flex)",
                   "Syntax analysis (LL, LR parsers, YACC)", "Error handling",
                   "Semantic analysis (attribute grammars)", "Run-time environment",
                   "Code generation", "Code optimization"],
        "textbooks": ["Compilers: Principles, Techniques & Tools — Aho, Ullman (Dragon Book)",
                      "Lex and Yacc — Levine, Mason, Brown"],
        "resources": [_yt("Compiler design full course"), _nptel("Compiler Design"),
                      _gfg("compiler design")],
    },
    "UCS714": {
        "objective": "Design and deploy Agentic AI and multi-agent systems.",
        "topics": ["Generative AI & LLM foundations", "Prompt engineering (CoT, ReAct)",
                   "Agent architectures & design patterns", "Tool-use & planning agents",
                   "Multi-agent collaboration (MCP, A2A)", "Workflow orchestration (n8n)",
                   "Evaluation & governance of agents"],
        "textbooks": ["Multi-Agent Systems — Shoham & Leyton-Brown",
                      "Mastering AI Agents — Elbert Gale"],
        "resources": [_yt("Build AI agents tutorial"),
                      _link("LangChain docs", "https://python.langchain.com/", "📘"),
                      _link("Anthropic — Building effective agents",
                            "https://www.anthropic.com/research/building-effective-agents", "📄")],
    },
    "UCS553": {
        "objective": "Build modular, database-driven applications with Java / web stack.",
        "topics": ["Java foundations & OOP", "Exceptions, collections, generics",
                   "File handling & serialization", "JDBC & DAO pattern",
                   "JavaFX UI & events", "Mini-project development"],
        "textbooks": ["Java: The Complete Reference — H. Schildt",
                      "Head First Java — Sierra & Bates"],
        "resources": [_yt("Java full course"), _link("Oracle Java docs",
                      "https://docs.oracle.com/en/java/", "📘"), _gfg("java")],
    },
    "UCS420": {
        "objective": "Build computational models of human cognition.",
        "topics": ["Computational modelling & neural nets", "Model optimization",
                   "Reasoning & learning (Bayesian, CBR)", "Computational linguistics",
                   "Advanced analytics", "IBM Watson / Deep QA"],
        "textbooks": ["Cognitive Computing and Big Data Analytics — Judith S. et al."],
        "resources": [_yt("Cognitive computing introduction"), _gfg("cognitive computing")],
    },
    "UCS619": {
        "objective": "Introduction to quantum computation.",
        "topics": ["Linear algebra & qubits", "Quantum gates & circuits",
                   "Quantum algorithms (Deutsch, Grover, Shor)",
                   "Quantum Fourier transform", "Quantum cryptography (BB84)",
                   "Quantum error correction"],
        "textbooks": ["Quantum Computation and Quantum Information — Nielsen & Chuang"],
        "resources": [_yt("Quantum computing for beginners"),
                      _link("IBM Qiskit textbook", "https://qiskit.org/learn/", "📘")],
    },
    # ------- Electives (the ones the recommender predicts) ----------------
    "UCS548": {
        "objective": "Foundations of data science & its applications.",
        "topics": ["Data science process", "R & RStudio basics",
                   "Data cleaning & summarization", "Data visualization",
                   "Correlation & regression", "Clustering & PCA"],
        "textbooks": ["Data Mining: Concepts and Techniques — Han, Kamber, Pei"],
        "resources": [_yt("Data science full course"),
                      _link("Coursera — IBM Data Science Certificate",
                            "https://www.coursera.org/professional-certificates/ibm-data-science", "🎓"),
                      _link("Kaggle Learn", "https://www.kaggle.com/learn", "💻")],
    },
    "UCS761": {
        "objective": "Build intelligent machines with deep learning.",
        "topics": ["Artificial neural networks & backprop", "CNN architectures",
                   "Regularization & dropout", "RNN, LSTM, attention & transformers",
                   "Autoencoders & GANs"],
        "textbooks": ["Deep Learning — Goodfellow, Bengio, Courville"],
        "resources": [_yt("Deep learning specialization"),
                      _link("Coursera — Deep Learning Specialization (Andrew Ng)",
                            "https://www.coursera.org/specializations/deep-learning", "🎓"),
                      _link("PyTorch tutorials", "https://pytorch.org/tutorials/", "📘")],
    },
    "UCS534": {
        "objective": "Computer & network security technologies and tools.",
        "topics": ["Security attacks & malware", "Set-UID & buffer overflow",
                   "Packet sniffing & spoofing", "Firewalls & IPTables",
                   "ARP/DNS poisoning", "PKI & TLS"],
        "textbooks": ["Network Security Essentials — W. Stallings",
                      "Computer Security: A Hands-on Approach — Wenliang Du"],
        "resources": [_yt("Network security full course"),
                      _link("OWASP", "https://owasp.org/", "📄")],
    },
    "UCS531": {
        "objective": "Cloud infrastructure, services and virtualization.",
        "topics": ["Cloud paradigms & XaaS", "AWS (EC2, S3, SQS)",
                   "Virtualization & VDC", "Hadoop & MapReduce",
                   "Fog/Edge computing", "Cloud sustainability"],
        "textbooks": ["Cloud Computing: Principles and Paradigms — Buyya et al."],
        "resources": [_yt("AWS cloud practitioner full course"),
                      _link("AWS free tier", "https://aws.amazon.com/free/", "☁️")],
    },
    "UCS664": {
        "objective": "Deep learning for natural language processing.",
        "topics": ["NLP basics & linguistics", "Embeddings (Word2Vec, GloVe)",
                   "RNN/GRU/LSTM", "Transformers & BERT",
                   "NLP applications (NER, MT, QA)", "NVIDIA NeMo"],
        "textbooks": ["Speech and Language Processing — Jurafsky & Martin"],
        "resources": [_yt("NLP with transformers"),
                      _link("Coursera — NLP Specialization (DeepLearning.AI)",
                            "https://www.coursera.org/specializations/natural-language-processing", "🎓"),
                      _link("Hugging Face course", "https://huggingface.co/learn", "🎓")],
    },
    "UCS748": {
        "objective": "Generative AI with a focus on Large Language Models.",
        "topics": ["Generative AI & tools", "LLMs & transformer architecture",
                   "Text & image generation", "Multi-modal generation",
                   "Prompt engineering"],
        "textbooks": ["Generative Deep Learning — David Foster"],
        "resources": [_yt("Generative AI full course"),
                      _link("Prompt Engineering Guide", "https://www.promptingguide.ai/", "📄")],
    },
    "UCS532": {
        "objective": "Core concepts and applications of computer vision.",
        "topics": ["Image formation & preprocessing", "Features (SIFT, SURF, HOG)",
                   "Image segmentation", "Pattern analysis & PCA",
                   "Motion analysis & optical flow"],
        "textbooks": ["Computer Vision: Algorithms and Applications — R. Szeliski"],
        "resources": [_yt("OpenCV computer vision course"),
                      _link("OpenCV tutorials", "https://docs.opencv.org/", "📘")],
    },
    "UCS646": {
        "objective": "Game design & development with Unity and C#.",
        "topics": ["Game loop & engine components", "Game objects, vectors, physics",
                   "Maths for game engines", "Collision & particle systems",
                   "AR/VR & mobile games", "Unity + C#"],
        "textbooks": ["Game Physics — D. Eberly",
                      "Introduction to Game Design, Prototyping & Development — Bond"],
        "resources": [_yt("Unity beginner tutorial"),
                      _link("Unity Learn", "https://learn.unity.com/", "🎮")],
    },
    "UCS542": {
        "objective": "Front-end web development: HTML, CSS, JS, React, Node.",
        "topics": ["HTML5 & CSS3", "JavaScript & DOM", "React & JSX",
                   "REST APIs", "Node.js basics", "Responsive UI/UX"],
        "textbooks": ["Web Technology: Theory and Practice — M. Srinivasan"],
        "resources": [_yt("Full stack web development"),
                      _link("MDN Web Docs", "https://developer.mozilla.org/", "📘"),
                      _link("freeCodeCamp", "https://www.freecodecamp.org/", "💻")],
    },
    "UCS754": {
        "objective": "Blockchain technology and real-time applications.",
        "topics": ["Cryptography basics & hashing", "Bitcoin & blockchain",
                   "Smart contracts & Ethereum", "Consensus mechanisms",
                   "Blockchain applications"],
        "textbooks": ["Blockchain: Blueprint for a New Economy — M. Swan"],
        "resources": [_yt("Blockchain full course"),
                      _link("Solidity docs", "https://docs.soliditylang.org/", "📘")],
    },
    "UCS645": {
        "objective": "Parallel & distributed computing fundamentals.",
        "topics": ["Parallelism & architectures", "Decomposition & load balancing",
                   "Distributed computing models", "MPI & shared address space",
                   "CUDA programming", "Parallel algorithms"],
        "textbooks": ["Introduction to Parallel Computing — Grama, Gupta, Karypis, Kumar"],
        "resources": [_yt("Parallel computing course"), _nptel("Parallel Computing")],
    },
    "UCS635": {
        "objective": "Modern GPU architecture & CUDA programming.",
        "topics": ["Heterogeneous computing & GPU architecture", "CUDA C data parallelism",
                   "Thread organization", "CUDA memories", "OpenCL & OpenACC"],
        "textbooks": ["CUDA by Example — Sanders & Kandrot",
                      "Programming Massively Parallel Processors — Kirk & Hwu"],
        "resources": [_yt("CUDA programming tutorial"),
                      _link("NVIDIA CUDA docs", "https://docs.nvidia.com/cuda/", "📘")],
    },
    "UCS673": {
        "objective": "Ethical hacking: analyse threats and implement defences.",
        "topics": ["Virtual/cloud/wireless network security", "Traffic & log monitoring",
                   "Incident response & forensics", "Risk management",
                   "System hacking & malware", "Sniffing, social engineering, DoS"],
        "textbooks": ["Certified Network Defender (CNDv2) — EC-Council",
                      "Ethical Hacking and Countermeasures (CEHv12) — EC-Council"],
        "resources": [_yt("Ethical hacking full course"),
                      _link("TryHackMe", "https://tryhackme.com/", "💻")],
    },
    "UCS537": {
        "objective": "DevOps & source code management.",
        "topics": ["Traditional vs Agile", "DevOps & CAMS", "CI/CD basics",
                   "Version control (Git)", "Centralized vs distributed VCS",
                   "Cloud sustainability"],
        "textbooks": ["The DevOps Handbook — Kim, Humble, Debois, Willis",
                      "Pro Git — Chacon & Straub"],
        "resources": [_yt("Git and GitHub for beginners"),
                      _link("Pro Git (free book)", "https://git-scm.com/book/", "📘")],
    },
}


# ---------------------------------------------------------------------------
# Catalogue assembly
# ---------------------------------------------------------------------------
def _default_resources(name):
    return [_yt(name + " full course"), _nptel(name), _gfg(name)]


def build_catalog():
    """All courses (core Sem I–VII + the elective courses), de-duplicated."""
    seen = {}
    order = []
    # Core courses from the official scheme
    for sem in SEMESTERS:
        for code, name, cat, ltp, cr in sem["courses"]:
            if code in ("—", "UCSXXX") or code in seen:
                continue
            seen[code] = {"code": code, "name": name, "category": cat,
                          "ltp": ltp, "cr": cr, "where": sem["name"],
                          "field": None, "is_elective": False}
            order.append(code)
    # Elective courses from the focus tracks
    for f in ELECTIVE_FOCUS:
        for code, name in f["courses"]:
            if code in seen:
                continue
            seen[code] = {"code": code, "name": name, "category": "PE",
                          "ltp": "2-0-2", "cr": "3.0", "where": "Elective",
                          "field": f["name"], "is_elective": True}
            order.append(code)
    return [seen[c] for c in order]


CATALOG = build_catalog()
CATALOG_BY_CODE = {c["code"]: c for c in CATALOG}


def get_course(code):
    """Return a full course view (metadata + content) or None."""
    meta = CATALOG_BY_CODE.get(code)
    if not meta:
        return None
    content = COURSE_CONTENT.get(code, {})
    info = dict(meta)
    info["category_name"] = CATEGORY_NAMES.get(meta["category"], meta["category"])
    info["objective"] = content.get("objective", "")
    info["topics"] = content.get("topics", [])
    info["textbooks"] = content.get("textbooks", [])
    # resources = curated (or default) + online-course platforms, de-duplicated
    res = list(content.get("resources") or _default_resources(meta["name"]))
    res += mooc_links(meta["name"])
    seen, deduped = set(), []
    for r in res:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        deduped.append(r)
    info["resources"] = deduped
    info["has_content"] = bool(content)
    # If predicted by the recommender, note its field
    if code in TARGET_INFO:
        info["predicted_field"] = TARGET_INFO[code]["field"]
        info["predicted_icon"] = TARGET_INFO[code]["icon"]
    return info


def catalog_by_group():
    """Catalog grouped by 'where' (semester or 'Elective') for the hub page."""
    groups = {}
    for c in CATALOG:
        groups.setdefault(c["where"], []).append(c)
    return groups
