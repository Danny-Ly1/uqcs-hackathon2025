from flask import Flask



app = Flask(__name__)



@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
    # This will run the Flask app on port 5001