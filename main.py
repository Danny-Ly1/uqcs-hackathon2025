from flask import Flask, request, jsonify, make_response
import psycopg2

DATA_HOST = '10.89.76.206'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '1234'
PORT = '5432'

app = Flask(__name__)

class User():
    id = None
    username = None
    email = None
    # add init method that takes email and name

    def json(self):
        return {'id': self.id,'username': self.username, 'email': self.email}

@app.route('/')
def hello_world():
    host_ip = request.host
    return host_ip

#create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)


# create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        # ADD USER TO DATABASE, FIELDS ARE EMAIL AND NAME
        return make_response(jsonify({'message': 'user created'}), 201)
    except:
        return make_response(jsonify({'message': 'error creating user'}), 500)

# get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        # QUERY DATABASE FOR LIST OF ALL USERS, WHICH IS A COLLECTION OF USER
        users = []
        return make_response(jsonify([user.json() for user in users]), 200)
    except:
        return make_response(jsonify({'message': 'error getting users'}), 500)

# get a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        # QUERY DATABASE FOR USER WHOSE ID MATCHES FUNCTION ARGUMENT
        user = None
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error getting user'}), 500)

# update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        # QUERY DATABASE FOR USER WHOSE ID MATCHES FUNCTION ARGUMENT
        user = None
        if user:
            # UPDATE THE USER FIELDS IN THE DATABASE
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error updating user'}), 500)

# delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        # QUERY DATABASE FOR USER WHOSE ID MATCHES FUNCTION ARGUMENT
        user = None
        if user:
            # DELETE THE USER IN THE DATABASE
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error deleting user'}), 500)


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
    cur.execute("""
    
    """)
    results = cur.fetchall() # Fetches all output from above query

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
