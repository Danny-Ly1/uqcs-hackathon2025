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
Trims url down to domain name. Supports com, org, net
"""
def url_trimmer(url: str) -> str:
    com_index = url.find(".com")
    org_index = url.find(".org")
    net_index = url.find(".net")

    www_index = url.find("www.") + 4 # Move past www

    if com_index:
        url = url[www_index:com_index]
    elif org_index:
        url = url[www_index:org_index]
    elif net_index:
        url = url[www_index:net_index]

    return url

"""
Add new blocked url
"""
def add_blocked_url(user_id: Optional[int], url: Optional[str]): # Make not optional later
    with connect_database() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT groupid FROM users WHERE userid = %s""", (user_id, ))
        group_id = cur.fetchall()[0] # extract value  
        
        url = url_trimmer(url)
        cur.execute("""UPDATE groups SET links = ARRAY_APPEND(links, %s) WHERE groupid = %s""", (url, group_id))
        cur.execute("""UPDATE groups SET links = (SELECT array_agg(DISTINCT l ORDER BY l) FROM unnest(links) as l)            
        """) # remove duplicates each pass. Case sensitive, typo sensitive
        conn.commit()

    conn.close()

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
Check if url is in blocklist
"""
def check_url(user_id, url: str):
    trimmed = url_trimmer(url)

    with connect_database() as conn:
        cur = conn.cursor()
        
        cur.execute("""SELECT groupID FROM users WHERE userID = %s""", (user_id, ))
        group_id = cur.fetchall()[0][0]
        cur.execute("""SELECT COUNT(*) FROM groups, unnest(links) AS element
                    WHERE element = %s AND groupid = %s """, (trimmed, group_id))
        count = cur.fetchall()[0][0]
        if count > 0:
            print("block ts")
        else:
            print("not blocked")
    conn.close()

"""
Reduces score of user
"""
def reduce_score(user_id: int):
    REDUCTION_AMOUNT = 10
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET score = score - %s WHERE userid = %s""", (REDUCTION_AMOUNT, user_id))
        
    conn.commit()
    conn.close()

"""
Sets new score for user
"""
def set_score(user_id: int, score: int):
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET score = %s WHERE userid = %s""", (score, user_id))
        
    conn.commit()
    conn.close()

def updateGroupID(user_id: int, group_id: int):
    with connect_to_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""UPDATE Users SET groupID = %s WHERE userID = %s""", (group_id, user_id))
            conn.commit()

# Table setup functions
"""
Creates new tables required
"""
def init_database():
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                    userid SERIAL PRIMARY KEY,
                    groupid INT,
                    username VARCHAR(25) UNIQUE,
                    password VARCHAR(50),
                    points INT DEFAULT 100
                    )
                    """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS groups (
                    groupid SERIAL PRIMARY KEY,
                    links TEXT[])
                    """)

    conn.commit()
    conn.close()

def drop_database():
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
                    DROP TABLE users;
                    DROP TABLE groups;
                    """)
        
    conn.commit()
    conn.close()

def add_user(name: str):
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO users (name)
                    VALUES (%s)
                    """, (name, ))
        
    conn.commit()
    conn.close()

def add_group():
    with connect_database() as conn:

        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO groups (links)
                    VALUES (%s)
                    """, ([], ))
        
    conn.commit()
    conn.close()
