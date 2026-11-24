"""Tests for the production-hardening batch (#1–#5)."""
import io
import json

import app as A


# ---- #5 consent / privacy -------------------------------------------------
def test_register_requires_consent(client):
    r = client.post("/register", data={"name": "NoConsent", "email": "nc@test.com",
                                       "password": "1234", "confirm": "1234"},  # no consent
                    follow_redirects=True)
    assert b"accept the privacy policy" in r.data


def test_privacy_page_public(client):
    r = client.get("/privacy")
    assert r.status_code == 200 and b"Privacy Policy" in r.data


# ---- #3 rate limiting -----------------------------------------------------
def test_login_rate_limiting(client):
    A._LOGIN_FAILS.clear()
    for _ in range(5):
        client.post("/login", data={"email": "rl@test.com", "password": "x"},
                    follow_redirects=True)
    r = client.post("/login", data={"email": "rl@test.com", "password": "x"},
                    follow_redirects=True)
    assert b"Too many failed attempts" in r.data
    A._LOGIN_FAILS.clear()


# ---- #3 CSRF --------------------------------------------------------------
def test_csrf_blocks_tokenless_post(client):
    client.application.config["WTF_CSRF_ENABLED"] = True
    try:
        r = client.post("/login", data={"email": "a@b.com", "password": "x"},
                        follow_redirects=True)
        assert b"session expired" in r.data
    finally:
        client.application.config["WTF_CSRF_ENABLED"] = False


# ---- #4 audit log ---------------------------------------------------------
def test_audit_log_records_admin_actions(admin_client):
    admin_client.post("/admin/retrain", follow_redirects=True)
    r = admin_client.get("/admin")
    assert b"Audit log" in r.data
    assert b"retrain" in r.data or b"login" in r.data


def test_admin_backup_export(admin_client):
    r = admin_client.get("/admin/export")
    assert r.status_code == 200 and r.mimetype == "application/json"
    dump = json.loads(r.data)
    assert "users" in dump and "audit_log" in dump
    # password hashes must NOT be in the backup
    assert all("password_hash" not in u for u in dump["users"])


# ---- #1 dataset schema validation -----------------------------------------
def test_retrain_rejects_missing_columns(admin_client):
    bad = b"colA,colB\n1,2\n3,4\n"
    r = admin_client.post("/admin/retrain",
                          data={"dataset": (io.BytesIO(bad), "bad.csv")},
                          content_type="multipart/form-data", follow_redirects=True)
    assert b"Dataset rejected" in r.data and b"Missing" in r.data


def test_retrain_rejects_out_of_range(admin_client):
    feats = A.BUNDLE["feature_columns"]
    tgts = A.BUNDLE["target_subjects"]
    cols = feats + tgts
    header = ",".join(cols)
    # 40 rows, but one mark is 150 (out of range)
    rows = [",".join(["70"] * len(cols)) for _ in range(40)]
    rows[0] = ",".join(["150"] + ["70"] * (len(cols) - 1))
    csv = (header + "\n" + "\n".join(rows) + "\n").encode()
    r = admin_client.post("/admin/retrain",
                          data={"dataset": (io.BytesIO(csv), "oor.csv")},
                          content_type="multipart/form-data", follow_redirects=True)
    assert b"above 100" in r.data


def test_retrain_accepts_valid_dataset(admin_client):
    feats = A.BUNDLE["feature_columns"]
    tgts = A.BUNDLE["target_subjects"]
    cols = feats + tgts
    header = ",".join(cols)
    rows = [",".join(["65"] * len(cols)) for _ in range(40)]
    csv = (header + "\n" + "\n".join(rows) + "\n").encode()
    r = admin_client.post("/admin/retrain",
                          data={"dataset": (io.BytesIO(csv), "good.csv")},
                          content_type="multipart/form-data", follow_redirects=True)
    assert b"Dataset check passed" in r.data
