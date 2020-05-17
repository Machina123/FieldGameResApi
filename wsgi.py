"""
Plik konfiguracyjny interfejsu WSGI (Web Server Gateway Interface) służącego do przekazywania zapytań HTTP do aplikacji
napisanej w języku Python.
"""
from app import app

if __name__ == '__main__':
    app.run()