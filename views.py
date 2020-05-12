from app import app
from flask import render_template


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/gamelist")
def gamelist():
    return render_template("games.html")


@app.route("/statistics")
def statistics():
    return render_template("statistics.html")