from flask import request, Blueprint
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_3 import Api, swagger, Resource
#from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask import Flask, current_app
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

from models import UserModel, ErrorModel
import json

app = Flask(__name__)

#-------------------------------------------------------------------------------------
#   Mongo DB zeug
#
#-------------------------------------------------------------------------------------
app.config['MONGO_URI'] = 'mongodb://admin:admin@mongodb:27017/admin'
#app.config['MONGO_USERNAME'] = 'admin'
#app.config['MONGO_PASSWORD'] = 'admin'

#mongo = PyMongo(app)
#db = mongo.db

client = MongoClient("mongodb://admin:admin@mongodb:27017/admin")
db = client.admin

class UserResource(Resource):
    @swagger.tags('User')
    @swagger.reorder_with(UserModel, response_code=200, summary="Add User")
    @swagger.parameter(_in='query', name='query', schema=UserModel, required=True, description='query')
    def post(self, _parser):
        """
        Adds a user
        """
        # Validate request body with schema model
        try:
            known_users = []
            print("Post new user in")
            data = UserModel(**_parser.parse_args())
            print("Data",data)
            # convert into json
            data_json = jsonable_encoder(data)
            print("DataJsonable",data_json)
            x = db.users.insert_one(data_json)
            print(x.inserted_id)

        except ValueError as e:
            return ErrorModel(**{'message': e.args[0]}), 400

        return data, 201, {'Location': request.path + '/' + str(data['id'])}

    @swagger.tags('User')
    @swagger.response(response_code=200)
    def get(self):
        """
        print("Get all users")
        """
        # Finde alle Benutzer, ohne das _id-Feld zurückzugeben
        users_cursor = db.users.find({}, {'_id': 0})
        user_list = [UserModel(**user) for user in users_cursor]
        print(user_list)

        return user_list, 200


class UserItemResource(Resource):
    @swagger.tags('User')
    @swagger.response(response_code=200)
    def get(self, user_id):
        """
        Returns a specific user.
        :param user_id: The user identifier
        """
        user = next((u for u in known_users if u['id'] == user_id), None)

        if user is None:
            return ErrorModel(**{'message': "User id {} not found".format(user_id)}), 404

        # Return data through schema model
        return UserModel(**user), 200


def get_user_resources():
    """
    Returns user resources.
    :param app: The Flask instance
    :return: User resources
    """
    blueprint = Blueprint('user', __name__)

    api = Api(blueprint)

    api.add_resource(UserResource, '/api/users')
    api.add_resource(UserItemResource, '/api/users/<int:user_id>')

    return api
