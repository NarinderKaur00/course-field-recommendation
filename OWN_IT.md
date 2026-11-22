# Make this project 100% yours

This guide hands you full ownership: your own database you can log into and
query, your own admin account, your own code history, and (optionally) your own
live URL. Nobody else holds the keys.

---

## 1. Your own database (full data access) — MongoDB Atlas, free

1. Go to **https://www.mongodb.com/atlas** → sign up with **your** email.
2. Create a free **M0** cluster (any cloud/region).
3. **Database Access** → *Add New Database User* → pick a username + password
   (write them down — these are *your* DB credentials).
4. **Network Access** → *Add IP Address* → `0.0.0.0/0` (allow from anywhere).
5. **Connect → Drivers** → copy the connection string. It looks like:
   ```
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   Replace `<user>`/`<password>` with the ones from step 3.

You now **own the database**. Anytime, log into Atlas → *Browse Collections* to
see every student account, result and recommendation yourself.

---

## 2. Point the app at your database

1. In the `portal` folder, copy the template:
   ```powershell
   Copy-Item portal\.env.example portal\.env
   ```
2. Open `portal\.env` and fill in **your** values:
   ```
   MONGODB_URI=mongodb+srv://you:yourpass@cluster0.xxxxx.mongodb.net/...
   MONGODB_DB=edupath
   SECRET_KEY=<any long random string>
   ADMIN_USER=<your admin name>
   ADMIN_PASS=<your strong password>
   ```
   `.env` is git-ignored, so these secrets never leave your machine.

---

## 3. Run it locally

```powershell
.\portal\run_local.ps1
```
(or `C:\Users\HP\co544venv\Scripts\python.exe portal\app.py`)

Open **http://127.0.0.1:5000**. Register a student, enter marks, get a
recommendation — then refresh Atlas and watch the data appear in *your* cluster.
Because it's real MongoDB now, your data **survives restarts**.

Log into the admin panel at **/admin/login** with the `ADMIN_USER` / `ADMIN_PASS`
you set — full student management, audit log and JSON backup are yours.

---

## 4. Your own code history (shows your name)

```powershell
git init
git config user.name  "Your Name"
git config user.email "your@email.com"
git add .
git commit -m "EduPath — course & field recommendation portal"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```
Now the repo and every commit are under **your** GitHub identity.

> `.gitignore` already excludes `.env`, `*.db`, `models/` and caches, so no
> secrets or build artifacts get pushed.

---

## 5. Your own live URL (optional) — Render

Follow **DEPLOY.md → Option A**. You connect *your* GitHub repo, paste the same
`MONGODB_URI` / `ADMIN_PASS` into *your* Render dashboard, and get a link like
`https://<you>.onrender.com`. Same Atlas database powers local + live.

---

## What stays honest

The **dataset** is a relabeled stand-in (real grade patterns wearing Thapar
course codes), disclosed in the UI and `data/Grade_Thapar_Students_NOTE.txt`.
That's about the *data's origin*, not ownership — the application, database and
deployment are entirely yours. If you ever get real institutional data with the
same columns, drop it in and retrain; nothing else changes.
