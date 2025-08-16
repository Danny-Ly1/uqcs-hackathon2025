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


# Helper function to check db
def get_all():
    with connect_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM users""")
            return cursor.fetchall()
        
# Helper function to execute SQL commands
def execute_command(query: str, args: tuple[str], returning: bool):
    with connect_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            results = cursor.fetchone()
            if returning:
                if results == None:
                    return "SOMETHING WENT VERY WRONG/DOES NOT EXIST"
                return results
            conn.commit()


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
def add_blocked_url(user_id: int, url: str):
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

"""
Updates the groupID for the user
"""
UPDATE_GROUPID_COMMAND = """UPDATE Users SET groupID = %s WHERE userID = %s RETURNING groupID"""
def updateGroupID(user_id: int, group_id: int):
    results = execute_command(UPDATE_GROUPID_COMMAND, (group_id, user_id), True)
    return results

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
                    name VARCHAR(50) UNIQUE,
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

"""
Adds a user to the database
"""
ADD_USER_COMMAND = """INSERT INTO users (username, password) VALUES (%s, %s) RETURNING userid, username"""
def add_user(username: str, password: str) -> int:
    results = execute_command(ADD_USER_COMMAND, (username, password), True)
    return results

"""
Gets a user from the database
"""
GET_USER_COMMAND = """SELECT userid, username, groupid FROM users WHERE userid = %s"""
def get_user(userid: int):
    user_info = execute_command(GET_USER_COMMAND, (userid,), True)
    return user_info

"""
Checks the user credentials against the db
"""
CHECK_LOGIN_COMMAND = """SELECT userid, username FROM users WHERE username = %s AND password = %s"""
def check_login(username: str, password: str):
    results = execute_command(CHECK_LOGIN_COMMAND, (username, password), True)
    return results

"""
Adds a new group to the db
"""
ADD_GROUP_COMMAND = """INSERT INTO groups (links) VALUES (%s) RETURNING groupID"""
def add_group():
    results = execute_command(ADD_GROUP_COMMAND, ([],), True)
    return results
