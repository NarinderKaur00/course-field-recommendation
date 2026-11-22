# How to run the Student Portal

A web app (student portal) built on top of the machine-learning engine.
It covers the full system: register, login, enter results, get elective
recommendations, and view history.

## One-time setup (already done on this machine)

```powershell
# Install Flask into the existing virtual environment
C:\Users\HP\co544venv\Scripts\python.exe -m pip install flask

# Train and save the 14 elective models (creates portal/models/bundle.joblib)
cd "C:\Users\HP\Downloads\e19-co544-course-and-field-recommendation-system-based-on-student-results-main\e19-co544-course-and-field-recommendation-system-based-on-student-results-main"
C:\Users\HP\co544venv\Scripts\python.exe portal\train_models.py
```

## Run the portal

```powershell
cd "C:\Users\HP\Downloads\e19-co544-course-and-field-recommendation-system-based-on-student-results-main\e19-co544-course-and-field-recommendation-system-based-on-student-results-main"
C:\Users\HP\co544venv\Scripts\python.exe portal\app.py
```

Then open **http://127.0.0.1:5000** in your browser.

1. **Sign Up** for an account
2. **Sign In**
3. Go to **My Results** → enter your marks → **Save & Recommend**
4. See your **Top electives** + full predicted-grade table
5. Check **Recommendations** (history) and **Model Insights** anytime

To stop the server: press **Ctrl + C** in the PowerShell window.

## If you see "Address already in use" (port 5000 busy)

Another copy is already running. Either use that browser tab, or stop the old
one first:

```powershell
Get-Process python | Stop-Process -Force
```

Then run the portal again.

## What's inside `portal/`

| File | Purpose |
| --- | --- |
| `ml_core.py` | Grade encoding, model training/saving, prediction + recommendation |
| `train_models.py` | Run once to train & save the 14 elective models |
| `app.py` | Flask web app (accounts, results, recommendations, history) |
| `templates/` | The HTML pages (login, dashboard, results, recommendation, …) |
| `static/css/style.css` | The portal styling |
| `models/bundle.joblib` | The saved trained models (created by `train_models.py`) |
| `portal.db` | SQLite database (created automatically on first run) |
