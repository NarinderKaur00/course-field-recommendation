"""
advisor.py
----------
AI Specialization Advisor — a chatbot that helps students choose their
Elective-Focus specialization and answers questions about each track.

- If an LLM is configured (env LLM_PROVIDER + LLM_API_KEY) it answers with a
  real language model, grounded in the student's own recommendation + the
  specialization knowledge base below.
- Otherwise it uses a built-in rule-based engine (keyword + intent matching)
  so the chatbot always works, even without a paid API key.
"""
import ai_assist   # reuse the LLM plumbing (llm_enabled, _call_anthropic/_openai)


# ---- Specialization knowledge base ----------------------------------------
# One entry per Elective-Focus track: what it is, careers, and the subjects
# that matter most. Keyed by the field name used across the app.
SPEC_KB = {
    "High Performance Computing": {
        "what": "Building systems that run huge computations fast — cloud, GPUs and parallel/distributed computing.",
        "careers": ["Cloud Engineer", "HPC / Systems Engineer", "Backend Engineer", "Infrastructure Engineer"],
        "strengths": ["Operating Systems", "Computer Architecture", "Programming", "Maths"],
    },
    "Computer Animation and Gaming": {
        "what": "Graphics, game development, 3D/animation and AR/VR, plus computer vision.",
        "careers": ["Game Developer", "Graphics Engineer", "AR/VR Developer", "Technical Artist"],
        "strengths": ["Programming", "Linear Algebra / geometry", "Creativity", "Maths"],
    },
    "Computer Animation & Gaming": {
        "what": "Graphics, game development, 3D/animation and AR/VR, plus computer vision.",
        "careers": ["Game Developer", "Graphics Engineer", "AR/VR Developer", "Technical Artist"],
        "strengths": ["Programming", "Linear Algebra / geometry", "Creativity", "Maths"],
    },
    "Information and Cyber Security": {
        "what": "Protecting systems, networks and data — cryptography, secure coding and blockchain.",
        "careers": ["Security Analyst", "Security Engineer", "Penetration Tester", "Blockchain Developer"],
        "strengths": ["Computer Networks", "Operating Systems", "Maths", "Programming"],
    },
    "Information & Cyber Security": {
        "what": "Protecting systems, networks and data — cryptography, secure coding and blockchain.",
        "careers": ["Security Analyst", "Security Engineer", "Penetration Tester", "Blockchain Developer"],
        "strengths": ["Computer Networks", "Operating Systems", "Maths", "Programming"],
    },
    "Mathematics and Computing": {
        "what": "Maths-heavy computing — the mathematics behind AI/ML, cryptography, quantum and finance.",
        "careers": ["Quantitative Analyst", "Research Engineer", "Cryptographer", "Data Scientist"],
        "strengths": ["Calculus", "Linear Algebra", "Probability & Statistics", "Discrete Maths"],
    },
    "Data Science": {
        "what": "Turning data into insight and building machine-learning / deep-learning models.",
        "careers": ["Data Scientist", "Machine Learning Engineer", "Data Analyst", "AI Engineer"],
        "strengths": ["Probability & Statistics", "Machine Learning", "Programming", "Maths"],
    },
    "Financial Derivative": {
        "what": "Applying computing and maths to finance — markets, pricing and risk.",
        "careers": ["Quant Analyst", "Risk Analyst", "FinTech Developer", "Algorithmic Trader"],
        "strengths": ["Probability & Statistics", "Maths", "Programming"],
    },
    "DevOps and Continuous Delivery": {
        "what": "Automating how software is built, tested and shipped — CI/CD and infrastructure.",
        "careers": ["DevOps Engineer", "Site Reliability Engineer (SRE)", "Platform Engineer", "Cloud Engineer"],
        "strengths": ["Operating Systems", "Computer Networks", "Programming / scripting", "Software Engineering"],
    },
    "DevOps & Continuous Delivery": {
        "what": "Automating how software is built, tested and shipped — CI/CD and infrastructure.",
        "careers": ["DevOps Engineer", "Site Reliability Engineer (SRE)", "Platform Engineer", "Cloud Engineer"],
        "strengths": ["Operating Systems", "Computer Networks", "Programming / scripting", "Software Engineering"],
    },
    "Full Stack": {
        "what": "Building complete web applications — front-end, back-end, data and cloud.",
        "careers": ["Full-Stack Developer", "Front-end / Back-end Engineer", "UI/UX Engineer", "Software Engineer"],
        "strengths": ["Programming", "Database Management Systems", "Software Engineering", "Design sense"],
    },
    "Conversational AI": {
        "what": "Language and speech AI — chatbots, natural-language processing and generative AI.",
        "careers": ["NLP Engineer", "Machine Learning Engineer", "Generative-AI Engineer", "AI Researcher"],
        "strengths": ["Machine Learning", "Probability & Statistics", "Programming", "Maths"],
    },
    "Robotics and Edge AI": {
        "what": "Running AI on devices and robots — embedded vision, edge computing and reinforcement learning.",
        "careers": ["Robotics Engineer", "Embedded AI Engineer", "Edge-AI Developer", "Control Systems Engineer"],
        "strengths": ["Programming", "Electronics", "Machine Learning", "Maths"],
    },
    "Cyber Forensics & Ethical Hacking": {
        "what": "Offensive security — ethical hacking, penetration testing, forensics and network defence.",
        "careers": ["Ethical Hacker", "Penetration Tester", "Forensics Analyst", "SOC Analyst"],
        "strengths": ["Computer Networks", "Operating Systems", "Programming", "Problem solving"],
    },
    "Intelligent Transport Systems": {
        "what": "Computing for connected vehicles and smart mobility — IoT, analytics and security.",
        "careers": ["ITS Engineer", "IoT / Embedded Engineer", "Mobility Data Analyst", "Connected-Vehicle Engineer"],
        "strengths": ["Computer Networks", "Data Analytics", "Programming", "Security"],
    },
}

