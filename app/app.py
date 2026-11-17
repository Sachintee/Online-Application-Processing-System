import os, time
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "applications"),
        user=os.getenv("POSTGRES_USER", "appuser"),
        password=os.getenv("POSTGRES_PASSWORD", "change-me"),
        connect_timeout=3)

def init_db():
    for attempt in range(20):
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY, applicant_name VARCHAR(120) NOT NULL,
                    email VARCHAR(255) NOT NULL, program VARCHAR(120) NOT NULL,
                    status VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            print("Database ready")
            return
        except psycopg2.OperationalError:
            if attempt == 19: raise
            time.sleep(2)

init_db()

@app.get("/")
def home():
    return jsonify(service="Online Application Processing System", status="running")

@app.get("/health")
def health():
    try:
        with connect() as conn:
            with conn.cursor() as cur: cur.execute("SELECT 1")
        return jsonify(status="healthy", database="connected"), 200
    except Exception:
        return jsonify(status="unhealthy", database="unavailable"), 503

@app.post("/api/applications")
def create_application():
    d = request.get_json(silent=True) or {}
    name, email, program = [str(d.get(k, "")).strip()
                            for k in ("applicant_name", "email", "program")]
    if not all((name, email, program)):
        return jsonify(error="applicant_name, email, and program are required"), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify(error="A valid email address is required"), 400
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""INSERT INTO applications (applicant_name,email,program)
            VALUES (%s,%s,%s) RETURNING *""", (name,email,program))
            row = cur.fetchone()
    return jsonify(dict(row)), 201

@app.get("/api/applications")
def list_applications():
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM applications ORDER BY created_at DESC")
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])

@app.patch("/api/applications/<int:app_id>/status")
def update_status(app_id):
    d = request.get_json(silent=True) or {}
    status = str(d.get("status", "")).upper()
    if status not in {"UNDER_REVIEW", "APPROVED", "REJECTED"}:
        return jsonify(error="Use UNDER_REVIEW, APPROVED, or REJECTED"), 400
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("UPDATE applications SET status=%s WHERE id=%s RETURNING *",
                        (status, app_id))
            row = cur.fetchone()
    if row is None: return jsonify(error="Application not found"), 404
    return jsonify(dict(row))
