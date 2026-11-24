# 📘 EduPath — Complete Project Guide (read this and you'll understand everything)

**Project:** Course & Field Recommendation System based on Student Results
**For:** the whole team — written in very easy English, assuming you know nothing yet.

> How to use this guide: read it top to bottom once. By the end you'll understand
> **what the project does, how every piece works, and the machine-learning in depth** —
> enough to explain any part of it confidently in the evaluation. At the end there is a
> **viva Q&A** and a **"who explains what"** split for the three of us.

---

# PART 1 — The big picture (what is this project?)

Imagine a student has finished their first two years of engineering. Now they must
choose **elective subjects** (optional advanced courses) and a **specialization field**
(like Data Science, Cyber Security, Game Development…). Most students are confused about
what suits them.

**Our project is a smart advisor website.** The student types in the **marks** they
scored in their earlier subjects, and the system uses **machine learning** to predict
which electives they are most likely to do well in — and recommends those, with reasons.

In one sentence:

> **Enter your past marks → the system predicts your performance in each elective → it
> recommends the best-fit electives and specialization fields, and shows you where to learn them.**

It also has:
- A **course catalogue** (syllabus, free resources, progress tracking).
- An **AI chatbot advisor** that answers "which specialization should I pick?".
- An **admin panel** to manage students and the model.

---

# PART 2 — How a student uses it (the journey)

1. **Register** → create an account (name, email, password, agree to privacy).
2. **Login**.
3. **My Results** → type the marks scored in 22 earlier subjects (starts at 0).
4. Click **Save & Recommend**.
5. **Recommendation page** shows:
   - Best-fit **fields** (e.g. Data Science) with a fit score.
   - Top **electives** ranked, each with a **reason** ("you did well in Maths & Programming…").
   - A **"why" panel** showing which subjects the model relied on.
6. **Courses & Curriculum** → browse any course → syllabus, resources, an **AI study plan**.
7. **🎓 Advisor chatbot** (bottom-right) → ask "which specialization is best for me?".

---

# PART 3 — The tech stack (what we used and why)

| Part of the project | Technology | In simple words |
|---|---|---|
| The web pages | **HTML + Jinja2 + CSS** | what the user sees in the browser |
| The server/brain | **Python Flask** | receives clicks, runs logic, sends back pages |
| The machine learning | **XGBoost + scikit-learn + SMOTE** | the part that predicts grades |
| Saving the model | **joblib** | saves the trained model to a file |
| The database | **MongoDB** | stores users, marks, recommendations |
| The AI chatbot | **LLM (Groq)** + rule-based fallback | answers questions conversationally |
| Putting it online | **Docker + Render + GitHub** | makes it a real website on the internet |
| Testing | **pytest** | automatic checks that the code works |

---

# PART 4 — How everything fits together

```
   Browser (student)
        │  clicks / types marks
        ▼
   Flask  (app.py)  ── asks ──►  ML engine (ml_core.py)  ── uses ──► bundle.joblib (trained models)
        │                                                              ▲
        │  saves/reads                                                 │ trained once by
        ▼                                                              │ train_models.py
   MongoDB (store.py)                                          data/Grade_Thapar_Students.csv
```

**Key idea:** the models are **trained once** (offline) and saved to a file called
`bundle.joblib`. The website just **loads that file** and uses it — so predictions are
instant. Training and serving are separate.

Files (all inside `portal/`):
- `app.py` — the Flask server (all the pages/routes).
- `ml_core.py` — the machine-learning engine (training + prediction).
- `store.py` — talks to MongoDB.
- `advisor.py` + `ai_assist.py` — the AI chatbot and study-plan generator.
- `thapar_map.py`, `curriculum.py`, `courses_data.py` — course data.
- `templates/` — the HTML pages. `static/css/` — the styling.
- `tests/` — the automatic tests.

---

# PART 5 — THE MACHINE LEARNING (the heart — explained deeply)

This is the most important part to understand. Take your time here.

## 5.1 The idea in one line
We train **14 separate models — one for each elective subject**. Each model learns, from
past students, the pattern of *"students with these grades usually get this grade in my
elective."* Given a new student's marks, each model predicts their grade in its own elective.

## 5.2 The data
We have a table (`data/Grade_Thapar_Students.csv`). Each **row = one student**. The
**columns = their marks** in many subjects.
- **22 columns are "features"** (input) — the earlier/core subjects.
- **14 columns are "targets"** (what we predict) — the advanced electives.

> **Honesty note:** this dataset is a **relabeled stand-in** — real student grade patterns
> with Thapar course codes put on top. It is a demonstration dataset, *not* real Thapar
> records. The ML method is 100% real; only the labels are a stand-in. (Keep saying this in the viva — examiners respect honesty.)

