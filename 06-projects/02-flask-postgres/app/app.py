import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/users")
def list_users():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users ORDER BY id")
            rows = cur.fetchall()
    users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
    return jsonify(users)

@app.route("/users/<int:user_id>")
def get_user(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": row[0], "name": row[1], "email": row[2]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
