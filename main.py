from flask import Flask, request, jsonify, make_response
import psycopg2

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
# create a user
@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        # check both of these fields were specified
        assert(username and password)
        # ADD USER TO DATABASE, FIELDS ARE USERNAME AND PASSWORD
        # id = database.insert_user(username, password)
        id = 0
        return make_response(jsonify({'id': id, 'username': username}), 201)
    except:
        return make_response(jsonify({'message': 'error creating user'}), 400)

# get a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        # QUERY DATABASE FOR USER WHOSE ID MATCHES FUNCTION ARGUMENT
        # (username, groupID) = database.query_specific_user(id)
        username = None
        groupID = None
        assert(username)
        return make_response(jsonify({'id': id, 'username': username, 'groupId': groupID}), 200)
    except:
        return make_response(jsonify({'message': 'error getting user'}), 400)

# update a user's group
@app.route('/users/<int:id>/group', methods=['POST'])
def update_usergroup():
    try:
        data = request.get_json()
        groupID = data['groupId']
        # is_success = database.update_usergroup(groupID)
        is_success = True
        assert is_success
        return make_response(jsonify({'groupId': groupID}), 200)
    except:
        return make_response(jsonify({'message': 'error updating user'}), 400)

############################### GROUPS ####################################
# Create a group
@app.route('/group/<int:id>')
def create_group(id):
    try:
        # groupID = database.create_group()
        groupID = None
        assert(groupID)
        # TODO: call update user group with id
        return make_response(jsonify({'groupId': groupID}), 200)
    except:
        return make_response(jsonify({'message': 'error updating user'}), 400)

@app.route('/group/<int:id>/locked_in', methods=['GET'])
def get_group_countdown(id):
    return make_response(jsonify({'message': 'ERROR'}), 400)

# Update group with locked_in count
@app.route('/group/<int:id>/locked_in', methods=['POST'])
def update_group_countdown(id):
    return make_response(jsonify({'message': 'ERROR'}), 400)

# Get rule list
@app.route('/groups/<int:id>/filter_list', methods=['GET'])
def get_group_rulelist(id):
    return make_response(jsonify({'message': 'ERROR'}), 400)

# Add rule
@app.route('/groups/<int:id>/filter_list', methods=['POST'])
def create_group_rule(id):
    return make_response(jsonify({'message': 'ERROR'}), 400)

# Remove rule
@app.route('/groups/<int:id>/filter_list/<int:ruleId>', methods=['DELETE'])
def remove_group_rule(id, ruleId):
    return make_response(jsonify({'message': 'ERROR'}), 400)

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
