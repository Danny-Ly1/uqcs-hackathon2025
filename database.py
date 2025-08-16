import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

GROUP_ID_INDEX=3

GET_GROUP_ID = """SELECT groupid FROM users WHERE userid = %s"""
APPEND_URL = """UPDATE groups SET links = ARRAY_APPEND(links, %s) WHERE groupid = %s"""
FILTER_DUP_URL = """UPDATE groups SET links = (SELECT array_agg(DISTINCT l ORDER BY l) FROM unnest(links) as l)"""

CLEAR_URL_ARRAY = """UPDATE groups SET links = %s WHERE groupid = %s"""
CHECK_VALID_URL = """SELECT COUNT(*) FROM groups, unnest(links) AS element WHERE element = %s AND groupid = %s """

REDUCE_POINTS = """UPDATE users SET points = points - %s WHERE userid = %s"""
SET_POINTS = """UPDATE users SET points = %s WHERE userid = %s"""

SET_WEBHOOK = """UPDATE groups SET webhookurl = %s WHERE groupid = %s"""
GET_WEBHOOK = """SELECT webhookurl FROM groups WHERE groupid = %s"""

INIT_USER_TABLE = """CREATE TABLE IF NOT EXISTS users (
                    userid SERIAL PRIMARY KEY,
                    groupid INT,
                    username VARCHAR(50) UNIQUE,
                    password VARCHAR(30),
                    points INT DEFAULT 100,
                    webhookurl TEXT
                    )
                    """

INIT_GROUP_TABLE = """
                    CREATE TABLE IF NOT EXISTS groups (
                    groupid SERIAL PRIMARY KEY,
                    links TEXT[],
                    elapsedtime BIGINT
                    )
                    """

DROP_TABLE = """
            DROP TABLE users;
            DROP TABLE groups;
            """

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
            # cursor.execute("""SELECT * FROM users WHERE username = 'bob'""")
            cursor.execute("""SELECT * FROM groups""")
            return cursor.fetchall()
        
# Helper function to execute SQL commands
def execute_command(query: str, args: tuple[str], returning: bool):
    with connect_database() as conn:
        try: 
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                if returning:
                    results = cursor.fetchone()
                    if results == None:
                        return "SOMETHING WENT VERY WRONG/DOES NOT EXIST"
                    return results
                conn.commit()
        except psycopg2.ProgrammingError as e:
            print(f"Database returned error: {e}, aborting...")


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
    else: 
      return ""
      
    return url

"""
Add new blocked url
"""
def add_blocked_url(user_id: int, url: str):
    group_id = execute_command(GET_GROUP_ID, (user_id, ), True)
    trimmed = url_trimmer(url)
    if not trimmed:
      print("URL not supported, abandoning addition")
    execute_command(APPEND_URL, (trimmed, group_id), False)
    execute_command(FILTER_DUP_URL, (trimmed, group_id), False)


"""
Clears array of blocked urls
"""
def clear_url_all(user_id: int):
    group_id = execute_command(GET_GROUP_ID, (user_id, ), True)
    execute_command(CLEAR_URL_ARRAY, ([], group_id), False)

"""
Check if url is in blocklist
"""
def check_url(user_id, url: str):
    trimmed = url_trimmer(url) 
    if not trimmed:
      print("URL not supported, abandoning check")
    group_id = execute_command(GET_GROUP_ID, (user_id, ), True)
    valid_url = execute_command(CHECK_VALID_URL, (trimmed, group_id), True)
    if valid_url:
        print("block ts")
    else:
        print("not blocked")


"""
Reduces points of user
"""
def reduce_points(user_id: int):
    REDUCTION_AMOUNT = 10
    execute_command(REDUCE_POINTS, (REDUCTION_AMOUNT, user_id), False)

"""
Sets new points for user
"""
def set_point(user_id: int, points: int):
    execute_command(SET_POINTS, (points, user_id), False)

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
    execute_command(INIT_USER_TABLE, None, False)
    execute_command(INIT_GROUP_TABLE, None, False)

def drop_database():
    execute_command(DROP_TABLE, None, False)

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

"""
Set epoch time in the db
"""
SET_EPOCH_TIME_COMMAND = """UPDATE Groups SET elapsedtime = %s, lockedin = true WHERE groupID = %s"""
def set_lock_in(groupID: int, epoch_time: int):
    execute_command(SET_EPOCH_TIME_COMMAND, (epoch_time, groupID), False)

"""
Obtain epoch time and lock in state
"""
GET_LOCK_STATUS = """SELECT lockedin FROM groups WHERE groupid = %s"""
def check_lock(userid):
    group_id = execute_command(GET_GROUP_ID, (userid, ), True)
    lock = execute_command(GET_LOCK_STATUS, (group_id, ), True)[0]
    print(lock)
    if lock == True:
        print("GETOUT")
    else:
        print("go ahead")

"""
Update lock in state and epoch timer
"""
REMOVE_LOCK_COMMAND = """UPDATE Groups SET lockedin = false WHERE groupID = %s"""
def remove_lock(groupid):
    execute_command(REMOVE_LOCK_COMMAND, (groupid, ), False)

def set_webhook(webhook: str, groupid):
  execute_command(ADD_WEBHOOK, (webhook, groupid), False);

def get_webhook(groupid):
  execute_command(GET_WEBHOOK, (groupid, ), False);
