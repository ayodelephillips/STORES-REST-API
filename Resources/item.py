from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_claims, 
    jwt_optional, 
    get_jwt_identity,
    fresh_jwt_required
)
from models.item import ItemModel

class Item(Resource):

    parser = reqparse.RequestParser()  # initialise reqparse object as an object of the class, and not a specific Item
    # add an argument with datatype of float. the 'required' keyword ensures no
    # request can come in without a price. the parser looks through
    # the json payload and only accepts those which have the argument
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be left blank")

    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="Every item requires a store id.")


    @jwt_required
    def get(self, name):
        """
        get the item using name. where name is unique
        we do not do jsonify(dict) here because flask restful does it automatically for us.
        so we return a dictionary. jwt_required ensures there is a valid access token present
        """

        item = ItemModel.find_by_name(name)
        if item:
            return item.json()  # call the json method inside itemmodel
        return {'message': 'Item not found'}, 404

    @fresh_jwt_required  # needs a fresh access token to post
    def post(self, name):
        """
        we add item to list of items as long as no another item with same name exists
        """
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400
        
        data = Item.parser.parse_args()

        item = ItemModel(name, **data)
        
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred while inserting the item."}, 500 # while 400 means something did go wrong, 500 tells the user that the erroer is not their fault but the server
        
        return item.json(), 201  # item is a piece of json data. 201 means the task was completed and the item was created. 202 code means accepted, and is used when delaying the creation
    
    
    @jwt_required
    def delete(self, name):
        """ DEL  /item/<name> """
        # get data from request, extract jwt coming into the request and ensure only admin user can delete
        claims = get_jwt_claims()
        print("claims is {}".format(claims))
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message':'Item deleted'}

#next(filter(lambda x: x['name'] == name, items), None) # get first output from items dict , where the name is the name, and items is items = {'name': name, "price": data['price']}
# NOTE: filter is defined as filter(f,l), where f is the function(which returns a boolean), and l the list iterated on

    def put(self, name):
        """create or update an item """
        data = Item.parser.parse_args()

        # check if item with that name exists in the db
        item = ItemModel.find_by_name(name)
        
        
        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, **data)
        
        item.save_to_db()

        return item.json()

class ItemList(Resource):
    @jwt_optional   # allows endpoint return all data if user's logged in and return some data if the user isn't logged in
    def get(self):
        """get  a list of all the items. if user is logged in, returns all the items, if not it returns only item names"""
        user_id = get_jwt_identity()  # the jwt_optional allows us get the jwt identity of user id. It returns None if there's no id 
        items =  [item.json() for item in ItemModel.find_all()]
        print("user id is {}".format(user_id))
        if user_id:
            return{'items':items},200
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if you log in'
        },200
