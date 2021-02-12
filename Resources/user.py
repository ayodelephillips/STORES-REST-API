import sqlite3
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_refresh_token_required,
    get_jwt_identity, jwt_required,
    get_raw_jwt
)
from models.user import UserModel
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                    type=str,
                    required=True,
                    help="This field cannot be left blank!"
                    )
_user_parser.add_argument('password',
                    type=str,
                    required=True,
                    help="This field cannot be left blank!"
                    )


class UserRegister(Resource):
    TABLE_NAME = 'users'

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User with that username already exists."}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    """ user resource for testing """
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        user.delete_from_db()

        return {"message": "user deleted."}, 200


class UserLogin(Resource):
    
    @classmethod
    def post(cls):
        # get data from parser, 
        data = _user_parser.parse_args()

        # find user in db,
        user = UserModel.find_by_username(data['username'])
        
        # this is what authenticate function did previously in jwt
        if user and safe_str_cmp(user.password, data['password']):
            # identity = is what the identity function used to do
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token':access_token,
                'refresh_token':refresh_token
            }, 200
        return {'message':'Invalid Credentials'},401  # return unauthorized error code


class UserLogout(Resource):
    @jwt_required
    def post(self):
        """we blacklist the jwt aceess token id used, so the user must get another one via login """
        jti = get_raw_jwt()['jti']  # jti is jwt ID, a unique identifier for a JWT
        BLACKLIST.add(jti)      # add the jti to the blacklist set
        return {"message":"successfully logged out."}, 200

class  TokenRefresh(Resource):
    """Get the refresh_token sent from the userLogin and generates a new access token. 
    Refresh token doesn't change """
    @jwt_refresh_token_required
    def post(self):
        # get_jwt_identity works with both refresh and access tokens
        current_user = get_jwt_identity()  # we have a refresh token already before this line is encountered
        new_token = create_access_token(identity=current_user, fresh=False)  # access token we get back won't be fresh. it will be saved, sent back in next request where it'll be checked if token is fresh or not
        return {'access_token':new_token}, 200



