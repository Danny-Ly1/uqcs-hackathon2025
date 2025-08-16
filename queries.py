DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

GROUP_ID_INDEX = 3

ADD_USER_COMMAND = """INSERT INTO users (username, password) VALUES (%s, %s) RETURNING userid, username"""
GET_USER_COMMAND = """SELECT userid, username, groupid, points FROM users WHERE userid = %s"""

GET_GROUP_ID = """SELECT groupid FROM users WHERE userid = %s"""
UPDATE_GROUPID_COMMAND = """UPDATE Users SET groupID = %s WHERE userID = %s RETURNING groupID"""
ADD_GROUP_COMMAND = """INSERT INTO groups (links) VALUES (%s) RETURNING groupID"""

ADD_URL_COMMAND = """INSERT INTO filters (url, groupid) VALUES (%s, %s) RETURNING linkid"""
DELETE_URL_COMMAND = """DELETE FROM filters WHERE linkid = %s"""
CHECK_VALID_URL = """SELECT COUNT(*) FROM groups, unnest(links) AS element WHERE element = %s AND groupid = %s """
GET_URL_COMMAND = """SELECT linkid, url FROM filters WHERE groupid = %s"""

REDUCE_POINTS = """UPDATE users SET points = points - %s WHERE userid = %s"""
SET_POINTS = """UPDATE users SET points = %s WHERE userid = %s"""

SET_WEBHOOK = """UPDATE users SET webhookurl = %s WHERE userid = %s"""
GET_WEBHOOK = """SELECT username, webhookurl FROM users WHERE userid = %s"""

GET_LOCK_STATUS = """SELECT elapsedtime FROM groups WHERE groupid = %s"""
REMOVE_LOCK_COMMAND = """UPDATE Groups SET elapsedtime = 0 WHERE groupID = %s"""

SET_EPOCH_TIME_COMMAND = """UPDATE Groups SET elapsedtime = %s WHERE groupID = %s"""
GET_UPDATE_TIME = """SELECT elapsedtime FROM groups WHERE groupid = %s"""

CHECK_LOGIN_COMMAND = """SELECT userid, username FROM users WHERE username = %s AND password = %s"""

GET_WORST_LEADERBOARD_COMMAND = """SELECT username, MIN(points) as MIN_POINTS FROM users GROUP BY username ORDER BY MIN_POINTS ASC"""

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
                    url TEXT UNIQUE,
                    groupid INT
                    """

DROP_TABLE = """
            DROP TABLE users;
            DROP TABLE groups;
            DROP TABLE filters;
            """