## 5.3 Step 1 — Turn marks into grades ("encoding")
A model works better with a few **grade categories** than with 100 different mark values.
So every mark (0–100) becomes a **grade class** from 0 (best) to 11 (fail):

```python
def encode_grade(marks):
    marks = int(marks)
    if marks > 85:      return 0    # A+
    elif 80 <= marks:   return 1    # A
    elif 75 <= marks:   return 2    # A-
    ...
    else:               return 11   # E (fail)
```
So "92 in Maths" → grade class **0 (A+)**. This is done for every mark in the table.

## 5.4 Step 2 — Balance the data with SMOTE
Problem: in real data some grades are **rare** (very few students got, say, an A+). A model
trained on unbalanced data becomes lazy and ignores the rare grades.

**SMOTE** fixes this. It looks at the rare cases and **creates new, synthetic but realistic
examples** of them, until every grade is fairly represented. (SMOTE = *Synthetic Minority
Over-sampling Technique*.)

```python
smote = SMOTE(k_neighbors=3)
X_res, y_res = smote.fit_resample(features_encoded, y)   # balanced data
```

## 5.5 Step 3 — LabelEncoder (a translator)
XGBoost wants the answer labels to be neat numbers `0,1,2,…`. `LabelEncoder` converts our
grade classes into that form before training, and back afterwards. It's just a translator.

```python
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
```

## 5.6 Step 4 — XGBoost (the actual model), 14 of them
**XGBoost** builds **hundreds of small decision trees**. Each tree asks simple yes/no
questions ("scored well in Maths? → yes"). Each new tree **fixes the mistakes of the
previous trees**. Add them all up and you get a strong, accurate predictor. It is one of
the best models for "predict from a table of numbers".

We train **one XGBoost per elective** (14 total):

```python
for col in TARGET_SUBJECTS:          # the 14 electives
    ...
    final_model = XGBClassifier(eval_metric='mlogloss')
    final_model.fit(X_res, y_all_enc)    # learn the pattern for THIS elective
    models[col] = final_model
```

## 5.7 Training — the full function, explained
This is `train_bundle_from_dataframe()` in `ml_core.py`. Here is what it does, step by step:

```python
def train_bundle_from_dataframe(df, models_dir):
    df = df.drop(DROP_COLUMNS, axis=1)                 # drop ID / year columns
    feature_columns = [c for c in df.columns if c not in TARGET_SUBJECTS]
    features = df[feature_columns].copy()              # the 22 inputs
    targets  = df[TARGET_SUBJECTS].copy()              # the 14 electives

    # remember each subject's MEDIAN mark (used later to fill blanks), then encode marks->grades
    feature_medians = {}
    for col in feature_columns:
        features[col] = pd.to_numeric(features[col], errors='coerce')
        feature_medians[col] = float(features[col].median())
        features[col] = features[col].fillna(feature_medians[col])
    features_encoded = features.map(encode_grade)

    for col in TARGET_SUBJECTS:                         # train one model per elective
        y = targets_encoded[col]
        X_res, y_res = SMOTE(k_neighbors=3).fit_resample(features_encoded, y)  # balance
        # measure accuracy on a held-out 20% test slice:
        X_tr, X_te, y_tr, y_te = train_test_split(X_res, y_res, test_size=0.2, random_state=42)
        eval_model = XGBClassifier(eval_metric='mlogloss'); eval_model.fit(X_tr, le.fit_transform(y_tr))
        accuracies[col] = accuracy_score(..., eval_model.predict(X_te))
        # final model: refit on ALL the balanced data for the best real predictions:
        final_model = XGBClassifier(eval_metric='mlogloss'); final_model.fit(X_res, ...)
        models[col] = final_model

    bundle = {'feature_columns':…, 'feature_medians':…, 'target_subjects':…,
              'models':…, 'label_encoders':…, 'accuracies':…}
    joblib.dump(bundle, models_dir + '/bundle.joblib')  # SAVE everything to one file
```

Two models per elective on purpose:
- an **eval model** (trained on 80%, tested on 20%) → gives us the **accuracy number**.
- a **final model** (trained on 100% of the balanced data) → used for real predictions.

Everything (the 14 models + medians + column names + accuracies) is bundled into **one
file, `bundle.joblib`**. That single file is the "trained brain".

## 5.8 Loading the brain
The website loads it once at startup:
```python
def load_bundle(models_dir):
    return joblib.load(models_dir + '/bundle.joblib')   # the 14 trained models, ready to use
```

## 5.9 Making a prediction (the live part)
When a student clicks *Save & Recommend*, `recommend_for_student()` runs:

