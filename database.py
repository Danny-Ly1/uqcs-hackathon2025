import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

"""
Creates connection to database
"""
def connect_database():
    conn = psycopg2.connect(
        host=DATA_HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    return conn

"""
Adds a new url into the blocklist
"""
def add_blocked_url(user_id: Optional[int], link: Optional[str]): # Make not optional later
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
        SELECT * FROM groups
        """)
        groups = cur.fetchall() # Records result

        cur.execute("""
        SELECT * FROM users
        """)
        user_data = cur.fetchall()

        group_id = -1
        for i in user_data:
            if i[0] == user_id:
                group_id = i[GROUP_ID_INDEX]
                break       
        
        cur.execute("""UPDATE groups SET links = ARRAY_APPEND(links, %s) 
        WHERE groupid = %s""", (link, group_id)) # Append url to record
        conn.commit()

    conn.close()


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
