from db import db


class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    # ensure we don't yet create the many items object in the db when we create the store model. 
    # not adding the 'lazy' attribute makes db operations expensive if there are many items
    items = db.relationship('ItemModel', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def json(self):
        """ return a json rep(dictionary) of the model. because lazy is dynamic, we go to the table anytime we call json """
        return {
            'id': self.id,
            'name': self.name, 
            'items': [item.json() for item in self.items.all()]
        }  # because lazy is dynamic, we use .all() to retrieve from querybuilder

    @classmethod
    def find_by_name(cls, name):
        """ return StoreModel object containing the name and price """
        return cls.query.filter_by(name=name).first()  # select* from items where name=name LIMIT 1

    @classmethod
    def find_all(cls):
        """ Get all the stores """
        return cls.query.all()

    def save_to_db(self):
        """insert an object into the db or update preexisting object """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