# keyword -> canonical field, for matching free text
_ALIASES = {
    "data science": "Data Science", "data scientist": "Data Science", "ml": "Data Science",
    "machine learning": "Data Science", "ai": "Data Science",
    "security": "Information and Cyber Security", "cyber": "Information and Cyber Security",
    "blockchain": "Information and Cyber Security",
    "hacking": "Cyber Forensics & Ethical Hacking", "ethical": "Cyber Forensics & Ethical Hacking",
    "forensic": "Cyber Forensics & Ethical Hacking", "pentest": "Cyber Forensics & Ethical Hacking",
    "nlp": "Conversational AI", "chatbot": "Conversational AI", "language": "Conversational AI",
    "generative": "Conversational AI", "speech": "Conversational AI",
    "game": "Computer Animation and Gaming", "gaming": "Computer Animation and Gaming",
    "graphics": "Computer Animation and Gaming", "animation": "Computer Animation and Gaming",
    "vr": "Computer Animation and Gaming", "ar": "Computer Animation and Gaming",
    "cloud": "High Performance Computing", "gpu": "High Performance Computing",
    "parallel": "High Performance Computing", "hpc": "High Performance Computing",
    "devops": "DevOps and Continuous Delivery", "ci/cd": "DevOps and Continuous Delivery",
    "deployment": "DevOps and Continuous Delivery",
    "full stack": "Full Stack", "web": "Full Stack", "frontend": "Full Stack",
    "backend": "Full Stack", "ui": "Full Stack", "ux": "Full Stack",
    "robot": "Robotics and Edge AI", "edge": "Robotics and Edge AI", "embedded": "Robotics and Edge AI",
    "finance": "Financial Derivative", "trading": "Financial Derivative", "quant": "Financial Derivative",
    "maths": "Mathematics and Computing", "cryptography": "Mathematics and Computing",
    "quantum": "Mathematics and Computing",
    "transport": "Intelligent Transport Systems", "vehicle": "Intelligent Transport Systems",
    "mobility": "Intelligent Transport Systems",
}


def _match_field(text):
    t = text.lower()
    # exact field name first
    for name in SPEC_KB:
        if name.lower() in t:
            return name
    # then keyword aliases (longest first so 'full stack' beats 'ai')
    for kw in sorted(_ALIASES, key=len, reverse=True):
        if kw in t:
            return _ALIASES[kw]
    return None


def _describe(field):
    kb = SPEC_KB.get(field)
    if not kb:
        return f"**{field}** is one of the specialization tracks you can choose."
    careers = ", ".join(kb["careers"])
    strengths = ", ".join(kb["strengths"])
    return (f"**{field}** — {kb['what']}\n\n"
            f"💼 Careers: {careers}.\n"
            f"📚 Do well in these subjects for it: {strengths}.")


