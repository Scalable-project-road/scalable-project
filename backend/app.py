from flask import Flask, render_template
 
from routes.batch import batch_bp

from routes.realtime import realtime_bp

from routes.comparison import comparison_bp
 
app = Flask(__name__)
 
app.register_blueprint(batch_bp)

app.register_blueprint(realtime_bp)

app.register_blueprint(comparison_bp)
 
@app.route("/")

def home():

    return {

        "backend": "Flask API",

        "project": "Luas Passenger Analytics",

        "status": "running"

    }
 
@app.route("/dashboard")

def dashboard():

    return render_template("dashboard.html")
 
if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
 
