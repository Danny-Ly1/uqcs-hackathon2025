from flask import Flask, request, jsonify, make_response
from discord_webhook import DiscordEmbed, DiscordWebhook
import psycopg2
import time
import database

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

app = Flask(__name__)

@app.route('/')
def hello_world():
    host_ip = request.host
    return host_ip

#create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

################################## USERS #####################################

@app.route('/user', methods=['POST'])
def create_user():
    """
    Create a user (requires username and password)
    """
    try:
        data = request.get_json()
        username: str = data['username']
        password: str = data['password']
        # check both of these fields were specified
        assert(username and password)
        result = database.add_user(username, password)
        print(result)
        return make_response(jsonify({'id': result[0], 'username': result[1]}), 201)
    except:
        return make_response(jsonify({'message': 'Error creating user'}), 400)

@app.route('/user/login', methods=['POST'])
def check_for_user():
    """
    GET a user id (requires username and password)
    """
    try:
        data = request.get_json()
        username: str = data['username']
        password: str = data['password']
        # check both of these fields were specified
        result = database.check_login(username, password)
        return make_response(jsonify({'id': result[0], 'username': result[1]}), 200)
    except:
        return make_response(jsonify({'message': 'Error logging into user'}), 400)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    GET a specific user, via their id
    """
    try:
        # should already know user id
        (dummyid, username, groupID) = database.get_user(id)
        payload = None
        if not groupID:
            payload = jsonify({'id': id, 'username': username, 'groupId': None})
        else:
            payload = jsonify({'id': id, 'username': username, 'groupId': groupID})
        return make_response(payload, 200)
    except:
        return make_response(jsonify({'message': 'Error getting user'}), 400)

@app.route('/users/<int:id>/group', methods=['POST'])
def update_usergroup(id):
    """
    Update a user's groupId
    """
    try:
        data = request.get_json()
        groupID = int(data['groupId'])  # TODO: check if this should be int or str
        # should already know groupid
        (dummyGroupID) = database.updateGroupID(id, groupID)
        return make_response(jsonify({'groupId': groupID}), 200)
    except:
        return make_response(jsonify({'message': 'Error updating user'}), 400)

############################### GROUPS ####################################
@app.route('/group', methods=['POST'])
def create_group():
    """
    Create a group
    """
    try:
        data = request.get_json()
        userID = data['initialUserId']
        groupID = database.add_group()
        # Add initial user as first member of group
        # TODO: force users to only join 1 group
        database.updateGroupID(userID, groupID[0])
        return make_response(jsonify({'groupId': groupID[0]}), 200)
    except:
        return make_response(jsonify({'message': 'Error creating group'}), 400)

# BIGGER TODO: FIX THIS TAKING USER ID AND NOT GROUPID
# Get the group countdown from a user's id
@app.route('/group/<int:id>/locked_in', methods=['GET'])
def get_group_countdown(id):
    try:
        result = database.check_lock(id)
        return make_response(jsonify({'unlock_time_epoch': result[0]}), 200)
    except:
        return make_response(jsonify({'message': 'Error getting group locked in state'}), 400)
    return make_response(jsonify({'message': 'Unfinished'}), 501)

# Update group with locked_in count
@app.route('/group/<int:id>/locked_in', methods=['POST'])
def update_group_countdown(id):
    try: 
        data = request.get_json()
        update_time = int(data['timer_duration']) + (time.time_ns() / (10 ** 9))
        new_time = database.set_lock_in(id, update_time)
        return make_response(jsonify({'unlock_time_epoch': new_time[0]}), 200)
    except:
        return make_response(jsonify({'message': 'Error updating unlock time'}), 400)
    if False:
        # TODO: logic for calculating future epoch
        return make_response(jsonify({'message': 'Error updating group locked in state'}), 400)
    return make_response(jsonify({'message': 'Unfinished'}), 501)

# Get rule list
@app.route('/groups/<int:id>/filter_list', methods=['GET'])
def get_group_rulelist(id):
    try:
        (groupID, urls) = database.get_urls(id)
        # print(f"groupID: {groupID}")
        # print(f"urls: {urls}")
        return make_response(jsonify({urls}, 200))
    except:
        return make_response(jsonify({'message': 'Error getting group filter list'}), 400)

# Add rule
@app.route('/groups/<int:id>/filter_list', methods=['POST'])
def create_group_rule(id):
    try:
        data = request.get_json()
        url = data['url']
        results = database.add_blocked_url(url, id)
        url, linkid = results
        print(url, linkid[0])
        return make_response(jsonify({'id': linkid[0], 'url': url}), 200)
    except:
        return make_response(jsonify({'message': 'Error adding a rule to filter list'}), 400)

# Remove rule
@app.route('/groups/<int:id>/filter_list/<int:ruleId>', methods=['DELETE'])
def remove_group_rule(id, ruleId):
    try:
        database.clear_one_url(ruleId)
        return make_response(jsonify(), 204)
    except:
        return make_response(jsonify({'message': 'Error removing a rule from filter list'}), 400)


#Sends JSON to discord
def send_webhook(user: str, hook: str):
    print("reached")
    webhook = DiscordWebhook(url=hook)      
    embed = DiscordEmbed(title="Blocked Site Access Attempt",
    description= f"{user} went on a blocked website and lost 10 points. Lock innnnnnn",
    color="00FF00") 

    webhook.add_embed(embed)
    webhook.execute()

# User snitching
@app.route('/groups/<int:id>/infraction', methods=['POST'])
def alert_discord(id):
    try:
        data = database.get_webhook(id)
        send_webhook(data[0], data[1])

        data = request.get_json()
        user_id = data['userId']

        database.reduce_points(user_id)

        return make_response(jsonify(), 204)
    except:
        return make_response(jsonify({'message': 'Bad '}), 400)
    

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
    # print("hello world")
    cur.execute("""
    SELECT * FROM USERS
    """)
    results = cur.fetchall() # Fetches all output from above query
    # print(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    access_database()
