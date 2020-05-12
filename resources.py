import json

from flask import jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask_restful import Resource, reqparse

from app import db
from models import UserModel, RevokedTokenModel, GameModel, RiddleModel, ScoreboardEntryModel

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': f"User {data['username']} already exists"}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            return {
                'message': f"User {data['username']} was created"
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': f'User {data["username"]} doesn\'t exist'}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            resp = jsonify({
                'message': f'Logged in as {current_user.username}',
                'access_token': access_token,
                'refresh_token': refresh_token
            })
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp
        else:
            return {'message': 'Wrong credentials'}


class UserLogout(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            resp = jsonify({'message': 'Refresh token has been revoked'})
            unset_jwt_cookies(resp)
            return resp
        except Exception as e:
            print(e)
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        resp = jsonify({'access_token': access_token})
        set_access_cookies(resp, access_token)
        return resp


class GameDetailsResource(Resource):
    @jwt_required
    def get(self, game_id):
        return GameModel.serialize([GameModel.find_by_id(game_id)])


class RiddleListResource(Resource):
    @jwt_required
    def get(self, game_id):
        return RiddleModel.print_riddles_for_game(game_id)


class UserGamesStatusResource(Resource):
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        return ScoreboardEntryModel.print_by_user(current_user)


class GameProgressResource(Resource):
    @jwt_required
    def get(self, game_id):
        current_user = get_jwt_identity()
        return ScoreboardEntryModel.print_by_user_and_game(current_user, game_id)


class GameAdvancementResource(Resource):
    @jwt_required
    def post(self, game_id):
        import datetime as dt
        current_user = get_jwt_identity()
        current_progress = ScoreboardEntryModel.filter_by_user_and_game(current_user, game_id)
        current_game = GameModel.find_by_id(game_id)
        if current_progress.current_riddle + 1 > current_game.riddles:
            current_progress.finished = True
            current_progress.time_end = dt.datetime.now()
        else:
            current_progress.current_riddle = ScoreboardEntryModel.current_riddle + 1
        db.session.commit()
        return ScoreboardEntryModel.serialize([current_progress])


class GameStartResource(Resource):
    @jwt_required
    def post(self, game_id):
        username = get_jwt_identity()
        user = UserModel.find_by_username(username)
        is_game_started = ScoreboardEntryModel.filter_by_user_and_game(username, game_id)
        print(is_game_started)
        if is_game_started is None:
            game = ScoreboardEntryModel(
                user_id=user.id,
                game_id=game_id
            )
            game.save_to_db()
        return ScoreboardEntryModel.serialize(ScoreboardEntryModel.filter_by_user(username))


class StatisticsResource(Resource):
    def get(self):
        import datetime as dt
        out_entries = []
        scoreboard = ScoreboardEntryModel.get_all_entries()
        for sbentry in scoreboard:
            user = UserModel.find_by_id(sbentry.user_id)
            game = GameModel.find_by_id(sbentry.game_id)
            elapsed_seconds = (sbentry.time_end - sbentry.time_begin).total_seconds() \
                if sbentry.time_end else (dt.datetime.now() - sbentry.time_begin).total_seconds()
            entry = {
                "username": user.username,
                "game": game.title,
                "current_riddle": sbentry.current_riddle,
                "finished": sbentry.finished,
                "time_begin": int(sbentry.time_begin.timestamp() * 1000),
                "elapsed_seconds": elapsed_seconds
            }
            out_entries.append(entry)
        return {"entries": out_entries}


class AllGamesResource(Resource):
    def get(self):
        return GameModel.return_all()