# ---- rule-based engine -----------------------------------------------------
def _rule_based(question, ctx):
    q = question.lower().strip()
    top_fields = ctx.get("top_fields") or []
    top_name = top_fields[0]["field"] if top_fields else None

    # 1) "which should I choose / best for me / suggest / recommend"
    if any(k in q for k in ("which", "best for me", "suggest", "recommend", "should i",
                            "what should", "choose", "pick", "right for me", "suit")):
        if top_fields:
            lines = [f"Based on the marks you entered, your best-fit tracks are:"]
            for i, f in enumerate(top_fields[:3], 1):
                lines.append(f"{i}. **{f['field']}** — fit {f.get('avg','?')}/100")
            lines.append("")
            lines.append(_describe(top_fields[0]["field"]))
            lines.append("\n💡 Open **Recommendations** to see the full list and the reasons.")
            return "\n".join(lines)
        return ("I can suggest a specialization once you've entered your marks. "
                "Go to **My Results**, add your marks and hit *Save & Recommend*, "
                "then ask me again!")

    # 2) a specific field mentioned -> describe it (careers / subjects)
    field = _match_field(q)
    if field:
        ans = _describe(field)
        if any(k in q for k in ("career", "job", "scope", "salary", "future")):
            kb = SPEC_KB.get(field, {})
            ans = f"💼 Careers in **{field}**: {', '.join(kb.get('careers', []))}.\n\n" + ans
        return ans

    # 3) "why" questions about their recommendation
    if "why" in q and top_name:
        reason = ctx.get("reason")
        base = f"Your top track is **{top_name}**."
        if reason:
            base += f" {reason}"
        return base + "\n\n" + _describe(top_name)

    # 4) careers in general
    if any(k in q for k in ("career", "job", "scope")) and top_name:
        kb = SPEC_KB.get(top_name, {})
        return (f"For your top track **{top_name}**, common careers are: "
                f"{', '.join(kb.get('careers', []))}.")

    # 5) list all
    if any(k in q for k in ("list", "all", "options", "tracks", "specialization", "fields")):
        names = "\n".join(f"• {n}" for n in dict.fromkeys(  # de-dup alias keys
            [k for k in SPEC_KB if '&' not in k]))
        return "Here are the specialization tracks you can choose:\n" + names + \
               "\n\nAsk me about any one (e.g. *'tell me about Data Science'*)."

    # fallback
    hint = f" Your current best-fit track is **{top_name}**." if top_name else ""
    return ("I'm your specialization advisor 🎓. Ask me things like:\n"
            "• *Which specialization is best for me?*\n"
            "• *Tell me about Data Science*\n"
            "• *What careers are in Cyber Security?*" + hint)


# ---- public entry ----------------------------------------------------------
def answer(question, ctx):
    """ctx = {top_fields:[{field,avg}], top_elective:{...}, reason:str}"""
    if ai_assist.llm_enabled():
        try:
            return _llm_answer(question, ctx)
        except Exception:
            pass   # fall back silently
    return _rule_based(question, ctx)


def _llm_answer(question, ctx):
    top = ", ".join(f"{f['field']} ({f.get('avg','?')}/100)"
                    for f in (ctx.get("top_fields") or [])[:3]) or "not computed yet"
    kb_lines = "\n".join(f"- {n}: {d['what']} Careers: {', '.join(d['careers'])}."
                         for n, d in SPEC_KB.items() if '&' not in n)
    prompt = (
        "You are EduPath's friendly specialization advisor for B.E. (CSE) students. "
        "Answer ONLY about choosing an Elective-Focus specialization and related careers. "
        "Be concise (under 130 words), warm and practical.\n\n"
        f"The student's best-fit tracks from their marks: {top}.\n"
        f"Reason given by the recommender: {ctx.get('reason') or 'n/a'}.\n\n"
        f"Specialization tracks available:\n{kb_lines}\n\n"
        f"Student's question: {question}"
    )
    if ai_assist.PROVIDER == "anthropic":
        return ai_assist._call_anthropic(prompt).strip()
    return ai_assist._call_openai(prompt).strip()
