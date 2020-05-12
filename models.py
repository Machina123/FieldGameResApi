from app import db
from passlib.hash import pbkdf2_sha256 as sha256
import datetime as dt


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': f"{num_rows_deleted} row(s) deleted"}
        except:
            return {'message': "Something went wrong"}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, pwdhash):
        return sha256.verify(password, pwdhash)


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class GameModel(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    riddles = db.Column(db.Integer, nullable=False)

    @classmethod
    def find_by_id(cls, game_id):
        return cls.query.filter_by(id=game_id).first()

    @classmethod
    def return_all(cls):
        return cls.serialize(GameModel.query.all())

    @classmethod
    def serialize(cls, objects):
        def to_json(x):
            return {
                'id': x.id,
                'title': x.title,
                'description': x.description,
                'riddles': x.riddles
            }

        return {'games': list(map(lambda x: to_json(x), objects))}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class RiddleModel(db.Model):
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
        return cls.query.filter_by(game_id=game_id).order_by(cls.riddle_no).all()

    @classmethod
    def print_riddles_for_game(cls, game_id):
        return cls.serialize(cls.find_riddles_for_game(game_id))

    @classmethod
    def serialize(cls, objects):
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
        db.session.add(self)
        db.session.commit()


class ScoreboardEntryModel(db.Model):
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
        return cls.query.all()

    @classmethod
    def filter_by_user(cls, username):
        user = UserModel.find_by_username(username)
        return cls.query.filter_by(user_id=user.id).order_by(cls.time_begin.desc()).all()

    @classmethod
    def print_by_user(cls, username):
        return cls.serialize(cls.filter_by_user(username))

    @classmethod
    def serialize(cls, objects):
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
        user = UserModel.find_by_username(username)
        return cls.query.filter_by(user_id=user.id, game_id=game_id).first()

    @classmethod
    def print_by_user_and_game(cls, username, game_id):
        return cls.serialize([cls.filter_by_user_and_game(username, game_id)])

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
