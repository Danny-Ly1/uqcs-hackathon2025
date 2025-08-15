import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

GROUP_ID_INDEX=3

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
Clears array of blocked urls
"""
def clear_url_all(user_id: int):
    with connect_database() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT groupID FROM users WHERE userID = %s""", (user_id, ))
        group_id = cur.fetchall()[0]
        
        cur.execute("""UPDATE groups SET links = %s WHERE groupid = %s""", ([], group_id)) # Clear tuple
        conn.commit()

    conn.close()

"""
Add new blocked url
"""
def add_blocked_url(user_id: Optional[int], link: Optional[str]): # Make not optional later
    with connect_database() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT groupid FROM users WHERE userid = %s""", (user_id, ))
        group_id = cur.fetchall()[0] # extract value  
        
        cur.execute("""UPDATE groups SET links = ARRAY_APPEND(links, %s) WHERE groupid = %s""", (link, group_id))
        cur.execute("""UPDATE groups SET links = (SELECT array_agg(DISTINCT l ORDER BY l) FROM unnest(links) as l)            
        """) # remove duplicates each pass. Case sensitive, typo sensitive
        conn.commit()

    conn.close()


def update_score():
    pass

def check_url():
    pass

def updateGroupID(user_id: int, group_id: int):
    with connect_to_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""UPDATE Users SET groupID = %s WHERE userID = %s""", (group_id, user_id))
            conn.commit()
