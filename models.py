"""
Moduł zawierający modele wpisów do bazy danych oraz metody pomocnicze
"""
from app import db
from passlib.hash import pbkdf2_sha256 as sha256
import datetime as dt


class UserModel(db.Model):
    """
    Model użytkownika w bazie danych
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    isadmin = db.Column(db.Boolean(), default=False, nullable=False)

    def save_to_db(self):
        """
        Dodaje obiekt klasy UserModel do bazy danych
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        """
        Wyszukuje użytkownika w bazie danych

        :param username: Nazwa użytkownika
        :return: Pierwszy znaleziony rekord w bazie danych
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, uid):
        """
        Wyszukuje użytkownika w bazie danych

        :param uid: Identyfikator użytkownika w bazie danych
        :return: Pierwszy znaleziony rekord w bazie danych
        """
        return cls.query.filter_by(id=uid).first()

    @staticmethod
    def generate_hash(password):
        """
        Generuje skrót hasła

        :param password: Hasło
        :return: Skrót hasła w standardzie SHA-256
        """
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, pwdhash):
        """
        Sprawdza poprawność podanego hasła

        :param password: Hasło do sprawdzenia
        :param pwdhash: Skrót hasła wygenerowany podczas rejestracji
        :return: Informacja o zgodności haseł (True/False)
        """
        return sha256.verify(password, pwdhash)


class RevokedTokenModel(db.Model):
    """
    Model przechowujący w bazie danych informację o unieważnionych żetonach JWT (JSON Web Token)
    """

    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        """
        Dodaje obiekt klasy RevokedTokenModel do bazy danych
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        """
        Wysyła zapytanie do bazy danych sprawdzające czy dany żeton JWT nie został unieważniony

        :param jti: Identyfikator żetonu JWT
        :return: Informacja, czy żeton został unieważniony (True/False)
        """
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class GameModel(db.Model):
    """
    Model przechowujący w bazie danych informacje o dostępnych grach
    """
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    riddles = db.Column(db.Integer, nullable=False)

    @classmethod
    def find_by_id(cls, game_id):
        """
        Wyszukuje grę na podstawie jej identyfikatora

        :param game_id: Identyfikator gry
        :return: Pierwszy znaleziony rekord w bazie danych
        """
        return cls.query.filter_by(id=game_id).first()

    @classmethod
    def return_all(cls):
        """
        Pobiera wszystkie gry z bazy danych

        :return: Wszystkie rekordy z tabeli gier, zapisane w postaci JSON
        """
        return cls.serialize(GameModel.query.all())

    @classmethod
    def serialize(cls, objects):
        """
        Serializuje obiekty klasy GameModel do postaci JSON

        :param objects: Lista obiektów klasy GameModel
        :return: Słownik zgodny z notacją JSON zawierający informacje o obiektach klasy GameModel
        """
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'description': x.description,
                'riddles': x.riddles
            }

        return {'games': list(map(lambda x: to_json(x), objects))}

    def save_to_db(self):
        """
        Dodaje obiekt klasy GameModel do bazy danych
        """
        db.session.add(self)
        db.session.commit()


class RiddleModel(db.Model):
    """
    Model przechowujący w bazie danych informacje o zagadkach powiązanych z grami
    """
    __tablename__ = "riddles"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    riddle_no = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Integer, default=100)
    dominant_object = db.Column(db.String(100), nullable=False)

    @classmethod
    def find_riddles_for_game(cls, game_id):
        """
        Wyszukuje wszystkie zagadki powiązane z grą

        :param game_id: Identyfikator gry w bazie danych
        :return: Wszystkie pasujące rekordy z bazy danych, posortowane według numeru zagadki w grze
        """
        return cls.query.filter_by(game_id=game_id).order_by(cls.riddle_no).all()

    @classmethod
    def print_riddles_for_game(cls, game_id):
        """
        Pobiera wszystkie zagadki powiązane z grą

        :param game_id: Identyfikator gry
        :return: Wszystkie pasujące rekordy w tabeli zagadek, zapisane zgodnie z notacją JSON
        """
        return cls.serialize(cls.find_riddles_for_game(game_id))

    @classmethod
    def serialize(cls, objects):
        """
        Serializuje obiekty klasy RiddleModel do postaci JSON

        :param objects: Lista obiektów klasy RiddleModel
        :return: Słownik zgodny z notacją JSON zawierający informacje o obiektach klasy RiddleModel
        """
        def to_json(x):
            return {
                'id': x.id,
                'game_id': x.game_id,
                'description': x.description,
                'riddle_no': x.riddle_no,
                'latitude': x.latitude,
                'longitude': x.longitude,
                'radius': x.radius,
                'dominant_object': x.dominant_object
            }
        return {'riddles': list(map(lambda x: to_json(x), objects))}

    def save_to_db(self):
        """
        Dodaje obiekt klasy RiddleModel do bazy danych
        """
        db.session.add(self)
        db.session.commit()


