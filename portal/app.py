"""
app.py  -  Course & Field Recommendation Student Portal
=======================================================
A Flask web application that wraps the machine-learning engine (ml_core.py)
in a friendly student portal.

Covers the full data-flow diagram:
  1.0 Register / Sign Up        -> /register
  2.0 Login / Sign In           -> /login
  3.0 Manage Profile & Results  -> /results
  4.0 Preprocess + 5.0 Train    -> ml_core (models trained by train_models.py)
  6.0 Generate Prediction       -> ml_core.recommend_for_student
  7.0 Generate & View Recommend -> /recommend, /recommendation, /history
  8.0 Logout                    -> /logout

Run:
    python portal/app.py
Then open http://127.0.0.1:5000
"""

import os
import re
import sys
import json
from datetime import datetime
from functools import wraps

# Load a local .env file (your own MONGODB_URI, admin creds, API keys) if present.
# Safe no-op in production, where real environment variables are used instead.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except Exception:
    pass

import store

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, abort,
)
from werkzeug.security import generate_password_hash, check_password_hash

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ml_core import (  # noqa: E402
    load_bundle, recommend_for_student, explain_prediction,
    train_and_save, GRADE_LETTERS,
)
from curriculum import (  # noqa: E402
    SEMESTERS, ELECTIVE_FOCUS, PROFESSIONAL_ELECTIVES,
    GENERIC_ELECTIVES, CATEGORY_NAMES,
)
from thapar_map import (  # noqa: E402
    feature_groups, enrich_predictions, recommended_fields,
    TARGET_INFO, FEATURE_NAME,
)
from courses_data import (  # noqa: E402
    catalog_by_group, get_course, CATALOG_BY_CODE,
)
from ai_assist import generate_study_plan, llm_enabled as ai_llm_enabled  # noqa: E402

