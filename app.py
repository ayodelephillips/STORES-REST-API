import os
from flask import Flask, jsonify
from flask_restful import Api 
from flask_jwt_extended import JWTManager  # use jwt extended instead of jwt
from security import authenticate, identity

from Resources.user import (
    UserRegister, User,
    UserLogin, TokenRefresh, UserLogout
)
from Resources.item import  Item, ItemList
from Resources.store import  Store, StoreList

from blacklist import BLACKLIST
#sql alchemy
from db import db

# reqparse ensures only some elements can be passed in through the json payload. 
# it can be used in many other applications
# reqparse is used in the put method to ensure only allowed args are received, removes not needed data from payload
"""
 resource represents anything the api is concerned with. e.g if api is concerned with 'students', 
 then student is a resource. resource mainly refers to things api can create or return etc
 resource are usually mapped to db table
"""
app = Flask(__name__)  # flask app with url routes/endpoints

# either get the postgres fromm heroku or the sqlite db. we read from config vars 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # turn off flask alchemy modification tracker, not sql alchemy modif tracker. we are changing the extensions behaviour
app.config['PROPAGATE_EXCEPTIONS'] = True # flask extensions like jwt can raise their own errors

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access','refresh']  # enable blacklist for both access and refresh tokens

app.secret_key = "phillips"  # we can use app.config['JWT_SECRET_KEY']
api = Api(app)  # allows us add resources, and state whether we can GET or POST on the resource. api works with resource and every resource must be a class

"""
# jwt creates the /auth. when /auth is called, jwt gets username & pwd and sends it to the authenticate function
# the request to the /auth i.e authenticate returns a jtw token which can be used in next request
# when we send the jwt token to next request, it calls identity function, gets user id and correct user with the jw token
"""
        #  change the default '/auth' endpoint to '/login'
    # app.config['JWT_AUTH_URL_RULE'] = '/login' 
        # config JWT to expire within half an hour
    #app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)


# this will be hashed before deployment
@app.before_first_request
def create_tables():
    """create the tables before the first request. it uses the model imports e.g resources.store"""
    db.create_all()


jwt = JWTManager(app)  # doesn't create auth end point automatically

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    """runs each time we run the login endpoint, adds data to th """
    # check if user id is 1. ideally we should read from db or a config file instead of hardcoding the id 1
    print("identity is {}".format(identity))
    if identity == 1:
        return {'is_admin':True}
    return {'is_admin':False}


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    """ Returns true or otherwise if the id of token being sent is in the blacklist.
    decrypted_token contains token data as user id/identity, when token was created etc """
    return decrypted_token['jti'] in BLACKLIST  # return T or F if the id is in the blacklist

# customise some details in the jwt manager instance

@jwt.expired_token_loader
def expired_token_callback():
    """when flask jwt realises token sent across is expired, this function is called """
    return jsonify({
        'description': 'The token has expired',
        'error':'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_error(error):
    """returns message when wrong string is entered in authorization header. invalid jwt token """
    return jsonify({
        'description': 'Signature Verification failed.',
        'error':'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """called when no jwt token is received by the app """
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error':'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    """ called when no-fresh token is sent but we require a fresh token. e.g. /item/post """
    return jsonify({
        'description': 'Token Sent must be a fresh token',
        'error':'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    """can help log out a user that has valid jwt token by adding the token to revoked token list
        jwt goes to check_if_token_in_blacklist, and if the user is blacklisted, revokes the token
    """
    return jsonify({
        'description': 'The token has been revoked',
        'error':'token_revoked'
    }), 401


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')  # we can call the endpoint 'auth' if we want
api.add_resource(UserLogout, '/logout')  
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5400, debug=True)  # state the ports and also enable debugging
