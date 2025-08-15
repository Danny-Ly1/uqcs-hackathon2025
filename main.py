from flask import Flask, request
import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

app = Flask(__name__)


@app.route('/')
def hello_world():
    host_ip = request.host
    return host_ip

"""
Usage: call access database when needing to change anything.

"""
def access_database():
    conn = psycopg2.connect(
        host=DATA_HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    
    cur = conn.cursor()
    # Insert SQL between the """
    cur.execute("""
    
    """)
    results = cur.fetchall() # Fetches all output from above query
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)