# ----------------------------------------------------------------------------
# App setup
# ----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "co544-student-portal-dev-secret-change-me")
app.config.update(
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,                 # cap uploads at 5 MB
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ---- CSRF protection (#3) ----
from flask_wtf import CSRFProtect           # noqa: E402
from flask_wtf.csrf import CSRFError         # noqa: E402
csrf = CSRFProtect(app)


@app.errorhandler(CSRFError)
def _handle_csrf(e):
    flash("Your form session expired — please try again.", "danger")
    return redirect(request.referrer or url_for("index"))


# ---- simple in-memory login rate limiting (#3) ----
import time                                  # noqa: E402
from collections import defaultdict           # noqa: E402
_LOGIN_FAILS = defaultdict(list)
RATE_MAX, RATE_WINDOW = 5, 600               # 5 tries per 10 minutes


def _too_many(key):
    now = time.time()
    _LOGIN_FAILS[key] = [t for t in _LOGIN_FAILS[key] if now - t < RATE_WINDOW]
    return len(_LOGIN_FAILS[key]) >= RATE_MAX


def _record_fail(key):
    _LOGIN_FAILS[key].append(time.time())


def _clear_fail(key):
    _LOGIN_FAILS.pop(key, None)


# ---- audit log (#4) ----
def log_action(actor, action, detail=""):
    try:
        store.add_audit(actor, action, detail, datetime.now().strftime("%Y-%m-%d %H:%M"))
    except Exception:
        pass


# ---- dataset schema validation (#1) ----
def validate_dataset(path, expected_cols):
    """Check an uploaded CSV before retraining. Returns (ok, message)."""
    import pandas as pd
    try:
        df = pd.read_csv(path, na_values=["NA"])
    except Exception as e:
        return False, f"Could not read the CSV ({e})."
    cols = set(df.columns)
    missing = set(expected_cols) - cols
    if missing:
        sample = ", ".join(sorted(missing)[:6])
        return False, f"Missing {len(missing)} required column(s): {sample} …"
    if len(df) < 30:
        return False, f"Too few rows ({len(df)}). Need at least 30 students."
    sub = df[list(expected_cols)].apply(pd.to_numeric, errors="coerce")
    mx, mn = sub.max().max(), sub.min().min()
    if pd.notna(mx) and mx > 100:
        return False, f"Some marks are above 100 (max found: {mx:g})."
    if pd.notna(mn) and mn < 0:
        return False, f"Some marks are negative (min found: {mn:g})."
    return True, f"Valid — {len(df)} students, {len(cols)} columns."

MODELS_DIR = os.path.join(HERE, "models")
DATA_PATH = os.path.join(os.path.dirname(HERE), "data", "Grade_Thapar_Students.csv")

# Admin credentials — from environment, with demo fallbacks.
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")

# Load the trained ML bundle once at startup (may be None if not trained yet)
BUNDLE = load_bundle(MODELS_DIR)


# ----------------------------------------------------------------------------
# Database (MongoDB via store.py — set MONGODB_URI, else in-memory mongomock)
# ----------------------------------------------------------------------------
def init_db():
    store.configure()


# ----------------------------------------------------------------------------
# Auth helpers
# ----------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def build_reason(drivers):
    """A plain-English reason why an elective is a strong fit."""
    if not drivers:
        return ""
    good = [d for d in drivers if d["grade_class"] <= 4][:2]   # B or better
    if len(good) >= 2:
        return (f"Strong fit — you did well in {good[0]['name']} and "
                f"{good[1]['name']}, which this elective relies on most.")
    if len(good) == 1:
        return (f"Good fit — your strength in {good[0]['name']} "
                f"aligns with this elective.")
    names = " and ".join(d["name"] for d in drivers[:2])
    return f"This elective leans most on {names}."


def current_user():
    uid = session.get("user_id")
    if uid is None:
        return None
    return store.get_user_by_id(uid)


@app.context_processor
def inject_user():
    return {"user": current_user()}


# ----------------------------------------------------------------------------
# Subject grouping for the results form (Year 1 / 2 / 3)
# ----------------------------------------------------------------------------
DEPT_NAMES = {
    "CS": "Computer Science", "MA": "Mathematics", "GS": "General Studies",
    "PH": "Physics", "ST": "Statistics", "OR": "Operational Research",
    "SW": "Software", "MM": "Multimedia",
}


def group_feature_subjects(feature_columns):
    """Group the 52 input subjects into year buckets for a tidy form."""
    buckets = {"Year 1 (100-level)": [], "Year 2 (200-level)": [], "Year 3+ (300-500 level)": []}
    for code in feature_columns:
        m = re.match(r"([A-Za-z]+)(\d+)", code)
        dept = m.group(1) if m else code
        num = int(m.group(2)) if m else 0
        level = num // 100
        tag = DEPT_NAMES.get(dept, dept)
        item = {"code": code, "dept": dept, "dept_name": tag}
        if level <= 1:
            buckets["Year 1 (100-level)"].append(item)
        elif level == 2:
            buckets["Year 2 (200-level)"].append(item)
        else:
            buckets["Year 3+ (300-500 level)"].append(item)
    return {k: v for k, v in buckets.items() if v}


# ----------------------------------------------------------------------------
# Routes - Authentication
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        consent = 1 if request.form.get("consent") else 0

        error = None
        if not name or not email or not password:
            error = "All fields are required."
        elif not EMAIL_RE.match(email):
            error = "Please enter a valid email address."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 4:
            error = "Password must be at least 4 characters."
        elif not consent:
            error = "Please accept the privacy policy to continue."

        if error is None:
            try:
                store.create_user(name, email, generate_password_hash(password),
                                  consent, datetime.now().strftime("%Y-%m-%d %H:%M"))
            except store.DUPLICATE_ERRORS:
                error = "That email is already registered."
            else:
                flash("Account created! Please sign in.", "success")
                return redirect(url_for("login"))
        flash(error, "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        key = f"login:{email}"
        if _too_many(key):
            flash("Too many failed attempts. Please wait a few minutes.", "danger")
            return render_template("login.html")
        user = store.get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            _record_fail(key)
            flash("Invalid email or password.", "danger")
        else:
            _clear_fail(key)
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name'].split()[0]}!", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# ----------------------------------------------------------------------------
# Routes - Portal
# ----------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    has_results = store.get_results(uid) is not None
    rec_count = store.count_recommendations(uid)
    latest = store.latest_recommendation(uid)
    latest_payload = enrich_predictions(json.loads(latest["payload_json"])) if latest else None

    n_subjects = len(BUNDLE["feature_columns"]) if BUNDLE else 0
    n_electives = len(BUNDLE["target_subjects"]) if BUNDLE else 0
    avg_acc = round(sum(BUNDLE["accuracies"].values()) / n_electives * 100) if BUNDLE else 0

    return render_template(
        "dashboard.html",
        has_results=has_results,
        rec_count=rec_count,
        latest=latest_payload,
        latest_date=latest["created_at"] if latest else None,
        n_subjects=n_subjects,
        n_electives=n_electives,
        avg_acc=avg_acc,
        model_ready=BUNDLE is not None,
    )


@app.route("/results", methods=["GET", "POST"])
@login_required
def results():
    if BUNDLE is None:
        flash("Models are not trained yet. Run: python portal/train_models.py", "danger")
        return redirect(url_for("dashboard"))

    uid = session["user_id"]
    feature_columns = BUNDLE["feature_columns"]

    if request.method == "POST":
        marks = {}
        for code in feature_columns:
            raw = request.form.get(code, "").strip()
            if raw != "":
                try:
                    val = max(0, min(100, float(raw)))
                    if val > 0:           # 0 / blank = subject not taken -> skip
                        marks[code] = val
                except ValueError:
                    pass
        store.upsert_results(uid, json.dumps(marks),
                             datetime.now().strftime("%Y-%m-%d %H:%M"))
        if request.form.get("action") == "recommend":
            return redirect(url_for("recommend"))
        flash("Your academic results were saved.", "success")
        return redirect(url_for("results"))

    # Form starts at 0 — the student enters the marks they actually scored.
    row = store.get_results(uid)
    saved = json.loads(row["marks_json"]) if row else {}
    defaults = {c: 0 for c in feature_columns}

    return render_template(
        "results.html",
        groups=feature_groups(),
        saved=saved,
        defaults=defaults,
        has_saved=bool(saved),
    )


@app.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():
    if BUNDLE is None:
        flash("Models are not trained yet.", "danger")
        return redirect(url_for("dashboard"))

    uid = session["user_id"]
    row = store.get_results(uid)
    if row is None:
        flash("Please enter your academic results first.", "warning")
        return redirect(url_for("results"))

    marks = json.loads(row["marks_json"])
    result = recommend_for_student(marks, BUNDLE, top_n=5)
    # Attach an explanation (top driver subjects) to each recommended elective
    for p in result["recommended"]:
        p["drivers"] = explain_prediction(marks, BUNDLE, p["subject"], top_n=5)
    new_id = store.add_recommendation(
        uid, datetime.now().strftime("%Y-%m-%d %H:%M"), json.dumps(result))
    return redirect(url_for("recommendation", rec_id=new_id))


@app.route("/recommendation/<int:rec_id>")
@login_required
def recommendation(rec_id):
    uid = session["user_id"]
    row = store.get_recommendation(rec_id, uid)
    if row is None:
        abort(404)
    payload = enrich_predictions(json.loads(row["payload_json"]))

    # Backfill explanations for older recommendations, and add friendly names.
    mrow = store.get_results(uid)
    marks = json.loads(mrow["marks_json"]) if mrow else {}
    for p in payload.get("recommended", []):
        if not p.get("drivers") and marks:
            p["drivers"] = explain_prediction(marks, BUNDLE, p["subject"], top_n=5)
        for d in p.get("drivers", []):
            d["name"] = FEATURE_NAME.get(d["feature"], d["feature"])
        p["reason"] = build_reason(p.get("drivers", []))

    return render_template(
        "recommendation.html",
        rec=payload,
        fields=recommended_fields(payload, top_k=3),
        created_at=row["created_at"],
        rec_id=rec_id,
    )


@app.route("/history")
@login_required
def history():
    uid = session["user_id"]
    rows = store.list_recommendations(uid)
    items = []
    for r in rows:
        payload = enrich_predictions(json.loads(r["payload_json"]))
        top = payload["recommended"][0] if payload["recommended"] else None
        items.append({
            "id": r["id"],
            "created_at": r["created_at"],
            "top": top,
            "count": len(payload["recommended"]),
        })
    return render_template("history.html", items=items)


@app.route("/models")
@login_required
def models():
    if BUNDLE is None:
        flash("Models are not trained yet.", "danger")
        return redirect(url_for("dashboard"))
    perf = sorted(
        ({"subject": s, "name": TARGET_INFO.get(s, {}).get("name", s),
          "field": TARGET_INFO.get(s, {}).get("field", ""),
          "accuracy": round(a * 100, 1)} for s, a in BUNDLE["accuracies"].items()),
        key=lambda x: -x["accuracy"],
    )
    avg = round(sum(p["accuracy"] for p in perf) / len(perf), 1)
    return render_template("models.html", perf=perf, avg=avg,
                           n_subjects=len(BUNDLE["feature_columns"]))


@app.route("/curriculum")
@login_required
def curriculum():
    # Curriculum is merged into the Courses page.
    return redirect(url_for("courses"))


@app.route("/fields")
@login_required
def fields():
    return render_template(
        "fields.html",
        focus=ELECTIVE_FOCUS,
        prof_electives=PROFESSIONAL_ELECTIVES,
        generic=GENERIC_ELECTIVES,
    )


# ----------------------------------------------------------------------------
# Courses & Learning
# ----------------------------------------------------------------------------
def _enrolled_codes(uid):
    return store.enrolled_codes(uid)


def _progress_done(uid, code):
    row = store.get_progress(uid, code)
    return set(json.loads(row["done_json"])) if row else set()


def _credits(cr):
    try:
        return float(cr)
    except (TypeError, ValueError):
        return 0.0


@app.route("/courses")
@login_required
def courses():
    uid = session["user_id"]
    enrolled = _enrolled_codes(uid)
    groups = catalog_by_group()
    # credit subtotal per semester/group + overall core-credit total
    group_credits = {g: round(sum(_credits(c.get("cr")) for c in items), 1)
                     for g, items in groups.items()}
    core_credits = round(sum(v for g, v in group_credits.items() if g != "Elective"), 1)
    n_electives = sum(1 for c in CATALOG_BY_CODE.values() if c.get("is_elective"))
    return render_template(
        "courses.html",
        groups=groups,
        group_credits=group_credits,
        core_credits=core_credits,
        n_electives=n_electives,
        enrolled=enrolled,
        n_total=len(CATALOG_BY_CODE),
        n_enrolled=len(enrolled),
    )


def _course_context(uid, code):
    course = get_course(code)
    if course is None:
        return None
    done = _progress_done(uid, code)
    topics = course["topics"]
    return {
        "course": course,
        "enrolled": code in _enrolled_codes(uid),
        "done": done,
        "pct": round(len(done) / len(topics) * 100) if topics else 0,
    }


@app.route("/course/<code>")
@login_required
def course_detail(code):
    ctx = _course_context(session["user_id"], code)
    if ctx is None:
        abort(404)
    return render_template("course_detail.html", ai_enabled=ai_llm_enabled(), **ctx)


@app.route("/course/<code>/studyplan", methods=["POST"])
@login_required
def course_studyplan(code):
    ctx = _course_context(session["user_id"], code)
    if ctx is None:
        abort(404)
    plan = generate_study_plan(ctx["course"])
    return render_template("course_detail.html", ai_enabled=ai_llm_enabled(),
                           plan=plan, **ctx)


@app.route("/enroll/<code>", methods=["POST"])
@login_required
def enroll(code):
    if code not in CATALOG_BY_CODE:
        abort(404)
    store.enroll(session["user_id"], code, datetime.now().strftime("%Y-%m-%d %H:%M"))
    flash(f"Enrolled in {code}.", "success")
    return redirect(request.referrer or url_for("course_detail", code=code))


@app.route("/unenroll/<code>", methods=["POST"])
@login_required
def unenroll(code):
    store.unenroll(session["user_id"], code)
    flash(f"Removed {code} from My Learning.", "success")
    return redirect(request.referrer or url_for("courses"))


@app.route("/course/<code>/progress", methods=["POST"])
@login_required
def save_progress(code):
    course = get_course(code)
    if course is None:
        abort(404)
    uid = session["user_id"]
    done = [i for i in range(len(course["topics"]))
            if request.form.get(f"t{i}") == "on"]
    store.set_progress(uid, code, json.dumps(done))
    # saving progress implies enrollment
    store.enroll(uid, code, datetime.now().strftime("%Y-%m-%d %H:%M"))
    flash("Progress saved.", "success")
    return redirect(url_for("course_detail", code=code))


@app.route("/my-learning")
@login_required
def my_learning():
    uid = session["user_id"]
    enrolled = _enrolled_codes(uid)
    items = []
    for code in enrolled:
        course = get_course(code)
        if not course:
            continue
        topics = course["topics"]
        done = _progress_done(uid, code)
        items.append({
            "code": code, "name": course["name"], "where": course["where"],
            "pct": round(len(done) / len(topics) * 100) if topics else 0,
            "done": len(done), "total": len(topics),
        })
    items.sort(key=lambda x: -x["pct"])
    avg = round(sum(i["pct"] for i in items) / len(items)) if items else 0
    return render_template("my_learning.html", items=items, avg=avg)


# ----------------------------------------------------------------------------
# Admin area
# ----------------------------------------------------------------------------
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin sign-in required.", "warning")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        key = "adminlogin"
        if _too_many(key):
            flash("Too many failed attempts. Please wait a few minutes.", "danger")
            return render_template("admin_login.html")
        if (request.form.get("username") == ADMIN_USER
                and request.form.get("password") == ADMIN_PASS):
            _clear_fail(key)
            session.clear()
            session["is_admin"] = True
            log_action("admin", "login", "admin signed in")
            flash("Welcome, Admin.", "success")
            return redirect(url_for("admin_dashboard"))
        _record_fail(key)
        flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Admin signed out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    # --- students ---
    users = store.list_users_desc()
    students = []
    for u in users:
        has_res = store.get_results(u["id"]) is not None
        rc = store.count_recommendations(u["id"])
        latest = store.latest_recommendation(u["id"])
        top_field = ""
        if latest:
            flds = recommended_fields(enrich_predictions(json.loads(latest["payload_json"])), top_k=1)
            top_field = flds[0]["field"] if flds else ""
        students.append({"id": u["id"], "name": u["name"], "email": u["email"],
                         "created_at": u["created_at"], "has_results": has_res,
                         "rec_count": rc, "top_field": top_field})

    # --- popular fields across all recommendations ---
    all_recs = store.all_recommendations()
    field_tally = {}
    for r in all_recs:
        flds = recommended_fields(enrich_predictions(json.loads(r["payload_json"])), top_k=1)
        if flds:
            f = flds[0]["field"]
            field_tally[f] = field_tally.get(f, 0) + 1
    popular = sorted(({"field": k, "count": v} for k, v in field_tally.items()),
                     key=lambda x: -x["count"])

    # --- model performance ---
    perf = sorted(
        ({"subject": s, "name": TARGET_INFO.get(s, {}).get("name", s),
          "accuracy": round(a * 100, 1)} for s, a in BUNDLE["accuracies"].items()),
        key=lambda x: -x["accuracy"]) if BUNDLE else []

    # --- dataset info ---
    try:
        import pandas as pd
        df = pd.read_csv(DATA_PATH, na_values=["NA"])
        ds_rows, ds_cols = len(df), len(df.columns)
    except Exception:
        ds_rows = ds_cols = 0

    n_feat = len(BUNDLE["feature_columns"]) if BUNDLE else 0
    n_elec = len(BUNDLE["target_subjects"]) if BUNDLE else 0
    avg_acc = round(sum(p["accuracy"] for p in perf) / len(perf)) if perf else 0

    audit = store.recent_audit(15)

    return render_template(
        "admin_dashboard.html",
        students=students,
        n_students=len(students),
        n_with_results=sum(1 for s in students if s["has_results"]),
        n_recs=len(all_recs),
        popular=popular,
        perf=perf,
        audit=audit,
        ds_rows=ds_rows, ds_cols=ds_cols,
        n_feat=n_feat, n_elec=n_elec, avg_acc=avg_acc,
    )


@app.route("/admin/export")
@admin_required
def admin_export():
    """Download a full JSON backup of all collections (#2 backups)."""
    dump = store.export_all()
    log_action("admin", "export_backup", f"{sum(len(v) for v in dump.values())} rows")
    from flask import Response
    return Response(
        json.dumps(dump, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=edupath_backup.json"},
    )


@app.route("/admin/retrain", methods=["POST"])
@admin_required
def admin_retrain():
    global BUNDLE
    data_path = DATA_PATH
    # optional uploaded dataset
    f = request.files.get("dataset")
    if f and f.filename:
        if not f.filename.lower().endswith(".csv"):
            flash("Please upload a .csv file.", "danger")
            return redirect(url_for("admin_dashboard"))
        upath = os.path.join(os.path.dirname(HERE), "data", "admin_upload.csv")
        f.save(upath)
        data_path = upath
        # Validate the uploaded dataset BEFORE training (#1)
        expected = set(BUNDLE["feature_columns"]) | set(BUNDLE["target_subjects"])
        ok, msg = validate_dataset(upath, expected)
        if not ok:
            flash(f"Dataset rejected: {msg}", "danger")
            log_action("admin", "retrain_rejected", msg)
            return redirect(url_for("admin_dashboard"))
        flash(f"Dataset check passed — {msg}", "success")

    try:
        accuracies = train_and_save(data_path, MODELS_DIR)
        BUNDLE = load_bundle(MODELS_DIR)
        avg = round(sum(accuracies.values()) / len(accuracies) * 100, 1)
        log_action("admin", "retrain", f"{os.path.basename(data_path)} avg={avg}%")
        flash(f"Models retrained on {os.path.basename(data_path)} — "
              f"average accuracy {avg}% across {len(accuracies)} electives.", "success")
    except Exception as e:
        flash(f"Retrain failed: {e}. The uploaded file must have the same "
              f"feature + elective columns as the training dataset.", "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/student/<int:uid>/reset", methods=["POST"])
@admin_required
def admin_reset_student(uid):
    u = store.get_user_by_id(uid)
    if u is None:
        abort(404)
    store.purge_student(uid)
    log_action("admin", "reset_student", u["name"])
    flash(f"Reset {u['name']}'s data (account kept, results & recommendations cleared).", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/student/<int:uid>/delete", methods=["POST"])
@admin_required
def admin_delete_student(uid):
    u = store.get_user_by_id(uid)
    if u is None:
        abort(404)
    store.purge_student(uid)
    store.delete_user(uid)
    log_action("admin", "delete_student", u["name"])
    flash(f"Deleted student {u['name']} and all their data.", "success")
    return redirect(url_for("admin_dashboard"))


# ----------------------------------------------------------------------------
# Privacy / data rights (#5 — DPDP-style)
# ----------------------------------------------------------------------------
@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ----------------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(413)
def too_large(e):
    flash("That file is too large (max 5 MB).", "danger")
    return redirect(url_for("admin_dashboard"))


# Ensure the database exists on import (so gunicorn/production works too).
init_db()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print("=" * 56)
    print(f"  Student Portal running at:  http://127.0.0.1:{port}")
    print("  Models loaded:", "YES" if BUNDLE else "NO (run train_models.py first)")
    print("  Press CTRL+C to stop")
    print("=" * 56)
    app.run(host="0.0.0.0", port=port, debug=debug)
