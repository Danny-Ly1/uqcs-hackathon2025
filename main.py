import os
import psycopg2
from flask import request, Flask, jsonify

DATA_HOST = os.getenv("DATA_HOST", "10.89.76.206")
DATABASE  = os.getenv("DATABASE", "myapp")
USER      = os.getenv("DB_USER", "postgres")
PASSWORD  = os.getenv("DB_PASSWORD", "1234")
PORT      = os.getenv("DB_PORT", "5432")

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=DATA_HOST, database=DATABASE, user=USER, password=PASSWORD, port=PORT
    )

# @app.get("/db-ping")
# def db_ping():
#     try:
#         with get_conn() as conn, conn.cursor() as cur:
#             cur.execute("SELECT 1;")
#             return jsonify({"db": "up"})
#     except Exception as e:
#         return jsonify({"db": "down", "error": str(e)}), 500

def ensure_schema():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        """)


@app.post("/user")
def create_user():
    # Validate JSON
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"message": "username and password must be strings"}), 400
    if len(username.strip()) == 0:
        return jsonify({"message": "username cannot be empty"}), 400
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
                (username, password) # In a real app, hash the password here
            )
            new_id = cur.fetchone()[0]
            # commit happens automatically due to context manager on the connection
        # Return id as a string to match your spec’s example
        return jsonify({"id": str(new_id), "username": username}), 201

    except Exception as e:
        # hide internal errors behind a 400 per your spec
        return jsonify({"message": "failed to create user"}), 400

if __name__ == "__main__":
    ensure_schema()  # make sure the table exists
    app.run(host="0.0.0.0", port=5001, debug=True)



@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
    # This will run the Flask app on port 5001