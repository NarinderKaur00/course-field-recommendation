"""
store.py
--------
MongoDB data layer for the portal (replaces the old SQL db.py).

- Production / local: set MONGODB_URI (e.g. MongoDB Atlas) -> real MongoDB.
- Tests / no URI: falls back to an in-memory mongomock database (no server),
  so the whole test-suite runs offline.

Collections: users, results, recommendations, enrollments, progress,
audit_log, counters (for integer auto-increment ids).
"""
import os

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

DUPLICATE_ERRORS = (DuplicateKeyError,)

_client = None
_db = None


def configure(uri=None, use_mock=False, db_name=None):
    """(Re)connect. use_mock or a missing URI -> in-memory mongomock."""
    global _client, _db
    uri = uri or os.environ.get("MONGODB_URI", "")
    db_name = db_name or os.environ.get("MONGODB_DB", "edupath")
    if use_mock or not uri:
        import mongomock
        _client = mongomock.MongoClient()
    else:
        from pymongo import MongoClient
        # Point TLS at an up-to-date CA bundle (fixes the Windows "SSL
        # handshake failed" error when connecting to MongoDB Atlas).
        try:
            import certifi
            _client = MongoClient(uri, tlsCAFile=certifi.where())
        except Exception:
            _client = MongoClient(uri)
    _db = _client[db_name]
    _db.users.create_index("email", unique=True)
    return _db


def db():
    if _db is None:
        configure()
    return _db


def reset():
    """Drop everything (used by tests)."""
    d = db()
    for c in ("users", "results", "recommendations", "enrollments",
              "progress", "audit_log", "counters"):
        d[c].delete_many({})


def _next_id(name):
    doc = db().counters.find_one_and_update(
        {"_id": name}, {"$inc": {"seq": 1}},
        upsert=True, return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])


# ---- users ----------------------------------------------------------------
def create_user(name, email, password_hash, consent, created_at):
    uid = _next_id("users")
    db().users.insert_one({
        "_id": uid, "id": uid, "name": name, "email": email,
        "password_hash": password_hash, "consent": consent, "created_at": created_at,
    })
    return uid


def get_user_by_email(email):
    return db().users.find_one({"email": email})


def get_user_by_id(uid):
    return db().users.find_one({"_id": uid})


def list_users_desc():
    return list(db().users.find().sort("_id", -1))


def delete_user(uid):
    db().users.delete_one({"_id": uid})


# ---- results --------------------------------------------------------------
def upsert_results(uid, marks_json, updated_at):
    db().results.update_one(
        {"_id": uid},
        {"$set": {"user_id": uid, "marks_json": marks_json, "updated_at": updated_at}},
        upsert=True,
    )


def get_results(uid):
    return db().results.find_one({"_id": uid})


# ---- recommendations ------------------------------------------------------
def add_recommendation(uid, created_at, payload_json):
    rid = _next_id("recommendations")
    db().recommendations.insert_one({
        "_id": rid, "id": rid, "user_id": uid,
        "created_at": created_at, "payload_json": payload_json,
    })
    return rid


def get_recommendation(rec_id, uid):
    return db().recommendations.find_one({"_id": rec_id, "user_id": uid})


def list_recommendations(uid):
    return list(db().recommendations.find({"user_id": uid}).sort("_id", -1))


def latest_recommendation(uid):
    return db().recommendations.find_one({"user_id": uid}, sort=[("_id", -1)])


def count_recommendations(uid):
    return db().recommendations.count_documents({"user_id": uid})


def all_recommendations():
    return list(db().recommendations.find())


# ---- enrollments ----------------------------------------------------------
def enroll(uid, code, created_at):
    db().enrollments.update_one(
        {"_id": f"{uid}:{code}"},
        {"$setOnInsert": {"user_id": uid, "course_code": code, "created_at": created_at}},
        upsert=True,
    )


def unenroll(uid, code):
    db().enrollments.delete_one({"_id": f"{uid}:{code}"})


def enrolled_codes(uid):
    return {e["course_code"] for e in db().enrollments.find({"user_id": uid})}


# ---- progress -------------------------------------------------------------
def get_progress(uid, code):
    return db().progress.find_one({"_id": f"{uid}:{code}"})


def set_progress(uid, code, done_json):
    db().progress.update_one(
        {"_id": f"{uid}:{code}"},
        {"$set": {"user_id": uid, "course_code": code, "done_json": done_json}},
        upsert=True,
    )


# ---- audit ----------------------------------------------------------------
def add_audit(actor, action, detail, created_at):
    aid = _next_id("audit_log")
    db().audit_log.insert_one({
        "_id": aid, "actor": actor, "action": action,
        "detail": detail, "created_at": created_at,
    })


def recent_audit(limit=15):
    return list(db().audit_log.find().sort("_id", -1).limit(limit))


# ---- cross-collection helpers ---------------------------------------------
def purge_student(uid):
    d = db()
    d.results.delete_many({"user_id": uid})
    d.recommendations.delete_many({"user_id": uid})
    d.enrollments.delete_many({"user_id": uid})
    d.progress.delete_many({"user_id": uid})


def export_all():
    """Full backup (admin). Password hashes stripped."""
    d = db()
    out = {}
    for c in ("users", "results", "recommendations", "enrollments", "progress", "audit_log"):
        rows = []
        for doc in d[c].find():
            doc.pop("password_hash", None)
            rows.append(doc)
        out[c] = rows
    return out


def export_user(uid):
    """One student's data (privacy export)."""
    d = db()
    u = d.users.find_one({"_id": uid}, {"password_hash": 0})
    return {
        "profile": u or {},
        "results": list(d.results.find({"user_id": uid})),
        "recommendations": list(d.recommendations.find({"user_id": uid})),
        "enrollments": list(d.enrollments.find({"user_id": uid})),
        "progress": list(d.progress.find({"user_id": uid})),
    }
