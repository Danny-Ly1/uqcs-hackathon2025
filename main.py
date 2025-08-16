from flask import Flask, request, jsonify, make_response
import psycopg2
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
        id = database.add_user(username, password)
        return make_response(jsonify({'id': id, 'username': username}), 201)
    except:
        return make_response(jsonify({'message': 'Error creating user'}), 400)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    GET a specific user, via their id
    """
    try:
        # QUERY DATABASE FOR USER WHOSE ID MATCHES FUNCTION ARGUMENT
        # (username, groupID) = database.query_specific_user(id)
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
        groupID = int(data['groupId'])
        # is_success = database.update_usergroup(groupID)
        (groupID) = database.updateGroupID(id, groupID)
        return make_response(jsonify({'groupId': groupID}), 200)
    except:
        return make_response(jsonify({'message': 'Error updating user'}), 400)

############################### GROUPS ####################################
@app.route('/group')
def create_group():
    """
    Create a group
    """
    try:
        data = request.get_json()
        userID = data['initialUserId']
        groupID = database.add_group()
        # TODO: call update user group with id
        return make_response(jsonify({'groupId': groupID}), 200)
    except:
        return make_response(jsonify({'message': 'Error creating group'}), 400)

# Get the group countdown from a user's id
@app.route('/group/<int:id>/locked_in', methods=['GET'])
def get_group_countdown(id):
    try:
        # TODO: something funky is going on
        (locked_in, unlock_time_epoch) = database.check_lock(id)
        return make_response(jsonify({'locked_in': locked_in,
        'unlock_time_epoch': unlock_time_epoch}), 200)
    except:
        return make_response(jsonify({'message': 'Error getting group locked in state'}), 400)

# Update group with locked_in count
@app.route('/group/<int:id>/locked_in', methods=['POST'])
def update_group_countdown(id):
    # TODO: logic for calculating future epoch
    return make_response(jsonify({'message': 'Error updating group locked in state'}), 400)

# Get rule list
@app.route('/groups/<int:id>/filter_list', methods=['GET'])
def get_group_rulelist(id):
    return make_response(jsonify({'message': 'Error getting group filter list'}), 400)

# Add rule
@app.route('/groups/<int:id>/filter_list', methods=['POST'])
def create_group_rule(id):
    return make_response(jsonify({'message': 'Error adding a rule to filter list'}), 400)

# Remove rule
@app.route('/groups/<int:id>/filter_list/<int:ruleId>', methods=['DELETE'])
def remove_group_rule(id, ruleId):
    return make_response(jsonify({'message': 'Error removing a rule from filter list'}), 400)

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
    print("hello world")
    cur.execute("""
    SELECT * FROM groups
    """)
    results = cur.fetchall() # Fetches all output from above query
    print(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    access_database()
