from typing import Any
import psycopg2
from queries import *

"""
Helper function to check db and debug
"""
def get_all() -> list[tuple]:
    with connect_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM groups""")
            return cursor.fetchall()

"""
Helper function to execute SQL commands
"""
def execute_command(query: str, args: tuple[str], returning: bool) -> list[tuple]:
    with connect_database() as conn:
        try: 
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                if returning:
                    results = cursor.fetchone()
                    # if results == None:
                    #     raise Exception("SOMETHING WENT 5 BIG BOOMS")
                    return results
                conn.commit()
        except psycopg2.ProgrammingError as e:
            print(f"Database returned error: {e}, aborting...")


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
# def url_trimmer(url: str) -> str:
#     com_index = url.find(".com")
#     org_index = url.find(".org")
#     net_index = url.find(".net")
#     www_index = url.find("www.") + 4 # Move past www
#     if com_index:
#         url = url[www_index:com_index]
#     elif org_index:
#         url = url[www_index:org_index]
#     elif net_index:
#         url = url[www_index:net_index]
#     else: 
#       return ""
#     return url


"""
Add new blocked url
"""
def add_blocked_url(url: str, group_id: int) -> tuple[str, list[tuple]]:
    link_id = execute_command(ADD_URL_COMMAND, (url, group_id), True)
    return url, link_id


"""
Delete URL from db
"""
def clear_one_url(link_id: int) -> None:
    execute_command(DELETE_URL_COMMAND, (link_id,), False)

"""
Search for url duplicates under same group id
"""
def url_duplicate_yes(group_id: int, url: str) -> list[tuple]:
    result = execute_command(CHECK_VALID_URL, (group_id, url), True)
    return result[0]


"""
Reduces points of user
"""
def reduce_points(user_id: int, points: int) -> None:
    execute_command(REDUCE_POINTS, (points, user_id), False)


"""
Sets new points for user
"""
def set_point(user_id: int, points: int) -> None:
    execute_command(SET_POINTS, (points, user_id), False)


"""
Updates the groupID for the user
"""
def updateGroupID(user_id: int, group_id: int) -> list[tuple]:
    results = execute_command(UPDATE_GROUPID_COMMAND, (group_id, user_id), True)
    return results

def group_exists(group_id: int):
    results = execute_command(CHECK_GROUP_ID, (group_id, ), True)
    return results[0]

"""
Adds a user to the database
"""
def add_user(username: str, password: str) -> list[tuple]:
    results = execute_command(ADD_USER_COMMAND, (username, password), True)
    return results

"""
Gets a user from the database
"""
def get_user(userid: int) -> list[tuple]:
    user_info = execute_command(GET_USER_COMMAND, (userid,), True)
    return user_info

"""
Checks the user credentials against the db
"""
def check_login(username: str, password: str):
    results = execute_command(CHECK_LOGIN_COMMAND, (username, password), True)
    return results

"""
Adds a new group to the db
"""
def add_group() -> list[tuple]:
    # with connect_database() as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute(ADD_GROUP_COMMAND)
    #         results = cursor.fetchone()
    # print(results)
    results = execute_command(ADD_GROUP_COMMAND, None, True)
    return results

"""
Set epoch time in the db
"""
def set_lock_in(groupID: int, epoch_time: int) -> list[tuple]:
    execute_command(SET_EPOCH_TIME_COMMAND, (epoch_time, groupID), True)
    result = execute_command(GET_UPDATE_TIME, (groupID, ), True)
    return result

"""
Obtain epoch time and lock in state
"""
def check_lock(group_id: int) -> list[tuple]:
    lock = execute_command(GET_LOCK_STATUS, (group_id, ), True)
    return lock

"""
Remove lock
"""
def remove_lock(groupid: int) -> None:
    execute_command(REMOVE_LOCK_COMMAND, (groupid, ), False)

"""
Insert webhook in the db
"""
def set_webhook(webhook: str, userid: int) -> None:
  execute_command(SET_WEBHOOK, (webhook, userid), False)

"""
Obtain the webhook from the db
"""
def get_webhook(userid: int) -> list[tuple]:
    result = execute_command(GET_WEBHOOK, (userid,), True)
    return result

"""
Obtain URL and groupID from db
"""
def get_urls(group_id: int) -> list[dict]:
    with connect_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(GET_URL_COMMAND, (group_id,))
            results = cursor.fetchall()
    ans = []
    for entry in results:
        ans.append({'id': entry[0], 'url': entry[1]})
    return ans


"""
Obtains the leaderboard for the lowest points
"""
def get_worst_leaderboard() -> list[tuple[Any, ...]]:
    with connect_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(GET_WORST_LEADERBOARD_COMMAND)
            results = cursor.fetchall()
            return results


"""
Initialises the database
"""
def init_database() -> None:
    execute_command(INIT_USER_TABLE, None, False)
    execute_command(INIT_GROUP_TABLE, None, False)
    execute_command(INIT_FILTER_TABLE, None, False)


"""
Clears the database
"""
def drop_database() -> None:
    execute_command(DROP_TABLE, None, False)
