"""
Moduł zawierający metody generujące widoki po wejściu pod adres internetowy serwera
"""
from app import app
from flask import render_template


@app.route("/")
def hello():
    """
    Generuje widok wyświetlający stronę głównej aplikacji
    """
    return render_template("index.html")


@app.route("/gamelist")
def gamelist():
    """
    Generuje widok wyświetlający listę wszystkich dostępnych gier z możliwością dołączenia do nich
    """
    return render_template("games.html")


@app.route("/statistics")
def statistics():
    """
    Generuje widok wyświetlający postęp wszystkich użytkowników w każdej grze, do której dołączyli
    """
    return render_template("statistics.html")