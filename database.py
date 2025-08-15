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


def update_score():
    pass

def updateGroupID(user_id: int, group_id: int):
    with connect_to_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""UPDATE Users SET groupID = %s WHERE userID = %s""", (group_id, user_id))
            conn.commit()
