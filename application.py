import os

from flask import Flask, render_template, request, url_for
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

socketio = SocketIO(app)
database_url = 'postgres://vysrlwhpdhuyxq:e306c8e308dc7790339d6037ef179cab11098d423dfc7dc059afbfee050aa3f0@ec2-75-101-153-56.compute-1.amazonaws.com:5432/d49d9cte5vk135'
# Set up databases
engine = create_engine(database_url)
db = scoped_session(sessionmaker(bind=engine))

# Homepage
@app.route('/')
def index():
    return render_template("index.html")

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    # Gets top scores from database
    topscores = db.execute("SELECT * FROM scores ORDER BY score DESC, name ASC").fetchall()
    #topscores = []
    # Displays leaderboard with received scores
    return render_template("leaderboard.html", topscores = topscores)

@socketio.on("check score")
def scorecheck(data):
    """Checks if the score is a high score."""
    if db.execute("SELECT * FROM scores").rowcount < 10:
        emit("get name")
    else:
        breakpoint = db.execute("SELECT score FROM scores ORDER BY score ASC LIMIT 1").fetchone()[0]
        if data["score"] > breakpoint:
            emit("get name")

@socketio.on("add score")
def addscore(data):
    """Adds the score to the database."""

    if db.execute("SELECT * FROM scores").rowcount == 10:
        db.execute("DELETE FROM scores ORDER BY score ASC, name DESC LIMIT 1")
    db.execute("INSERT INTO scores (name, score) VALUES (:name, :score)", {"name": data["name"], "score": data["score"]})
    db.commit()


port = int(os.environ.get("PORT", 5000))
socketio.run(app,host='0.0.0.0', port=port)







