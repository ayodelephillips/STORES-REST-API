"""contains in memory table of registered users """
from werkzeug.security import safe_str_cmp  # safer way to compare strings
from models.user import UserModel


def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        return user


def identity(payload):
    """ this function is unique to flask jwt extension. payload is content of jwt token"""
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)


"""
#users = [
#     User(1, 'bob', 'asdf')
# ]

# # set comprehension, where we assign key value pairs. for instance, the output of below is
# #  'bob':  {
# #         'id':1,
# #         'username':'bob',
# #         'password':'asdf'
# #     }
# username_mapping = { 
#     u.username: u for u in users
# }

# userid_mapping = {
#     u.id: u for u in users
# }
"""
