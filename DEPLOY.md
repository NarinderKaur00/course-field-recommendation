# Deploying the EduPath portal

The web app is container-ready. Deploy it **under your own GitHub + hosting
account** — the steps below use **your** credentials and **your** API key. (I
can't log into your accounts for you.)

---

## Option A — Render.com (free, recommended, uses `render.yaml`)

1. **Push this project to your own GitHub repo.**
   ```bash
   git init
   git add .
   git commit -m "EduPath portal"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. Go to **https://render.com** → sign in with **your** account → **New +** →
   **Blueprint** → connect your repo. Render reads `render.yaml` automatically.

3. **Create a free MongoDB Atlas database** (this is where student accounts,
   results and recommendations are stored permanently):
   - Go to **https://www.mongodb.com/atlas** → sign up → create a **free M0
     cluster**.
   - **Database Access** → add a database user (username + password).
   - **Network Access** → add IP `0.0.0.0/0` (allow from anywhere, so Render can
     reach it).
   - **Connect → Drivers** → copy the connection string. It looks like:
     `mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
     Put your real username/password into it — that's your `MONGODB_URI`.

4. Set the environment variables it asks for (in the Render dashboard):
   | Variable | What to put |
   |---|---|
   | `SECRET_KEY` | leave as auto-generated |
   | `ADMIN_USER` | your admin username (e.g. `admin`) |
   | `ADMIN_PASS` | **your own** strong admin password |
   | `MONGODB_URI` | **your own** Atlas connection string (from step 3) |
   | `MONGODB_DB` | `edupath` (or any database name you like) |
   | `LLM_PROVIDER` | `anthropic` or `openai` (or `none` to use the built-in planner) |
   | `LLM_API_KEY` | **your own** API key (only if you set a provider) |
   | `LLM_MODEL` | optional model id |

5. Click **Apply / Deploy**. First build takes a few minutes (it installs deps,
   builds the dataset and trains the models inside the image). You'll get a URL
   like `https://edupath-portal.onrender.com` — **that's your resume link.**

> Storage: the app uses **MongoDB Atlas** (step 3), so student accounts and data
> survive redeploys and restarts. If `MONGODB_URI` is left unset the app falls
> back to an in-memory database — fine for a quick demo, but it resets on every
> restart, so always set `MONGODB_URI` for a real deployment.

---

## Option B — Run the Docker image anywhere

```bash
# build
docker build -f Dockerfile.web -t edupath-portal .

# run (set your own secrets/keys)
docker run -p 8000:8000 \
  -e SECRET_KEY="change-me" \
  -e ADMIN_USER="admin" -e ADMIN_PASS="your-strong-pass" \
  -e MONGODB_URI="mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/" \
  -e MONGODB_DB="edupath" \
  -e LLM_PROVIDER="anthropic" -e LLM_API_KEY="sk-ant-..." \
  edupath-portal
```
Open **http://localhost:8000**. Works on Railway, Fly.io, AWS, GCP, etc.

---

## Local development (Windows, no Docker)
```powershell
C:\Users\HP\co544venv\Scripts\python.exe portal\app.py
```
(gunicorn is Linux-only; it's used only inside the container/host.)

## Enabling the AI Study Assistant
Without a key it uses the **built-in planner** (always works). To use a real
LLM, set `LLM_PROVIDER` + `LLM_API_KEY` (and optionally `LLM_MODEL`). Your key
stays in your environment — it is never committed to the repo.

## Tests / CI
`.github/workflows/ci.yml` runs the pytest suite and builds the Docker image on
every push to your GitHub repo.
```powershell
cd portal
C:\Users\HP\co544venv\Scripts\python.exe -m pytest -q
```
