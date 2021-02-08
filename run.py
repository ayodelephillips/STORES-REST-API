""" 
This file allows for creationof the tables when run by the deployed platform
"""

from app import app
from db import db

db.init_app(app)

@app.before_first_request
def create_tables():
    """create the tables before the first request. it uses the model imports e.g resources.store"""
    db.create_all()