```python
def recommend_for_student(marks, bundle, top_n=5):
    X = _encode_student_row(marks, bundle)        # turn THIS student's marks into grades
    predictions = []
    for col in bundle['target_subjects']:         # ask all 14 models
        model = bundle['models'][col]
        grade_class = ...model.predict(X)...       # predicted grade in this elective
        confidence  = max(model.predict_proba(X)[0]) * 100   # how sure the model is (%)

        grade_score = (11 - grade_class) / 11 * 100          # better grade -> higher score
        fit = round(0.75 * grade_score + 0.25 * confidence)  # BLEND grade + confidence
        predictions.append({'subject': col, 'score': fit, 'confidence': confidence, ...})

    ranked = sorted(predictions, key=lambda p: -p['score'])  # best fit first
    return {'recommended': ranked[:top_n], 'all_predictions': ranked}
```

**Important detail — missing marks:** if a student leaves a subject blank/0, we don't feed
0 (that would mean "failed"). Instead `_encode_student_row` fills it with that subject's
**median** mark from training, so predictions stay sensible:
```python
val = marks.get(col) or bundle['feature_medians'][col]   # fill gaps with the median
row[col] = encode_grade(val)
```

## 5.10 The fit score formula (why it's smart)
`fit = 0.75 × grade_score + 0.25 × confidence`
- `grade_score` = how good the predicted grade is (A+ → 100, fail → 0).
- `confidence` = how **sure** the model is (its own probability).

Why blend them? Two electives might both predict a good grade, but if the model is far more
**confident** about one, that one should rank higher. This also stops many electives from
showing the **same** score (which was confusing before). Grade counts more (0.75) so a better
grade still leads.

## 5.11 Explainability — the "why" panel
We don't want a black box. For each elective we show **which of the student's subjects the
model relied on most**. XGBoost tells us this via `feature_importances_`:

```python
def explain_prediction(marks, bundle, code, top_n=5):
    importances = bundle['models'][code].feature_importances_   # how much each subject mattered
    order = np.argsort(importances)[::-1][:top_n]               # top subjects
    # for each, show the subject, its weight %, and the student's grade in it
```
So the UI can say: *"This elective relies most on Machine Learning (weight 7%), where you
got an A."* That's genuine **Explainable AI (XAI)**.

## 5.12 From electives to FIELDS
Each elective belongs to a **field** (e.g. Generative AI → Conversational AI). To rank
**fields**, we **average** the fit scores of the electives in each field
(`recommended_fields()` in `thapar_map.py`). The field with the best average is the student's
top specialization.