class ScoreboardEntryModel(db.Model):
    """
    Model przechowujący w bazie danych informacje o rozpoczętych przez użytkowników grach oraz postępie w nich
    """
    __tablename__ = "scoreboard"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    finished = db.Column(db.Boolean, default=False)
    current_riddle = db.Column(db.Integer, nullable=False, default=1)
    time_begin = db.Column(db.DateTime, default=dt.datetime.now())
    time_end = db.Column(db.DateTime)

    @classmethod
    def get_all_entries(cls):
        """
        Pobiera wszystkie rekordy z bazy danych

        :return: Wszystkie rekordy w bazie danych informujące o postępie w grach
        """
        return cls.query.all()

    @classmethod
    def filter_by_user(cls, username):
        """
        Pobiera postęp konkretnego użytkownika we wszystkich grach, do których dołączył

        :param username: Nazwa użytkownika
        :return: Wszystkie pasujące rekordy w bazie danych, posortowane malejąco według daty dołączenia do gry
        """
        user = UserModel.find_by_username(username)
        return cls.query.filter_by(user_id=user.id).order_by(cls.time_begin.desc()).all()

    @classmethod
    def print_by_user(cls, username):
        """
        Wypisuje postęp użytkownika w grach, do których dołączył

        :param username: Nazwa użytkownika
        :return: Postęp użytkownika w grach, do których dołączył, zapisany zgodnie z notacją JSON
        """
        return cls.serialize(cls.filter_by_user(username))

    @classmethod
    def serialize(cls, objects):
        """
        Serializuje obiekty klasy ScoreboardEntryModel do postaci JSON

        :param objects: Lista obiektów klasy ScoreboardEntryModel
        :return: Słownik zgodny z notacją JSON zawierający informacje o obiektach klasy ScoreboardEntryModel
        """
        def to_json(x):
            return {
                'id': x.id,
                'user_id': x.user_id,
                'game_id': x.game_id,
                'finished': x.finished,
                'current_riddle': x.current_riddle,
                'time_begin': str(x.time_begin),
                'time_end': str(x.time_end)
            }
        return {'game_data': list(map(lambda x: to_json(x), objects))}

    @classmethod
    def filter_by_user_and_game(cls, username, game_id):
        """
        Pobiera postęp użytkownika w wybranej grze

        :param username: Nazwa użytkownika
        :param game_id: Identyfikator gry
        :return: Pierwszy pasujący rekord w bazie danych, zawierający informację o postępie w grze
        """
        user = UserModel.find_by_username(username)
        return cls.query.filter_by(user_id=user.id, game_id=game_id).first()

    @classmethod
    def print_by_user_and_game(cls, username, game_id):
        """
        Wypisuje postęp użytkownika w wybranej grze

        :param username: Nazwa użytkownika
        :param game_id: Identyfikator gry
        :return: Pierwszy pasujący rekord w bazie danych, zawierający informację o postępie w grze
        """
        return cls.serialize([cls.filter_by_user_and_game(username, game_id)])

    def save_to_db(self):
        """
        Dodaje obiekt klasy ScoreboardEntryModel do bazy danych
        """
        db.session.add(self)
        db.session.commit()
