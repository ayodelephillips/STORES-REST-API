import os
from flask import Flask
from flask_restful import Api 
from flask_jwt import JWT
from security import authenticate, identity

from Resources.user import UserRegister
from Resources.item import  Item, ItemList
from Resources.store import  Store, StoreList

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
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' # either get the postgres fromm heroku or the sqlite db. we read from config vars 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # turn off flask alchemy modification tracker, not sql alchemy modif tracker. we are changing the extensions behaviour
app.secret_key = "phillips"
api = Api(app)  # allows us add resources, and state whether we can GET or POST on the resource. api works with resource and every resource must be a class

"""
# jwt creates the /auth. when /auth is called, jwt gets username & pwd and sends it to the authenticate function
# the request to the /auth i.e authenticate returns a jtw token which can be used in next request
# when we send the jwt token to next request, it calls identity function, gets user id and correct user with the jw token
"""
        # change the default '/auth' endpoint to '/login'
    # app.config['JWT_AUTH_URL_RULE'] = '/login'   
        # config JWT to expire within half an hour
    #app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)
        # config JWT token to expire within half an hour
    #app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

# @app.before_first_request
# def create_tables():
#     """create the tables before the first request. it uses the model imports e.g resources.store"""
#     db.create_all()

jwt = JWT(app, authenticate, identity) 


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')



if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5400, debug=True)  # state the ports and also enable debugging