## 5.13 Accuracy & "why XGBoost?"
Each model's accuracy is measured on held-out test data (~**79% average**). We chose XGBoost
because it is the strongest, most popular model for tabular (table) data and gave the best
results in our comparison. (If asked "why not Random Forest / SVM / Neural Net?" → *"We
compared them; XGBoost was the most accurate for this data."*)

---

# PART 6 — The web app (Flask back end)

`app.py` defines **routes** — each route is a URL the user can visit, and a function that runs.

Example — the login route:
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = store.get_user_by_email(request.form["email"])
        if user and check_password_hash(user["password_hash"], request.form["password"]):
            session["user_id"] = user["id"]          # remember who is logged in
            return redirect(url_for("dashboard"))
    return render_template("login.html")
```

How a request flows:
1. Browser visits a URL (e.g. `/recommend`).
2. Flask runs that route's function.
3. The function reads/writes the **database** (`store.*`) and calls the **ML engine** (`ml_core.*`).
4. It fills an **HTML template** with the results and sends the page back.

`session` keeps the user logged in. Passwords are **hashed** (never stored as plain text) with
Werkzeug's `generate_password_hash` / `check_password_hash`.

---

# PART 7 — The database (MongoDB)

`store.py` is the only file that talks to the database. MongoDB stores **documents**
(like JSON) in **collections** (like tables):
- `users`, `results` (marks), `recommendations`, `enrollments`, `progress`, `audit_log`.

Example:
```python
def create_user(name, email, password_hash, consent, created_at):
    uid = _next_id("users")
    db().users.insert_one({"_id": uid, "name": name, "email": email,
                           "password_hash": password_hash, ...})
    return uid
```
In production it connects to **MongoDB Atlas** (a free cloud database) via `MONGODB_URI`.
For tests it uses **mongomock** (a fake in-memory MongoDB) so no server is needed.

---

# PART 8 — The AI advisor + study assistant

Two AI features, both in `advisor.py` / `ai_assist.py`:
1. **🎓 Specialization Advisor** (floating chat): answers "which specialization should I pick?"
   using the student's **own recommendation** + a knowledge base of the 12 tracks.
2. **AI Study Assistant** (on each course page): generates a 4-week study plan.

Both work in **two modes**:
- **No API key** → a **rule-based** engine (keyword + intent matching). Always works, free.
- **With an API key** (`LLM_PROVIDER` + `LLM_API_KEY`) → a real **LLM** (we use **Groq**, which
  is free) writes a genuine conversational answer.

```python
def answer(question, ctx):
    if ai_assist.llm_enabled():      # a key is set?
        try: return _llm_answer(question, ctx)   # real AI
        except Exception: pass                    # if it fails, fall back
    return _rule_based(question, ctx)             # rule-based answer
```

---

# PART 9 — "Senior developer" / production features

To make it realistic and safe, we added:
- **Input validation** — marks are clamped to 0–100; bad values ignored.
- **CSRF protection** (Flask-WTF) — stops forged form submissions.
- **Login rate-limiting** — max 5 failed logins per 10 min (stops password guessing).
- **Audit log** — records admin actions (who did what, when).
- **Consent + privacy** — the student must agree at registration (DPDP-style).
- **Dataset validation** before retraining (checks columns, rows, 0–100 range).
- **Password hashing**, secure cookies, custom 404 page, 5 MB upload cap.

---

# PART 10 — Deployment (making it a real website)

- Code lives on **GitHub**.
- **Render** watches GitHub and auto-builds the app in a **Docker** container
  (`Dockerfile.web`) — it installs dependencies, builds the dataset, trains the models, and
  runs the app with **gunicorn**.
- The database is **MongoDB Atlas** (free cloud tier).
- **GitHub Actions** (`.github/workflows/ci.yml`) runs the tests automatically on every push.
- Live URL: **https://edupath-portal.onrender.com**.

Secrets (database URL, admin password, AI key) are **environment variables** — never written
in the code.

---

# PART 11 — Testing

`portal/tests/` has **39 automated tests** (pytest). They check registration, login,
entering marks, recommendations, the advisor, admin actions, security, and the ML functions.
They run on **mongomock** so no database or internet is needed.
```powershell
cd portal
python -m pytest -q      # -> 39 passed
```

---

# PART 12 — How to run it

```powershell
# one-time: build dataset + train models
python portal\build_thapar_dataset.py
python portal\train_models.py
# start the website
python portal\app.py        # -> http://127.0.0.1:5000
```

---

# PART 13 — VIVA / Evaluation Q&A (memorize these)

**Q: What is your project?**
A: A web app that recommends elective subjects and specialization fields to students based on
their past marks, using machine learning.

**Q: Which ML model and why?**
A: XGBoost — one model per elective (14 total). It's the strongest model for tabular data and
gave the best accuracy (~79%) in our comparison.

**Q: How does it predict?**
A: We convert marks into grade categories, balance the data with SMOTE, train an XGBoost model
per elective, then for a new student each model predicts their grade; we combine the predicted
grade and the model's confidence into a fit score and rank the electives.

**Q: What is SMOTE / why use it?**
A: It balances the data by creating synthetic examples of rare grades so the model doesn't
ignore them.

**Q: Is it a black box?**
A: No — we show feature importances ("why" panel): which subjects the model relied on for each
elective, with the student's grade in them. That's Explainable AI.

**Q: What's the tech stack?**
A: Flask (backend), XGBoost/scikit-learn (ML), MongoDB (database), HTML/Jinja/CSS (frontend),
Docker + Render (deployment), pytest (testing), plus an optional LLM chatbot (Groq).

**Q: How is it deployed?**
A: On Render, in a Docker container, auto-deployed from GitHub, with a MongoDB Atlas database
and GitHub Actions CI running the tests.

**Q: Where did the data come from?**
A: It's a relabeled stand-in dataset (real grade patterns on Thapar course codes) — a
demonstration dataset, disclosed in the app. The method is real; the labels are a stand-in.

**Q: How do you handle a student who didn't take some subjects?**
A: Blank/0 marks are treated as "not taken" and filled with the subject's median from the
training data, so predictions stay accurate.

---

# PART 14 — Who explains what (3-person split)

So each of us can confidently own a part in the evaluation:

| Person | Owns & explains | Sections to master |
|---|---|---|
| **Member 1 — ML** | the data, grade encoding, SMOTE, XGBoost, training, prediction, fit score, explainability | Part 5 (all) + ML viva questions |
| **Member 2 — Backend & DB** | Flask routes, request flow, sessions/login, MongoDB/store.py, security features, deployment | Parts 6, 7, 9, 10, 11 |
| **Member 3 — Frontend & AI** | the pages/user journey, the course catalogue, the AI advisor + study assistant, the UX | Parts 2, 3, 8 |

Everyone should read **Parts 1, 4, and 13** (the big picture + viva answers).

---

# PART 15 — Honest reminders
- The dataset is a **relabeled stand-in**, disclosed in the app — say so plainly if asked.
- The AI chatbot is **rule-based without an API key**, and real AI (Groq) with one.
- The free hosting (Render) **sleeps** after 15 min — the first visit after idle takes ~50s to
  wake up. Open the live link a minute before demoing.

That's the whole project. Read it once more and you can explain any part of it. 💪
