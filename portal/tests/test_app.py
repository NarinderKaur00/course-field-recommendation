"""Integration tests for the EduPath portal."""
from conftest import median_marks


# ---- auth -----------------------------------------------------------------
def test_login_required_redirect(client):
    r = client.get("/dashboard", follow_redirects=True)
    assert b"Sign in" in r.data or b"Sign In" in r.data


def test_register_and_login(client):
    r = client.post("/register", data={"name": "Jane", "email": "jane@test.com",
                                       "password": "1234", "confirm": "1234", "consent": "1"},
                    follow_redirects=True)
    assert r.status_code == 200
    r = client.post("/login", data={"email": "jane@test.com", "password": "1234"},
                    follow_redirects=True)
    assert b"Jane" in r.data


def test_bad_login(client):
    client.post("/register", data={"name": "Jane", "email": "jane@test.com",
                                   "password": "1234", "confirm": "1234", "consent": "1"},
                follow_redirects=True)
    r = client.post("/login", data={"email": "jane@test.com", "password": "nope"},
                    follow_redirects=True)
    assert b"Invalid email or password" in r.data


# ---- recommendation flow --------------------------------------------------
def test_recommendation_flow(auth_client):
    data = median_marks()
    data["action"] = "recommend"
    r = auth_client.post("/results", data=data, follow_redirects=True)
    assert r.status_code == 200
    assert b"Recommended electives for you" in r.data
    assert b"Why these electives" in r.data          # explainability
    assert b"Top electives at a glance" in r.data      # compact chart
    assert b"View course" in r.data                  # course links


def test_history_after_recommendation(auth_client):
    data = median_marks(); data["action"] = "recommend"
    auth_client.post("/results", data=data, follow_redirects=True)
    r = auth_client.get("/history")
    assert b"Recommendation #" in r.data


# ---- courses & learning ---------------------------------------------------
def test_courses_hub(auth_client):
    r = auth_client.get("/courses")
    assert b"Data Structures" in r.data and b"Machine Learning" in r.data


def test_course_detail_and_resources(auth_client):
    r = auth_client.get("/course/UCS301")
    assert b"Linked lists" in r.data and b"Coursera" in r.data


def test_ai_study_plan_fallback(auth_client):
    # No LLM key in tests -> built-in planner must still produce a plan
    r = auth_client.post("/course/UCS301/studyplan", follow_redirects=True)
    assert b"Week 1" in r.data and b"study plan" in r.data.lower()


def test_enroll_and_progress(auth_client):
    auth_client.post("/course/UCS301/progress", data={"t0": "on", "t1": "on"},
                     follow_redirects=True)
    r = auth_client.get("/my-learning")
    assert b"UCS301" in r.data and b"Average progress" in r.data


# ---- reference pages ------------------------------------------------------
def test_curriculum_and_fields(auth_client):
    assert b"Operating System" in auth_client.get("/curriculum").data
    assert b"Data Science" in auth_client.get("/fields").data


# ---- admin ----------------------------------------------------------------
def test_admin_protected(client):
    r = client.get("/admin", follow_redirects=True)
    assert b"Admin sign in" in r.data


def test_admin_dashboard_and_retrain(admin_client):
    r = admin_client.get("/admin")
    assert b"Admin Dashboard" in r.data and b"Registered students" in r.data
    r = admin_client.post("/admin/retrain", follow_redirects=True)
    assert b"Models retrained" in r.data


def test_admin_delete_student(client):
    # register a student, then delete via admin
    client.post("/register", data={"name": "Gone", "email": "g@test.com",
                                   "password": "1234", "confirm": "1234", "consent": "1"},
                follow_redirects=True)
    client.post("/admin/login", data={"username": "admin", "password": "admin123"},
                follow_redirects=True)
    r = client.get("/admin")
    assert b"Gone" in r.data
    # user id 1 is the only student
    r = client.post("/admin/student/1/delete", follow_redirects=True)
    assert b"Deleted student" in r.data
