from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def hello_world():
    host_ip = request.host
    return host_ip



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)