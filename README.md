# EduPath — Course & Field Recommendation System

A web application that recommends the best **elective subjects** and **specialization
fields** to a B.E. (CSE) student, based on the marks they scored in their earlier
subjects. It uses **machine learning** (one XGBoost model per elective) and adds a
course catalogue, progress tracking and an **AI advisor chatbot**.

> 🌐 Live demo: https://edupath-portal.onrender.com
> 📖 Full project explanation for the team: see [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md)

---

## What it does
1. A student **registers** and **enters their marks**.
2. 14 trained ML models **predict** how well they'd do in each advanced elective.
3. The app **ranks** them and shows the student their **best-fit electives and fields**,
   with a plain-English reason for each.
4. The student can explore **courses** (syllabus, resources, progress) and ask the
   **🎓 AI advisor** which specialization to pick.

## Tech stack
| Layer | Technology |
|---|---|
| Front end | HTML + Jinja2 templates + CSS |
| Back end | Python **Flask** |
| Machine learning | **XGBoost**, scikit-learn, imbalanced-learn (SMOTE) |
| Database | **MongoDB** (Atlas in production, mongomock for tests) |
| AI assistant | LLM via **Groq / Anthropic / OpenAI** (optional), rule-based fallback |
| Deployment | **Docker**, **Render**, GitHub Actions CI |
| Tests | **pytest** (39 tests) |

## Run it locally (Windows)
```powershell
# 1. build the dataset and train the models (first time only)
C:\Users\HP\co544venv\Scripts\python.exe portal\build_thapar_dataset.py
C:\Users\HP\co544venv\Scripts\python.exe portal\train_models.py

# 2. start the web app
C:\Users\HP\co544venv\Scripts\python.exe portal\app.py
```
Then open **http://127.0.0.1:5000**.

Run the tests:
```powershell
cd portal
C:\Users\HP\co544venv\Scripts\python.exe -m pytest -q
```

## Project layout
```
portal/            the whole web app
  app.py           Flask routes (register, login, results, recommend, courses, admin…)
  ml_core.py       the ML engine (training + prediction)
  store.py         MongoDB data layer
  advisor.py       AI specialization-advisor chatbot
  ai_assist.py     LLM helper (study plans + advisor)
  thapar_map.py    maps dataset columns to Thapar course codes + fields
  curriculum.py    the B.E.(CSE) scheme
  courses_data.py  course catalogue (syllabus, resources)
  templates/       the HTML pages
  static/css/      the styling
  tests/           pytest suite
data/              the training dataset (a relabeled stand-in — see the note below)
Dockerfile.web     container for deployment
render.yaml        Render deployment blueprint
```

## Data note (please keep this)
The model is trained on a **relabeled stand-in dataset** — real student grade patterns
mapped onto Thapar course codes. It is a **demonstration dataset, not real Thapar
records**. The machine-learning method is genuine; only the data labels are a stand-in.

See **[`DEPLOY.md`](DEPLOY.md)** to deploy it and **[`OWN_IT.md`](OWN_IT.md)** to set up
your own database and hosting.
