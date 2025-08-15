import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

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
    cur.execute("""SELECT * FROM Groups""")
    results = cur.fetchall() # Fetches all output from above query
    print(results)

access_database()