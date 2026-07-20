from flask import Flask

from routes.batch import batch_bp
 
app = Flask(__name__)
 
app.register_blueprint(batch_bp)
 
@app.route("/")

def home():

    return {

        "status": "running",

        "project": "Luas Passenger Analytics",

        "backend": "Flask API"

    }
 
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
 
