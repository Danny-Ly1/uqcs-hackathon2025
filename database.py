import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

GROUP_ID_INDEX=3

GET_GROUP_ID = """SELECT groupid FROM users WHERE userid = %s"""

CHECK_VALID_URL = """SELECT COUNT(*) FROM groups, unnest(links) AS element WHERE element = %s AND groupid = %s """

REDUCE_POINTS = """UPDATE users SET points = points - %s WHERE userid = %s"""
SET_POINTS = """UPDATE users SET points = %s WHERE userid = %s"""

SET_WEBHOOK = """UPDATE users SET webhookurl = %s WHERE userid = %s"""
GET_WEBHOOK = """SELECT username, webhookurl FROM users WHERE userid = %s"""

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
                    elapsedtime BIGINT DEFAULT 0,
                    webhookurl TEXT
                    )
                    """

INIT_FILTER_TABLE = """
                    CREATE TABLE IF NOT EXISTS filters
                    linkid SERIAL PRIMARY KEY,
                    url TEXT,
                    groupid INT"""

DROP_TABLE = """
            DROP TABLE users;
            DROP TABLE groups;
            DROP TABLE filters;
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
ADD_URL_COMMAND = """INSERT INTO filters (url, groupid) VALUES (%s, %s) RETURNING linkid"""
def add_blocked_url(url: str, group_id: int):
    link_id = execute_command(ADD_URL_COMMAND, (url, group_id), True)
    return url, link_id


"""
Delete URL from db
"""
DELETE_URL_COMMAND = """DELETE FROM filters WHERE linkid = %s"""
def clear_one_url(link_id: int):
    execute_command(DELETE_URL_COMMAND, (link_id,), False)


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
SET_EPOCH_TIME_COMMAND = """UPDATE Groups SET elapsedtime = %s WHERE groupID = %s"""
GET_UPDATE_TIME = """SELECT elapsedtime FROM groups WHERE groupid = %s"""
def set_lock_in(groupID: int, epoch_time: int):
    execute_command(SET_EPOCH_TIME_COMMAND, (epoch_time, groupID), True)
    result = execute_command(GET_UPDATE_TIME, (groupID, ), True)
    return result

"""
Obtain epoch time and lock in state
"""
GET_LOCK_STATUS = """SELECT elapsedtime FROM groups WHERE groupid = %s"""
def check_lock(group_id):
    # group_id = execute_command(GET_GROUP_ID, (userid, ), True)
    lock = execute_command(GET_LOCK_STATUS, (group_id, ), True)
    return lock

"""
Remove lock
"""
REMOVE_LOCK_COMMAND = """UPDATE Groups SET elapsedtime = 0 WHERE groupID = %s"""
def remove_lock(groupid):
    execute_command(REMOVE_LOCK_COMMAND, (groupid, ), False)
"""
Insert webhook in the db
"""
def set_webhook(webhook: str, userid):
  execute_command(SET_WEBHOOK, (webhook, userid), False)

"""
Obtain the webhook from the db
"""
def get_webhook(userid):
    return execute_command(GET_WEBHOOK, (userid,), True)


"""
Obtain URL and groupID from db
"""
GET_URL_COMMAND = """SELECT groupid, links FROM Groups WHERE groupid = %s"""
def get_urls(group_id: int):
    results = execute_command(GET_URL_COMMAND, (group_id,), True)
    if results[1] is None:
        results = list(results)
        results[1] = []

    return tuple(results)



# Table initialise functions
def init_database():
    execute_command(INIT_USER_TABLE, None, False)
    execute_command(INIT_GROUP_TABLE, None, False)
    execute_command(INIT_FILTER_TABLE, None, False)

# Table drop function
def drop_database():
    execute_command(DROP_TABLE, None, False)



# Helper function to check db and debug
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
