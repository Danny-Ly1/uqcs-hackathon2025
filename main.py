from flask import Flask, request, jsonify, make_response
from discord_webhook import DiscordEmbed, DiscordWebhook
import time
import database
from flask_sock import Sock
from queries import *

app = Flask(__name__)
sock = Sock(app)

"""
Root test
"""
@app.route('/')
def hello_world():
    host_ip = request.host
    return host_ip

"""
Test path
"""
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

        assert(username and password) # check both of these fields were specified
        result = database.add_user(username, password)
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
        (dummyid, username, groupID, points) = database.get_user(id) # should already know user id
        payload = None
        if not groupID:
            payload = jsonify({'id': id, 'username': username, 'groupId': None, 'points': points})
        else:
            payload = jsonify({'id': id, 'username': username, 'groupId': groupID, 'points': points})
        return make_response(payload, 200)
    except:
        return make_response(jsonify({'message': 'Error getting user'}), 400)

@app.route('/users/<int:id>/group', methods=['POST'])
def update_usergroup(id):
    """
    Update a user's groupId aka joining a group
    """
    try:
        data = request.get_json()
        groupID = int(data['groupId'])
        exist = database.group_exists(groupID)
        if (exist == 0):
            return make_response(jsonify({'message': 'Group id does not exist'}), 400)
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
        database.updateGroupID(userID, groupID[0])
        return make_response(jsonify({'groupId': groupID[0]}), 200)
    except:
        return make_response(jsonify({'message': 'Error creating group'}), 400)

# Get the group countdown from a user's id
@app.route('/group/<int:id>/locked_in', methods=['GET'])
def get_group_countdown(id):
    try:
        result = database.check_lock(id)
        return make_response(jsonify({'unlock_time_epoch': result[0]}), 200)
    except:
        return make_response(jsonify({'message': 'Error getting group locked in state'}), 400)

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

# Get rule list
@app.route('/groups/<int:id>/filter_list', methods=['GET'])
def get_group_rulelist(id):
    try:
        result = database.get_urls(id)
        return make_response(jsonify(result), 200)
    except:
        return make_response(jsonify({'message': 'Error getting group filter list'}), 400)

# Add rule
@app.route('/groups/<int:id>/filter_list', methods=['POST'])
def create_group_rule(id):
    try:
        data = request.get_json()
        url = data['url']
        duplicate = database.url_duplicate_yes(id, url)
        
        if (duplicate > 1):
            return make_response(jsonify({'message': 'Duplicate found'}), 400)
        
        results = database.add_blocked_url(url, id)
        url, linkid = results
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
def send_webhook(user: str, hook: str, infraction: int):
    webhook = DiscordWebhook(url=hook)      
    if infraction == 1:
        embed = DiscordEmbed(title="Blocked Site Access Attempt",
        description= f"{user} went on a blocked website and lost 10 points. LOCK IN!",
        color="FF0000") 
        embed.set_image("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.tenor.com%2FDa_Q9QXAUzUAAAAi%2F" \
                "angry-fist-emoticon-emoticon.gif&f=1&nofb=1&ipt=a71db1e90a5d" \
                "e3001eea382f517141c1ec8b1e629de42ec7673aea5d76d41549")
    if infraction == 2:
        embed = DiscordEmbed(title="Blocked Site Access Attempt",
        description= f"{user} quit early and lost 50 points. Next time, LOCK IN!",
        color="FFFFFF") 
        embed.set_image("https://external-content.duckduckgo.com/iu/?u=" \
        "https%3A%2F%2Fi.imgflip.com%2F740194.png&f=1&nofb=1&ipt=6" \
        "270529088328ceb3d3f9d2fd94a97ceb4ada92d2e86e584241c0d8352c6e9fe")
    webhook.add_embed(embed)
    webhook.execute()

# User snitching
@app.route('/groups/<int:id>/infraction', methods=['POST'])
def alert_discord(id):
    try:
        data = request.get_json()
        user_id = data['userId']
        database.reduce_points(user_id, 10)
        # hook = database.get_webhook(id)

        # if (hook is not None):
        #     send_webhook(hook[0], hook[1], infraction)

        # if infraction == 1:
        #     database.reduce_points(user_id, 10)
        # else:
        #     database.reduce_points(user_id, 50)

        return make_response(jsonify(), 204)
    except:
        return make_response(jsonify({'message': 'Bad '}), 400)

# Giving users points
@app.route('/users/<int:id>/addpoints', methods=['POST'])
def gain_points(id):
    try:
        data = request.get_json()
        user_id = data['userID']
        database.reduce_points(user_id, -50)
        return make_response(jsonify(), 204)
    except:
        return make_response(jsonify({'message': 'Bad '}), 400)

# Showing leaderboard for lowest number of points
# Haven't tested and isn't required to be implemented
@app.route('/users/<int:id>/leaderboard', methods=['POST'])
def show_leaderboard():
    try:
        results = database.get_worst_leaderboard()
        return make_response(jsonify({'leaderboard': results}), 200)
    except:
        return make_response(jsonify({'message': 'Bad '}), 400)

"""
Allow ping
"""
@sock.route("/ws")
def ws(ws):
    while True:
        data = ws.receive() 
        ws.send(f"Echo from server: {data}")

if __name__ == '__main__':
    database.init_database()
    app.run(host=DATA_HOST, port=5001, debug=True)
