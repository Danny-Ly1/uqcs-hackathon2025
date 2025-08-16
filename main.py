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

@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
    # This will run the Flask app on port 5001