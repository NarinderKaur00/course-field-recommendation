"""Edge-case & robustness tests — the 'what if the marks are weird' suite."""
import io
import json

from conftest import median_marks
import app as A
import store
from ml_core import encode_grade, recommend_for_student, explain_prediction


# ---- input validation on registration ------------------------------------
def test_register_rejects_bad_email(client):
    r = client.post("/register", data={"name": "X", "email": "not-an-email",
                                       "password": "1234", "confirm": "1234", "consent": "1"},
                    follow_redirects=True)
    assert b"valid email" in r.data


def test_register_rejects_password_mismatch(client):
    r = client.post("/register", data={"name": "X", "email": "x@test.com",
                                       "password": "1234", "confirm": "9999", "consent": "1"},
                    follow_redirects=True)
    assert b"do not match" in r.data


def test_register_rejects_short_password(client):
    r = client.post("/register", data={"name": "X", "email": "x@test.com",
                                       "password": "12", "confirm": "12", "consent": "1"},
                    follow_redirects=True)
    assert b"at least 4" in r.data


def test_register_rejects_duplicate_email(client):
    for _ in range(2):
        r = client.post("/register", data={"name": "X", "email": "dup@test.com",
                                           "password": "1234", "confirm": "1234", "consent": "1"},
                        follow_redirects=True)
    assert b"already registered" in r.data


# ---- marks edge cases ------------------------------------------------------
def _saved_marks(uid=1):
    row = store.get_results(uid)
    return json.loads(row["marks_json"]) if row else {}


def test_marks_out_of_range_are_clamped(auth_client):
    feats = A.BUNDLE["feature_columns"]
    data = {feats[0]: "999", feats[1]: "-50", feats[2]: "73"}
    auth_client.post("/results", data=data, follow_redirects=True)
    saved = _saved_marks()
    assert saved[feats[0]] == 100      # 999 -> clamped to 100
    assert saved[feats[1]] == 0        # -50 -> clamped to 0
    assert saved[feats[2]] == 73


def test_non_numeric_marks_are_ignored(auth_client):
    feats = A.BUNDLE["feature_columns"]
    data = {feats[0]: "abc", feats[1]: "", feats[2]: "80"}
    auth_client.post("/results", data=data, follow_redirects=True)
    saved = _saved_marks()
    assert feats[0] not in saved and feats[1] not in saved   # junk dropped
    assert saved[feats[2]] == 80


def test_recommend_without_results_redirects(auth_client):
    # fresh student, no marks entered yet
    r = auth_client.get("/recommend", follow_redirects=True)
    assert b"enter your academic results" in r.data.lower()


def test_recommendation_with_only_one_mark(auth_client):
    feats = A.BUNDLE["feature_columns"]
    r = auth_client.post("/results", data={feats[0]: "95", "action": "recommend"},
                         follow_redirects=True)
    assert r.status_code == 200 and b"Recommended electives" in r.data


# ---- 404s ------------------------------------------------------------------
def test_unknown_course_404(auth_client):
    assert auth_client.get("/course/NOPE999").status_code == 404


def test_unknown_recommendation_404(auth_client):
    assert auth_client.get("/recommendation/9999").status_code == 404


# ---- enroll / unenroll -----------------------------------------------------
def test_enroll_then_unenroll(auth_client):
    auth_client.post("/enroll/UCS301", follow_redirects=True)
    assert b"UCS301" in auth_client.get("/my-learning").data
    auth_client.post("/unenroll/UCS301", follow_redirects=True)
    assert b"UCS301" not in auth_client.get("/my-learning").data


# ---- admin: reset + bad retrain -------------------------------------------
def test_admin_reset_student(client):
    client.post("/register", data={"name": "Keep", "email": "k@test.com",
                                   "password": "1234", "confirm": "1234", "consent": "1"},
                follow_redirects=True)
    client.post("/login", data={"email": "k@test.com", "password": "1234"},
                follow_redirects=True)
    data = median_marks(); data["action"] = "recommend"
    client.post("/results", data=data, follow_redirects=True)
    client.get("/logout")
    client.post("/admin/login", data={"username": "admin", "password": "admin123"},
                follow_redirects=True)
    r = client.post("/admin/student/1/reset", follow_redirects=True)
    assert b"Reset" in r.data
    assert store.get_results(1) is None                 # results cleared
    assert store.get_user_by_id(1) is not None          # account kept


def test_admin_retrain_bad_csv_is_handled(admin_client):
    bad = (b"wrong,columns\n1,2\n")
    r = admin_client.post("/admin/retrain",
                          data={"dataset": (io.BytesIO(bad), "bad.csv")},
                          content_type="multipart/form-data", follow_redirects=True)
    # validated & rejected before training — no crash
    assert b"Dataset rejected" in r.data


# ---- pure ML unit tests ----------------------------------------------------
def test_encode_grade_boundaries():
    assert encode_grade(90) == 0       # A+
    assert encode_grade(85) == 1       # A (80-85)
    assert encode_grade(40) == 9       # D+
    assert encode_grade(10) == 11      # E (lowest)


def test_recommend_returns_all_electives():
    marks = {c: 70 for c in A.BUNDLE["feature_columns"]}
    out = recommend_for_student(marks, A.BUNDLE, top_n=5)
    assert len(out["all_predictions"]) == len(A.BUNDLE["target_subjects"])
    assert len(out["recommended"]) == 5
    # scores are a valid 0..100
    assert all(0 <= p["score"] <= 100 for p in out["all_predictions"])


def test_explain_returns_drivers():
    marks = {c: 70 for c in A.BUNDLE["feature_columns"]}
    drivers = explain_prediction(marks, A.BUNDLE, A.BUNDLE["target_subjects"][0], top_n=5)
    assert len(drivers) == 5
    assert all("importance" in d and "letter" in d for d in drivers)
