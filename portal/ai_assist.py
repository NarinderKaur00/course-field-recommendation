"""
ai_assist.py
------------
GenAI study assistant. Generates a personalized study plan for a course.

- If an LLM is configured (env LLM_PROVIDER = anthropic|openai + LLM_API_KEY),
  it calls that model.
- Otherwise it falls back to a built-in rule-based planner, so the feature
  always works (great for a live demo without a paid key).

Env vars:
  LLM_PROVIDER  none | anthropic | openai        (default: none)
  LLM_API_KEY   your API key
  LLM_MODEL     model id (optional; sensible default per provider)
"""
import os
import json
import requests

PROVIDER = os.environ.get("LLM_PROVIDER", "none").lower()
API_KEY = os.environ.get("LLM_API_KEY", "")
MODEL = os.environ.get("LLM_MODEL", "")

_DEFAULT_MODEL = {
    "anthropic": "claude-3-5-haiku-20241022",
    "openai": "gpt-4o-mini",
    "groq": "openai/gpt-oss-20b",           # free, fast, OpenAI-compatible (override with LLM_MODEL)
}

_LABEL = {
    "anthropic": "AI · Claude",
    "openai": "AI · GPT",
    "groq": "AI · Llama (Groq)",
}


def llm_enabled():
    return PROVIDER in ("anthropic", "openai", "groq") and bool(API_KEY)


def _prompt(course):
    topics = ", ".join(course.get("topics", [])) or course["name"]
    books = "; ".join(course.get("textbooks", [])) or "standard textbooks"
    return (
        f"You are a study coach. Create a concise, motivating 4-week study plan "
        f"for the university course '{course['code']} — {course['name']}'.\n"
        f"Syllabus topics: {topics}.\n"
        f"Recommended books: {books}.\n"
        f"For each week give a heading and 3-4 bullet tasks (learn, practice, "
        f"checkpoint). End with one mini-project idea. Keep it under 250 words."
    )


def _call_anthropic(prompt):
    model = MODEL or _DEFAULT_MODEL["anthropic"]
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        data=json.dumps({
            "model": model, "max_tokens": 700,
            "messages": [{"role": "user", "content": prompt}],
        }),
        timeout=40,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def _call_openai_compatible(prompt, url, default_model):
    """Shared caller for OpenAI-format chat APIs (OpenAI + Groq)."""
    model = MODEL or default_model
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {API_KEY}", "content-type": "application/json"},
        data=json.dumps({
            "model": model, "max_tokens": 700,
            "messages": [{"role": "user", "content": prompt}],
        }),
        timeout=40,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _call_openai(prompt):
    return _call_openai_compatible(
        prompt, "https://api.openai.com/v1/chat/completions", _DEFAULT_MODEL["openai"])


def _call_groq(prompt):
    return _call_openai_compatible(
        prompt, "https://api.groq.com/openai/v1/chat/completions", _DEFAULT_MODEL["groq"])


def _call_llm(prompt):
    """Dispatch to whichever provider is configured."""
    if PROVIDER == "anthropic":
        return _call_anthropic(prompt)
    if PROVIDER == "groq":
        return _call_groq(prompt)
    return _call_openai(prompt)


def _fallback_plan(course):
    """Rule-based 4-week plan built from the syllabus topics."""
    topics = course.get("topics", [])
    if not topics:
        topics = [f"Core concepts of {course['name']}"]
    # split topics across 4 weeks (roughly even)
    import math
    per = max(1, math.ceil(len(topics) / 4))
    weeks = []
    for w in range(0, len(topics), per):
        chunk = topics[w:w + per]
        n = len(weeks) + 1
        items = [f"📖 Learn: {t}" for t in chunk]
        items.append("✍️ Practice problems / revise with notes")
        items.append("✅ Checkpoint: explain this week's topics in your own words")
        weeks.append({"title": f"Week {n}", "items": items})
    weeks.append({
        "title": f"Week {len(weeks) + 1} — Apply it",
        "items": [f"🚀 Build a mini-project using {course['name']}",
                  "📝 Revise all topics & attempt past questions",
                  "🎯 Use the resources on this page (videos / Coursera / docs)"],
    })
    return {"source": "Built-in study planner", "weeks": weeks, "text": None}


def generate_study_plan(course):
    """Return {'source', 'weeks'|None, 'text'|None}."""
    if llm_enabled():
        try:
            prompt = _prompt(course)
            text = _call_llm(prompt)
            label = _LABEL.get(PROVIDER, "AI")
            return {"source": label, "weeks": None, "text": text.strip()}
        except Exception as e:
            fb = _fallback_plan(course)
            fb["source"] = f"Built-in planner (AI unavailable: {type(e).__name__})"
            return fb
    return _fallback_plan(course)
