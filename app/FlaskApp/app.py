#!/usr/bin/env python

# Create a virtual environment 
# python -m venv venv

# Activate the virtual environment

# Windows
# venv\Scripts\activate
# Linux
# source venv/bin/activate
# pip freeze > requirements.txt

from flask import Flask, render_template, request, session
from flask_cors import CORS
from flask_restful_swagger_3 import swagger, get_swagger_blueprint
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from blueprints import get_user_resources
from ultralytics import YOLO


async_mode = None
app = Flask(__name__)
CORS(app, resources={"/api/*": {"origins": "*"}})
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")

def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True

swagger.auth = auth

# Get user resources
user_resources = get_user_resources()

# Register the blueprint for user resources
app.register_blueprint(user_resources.blueprint)

# Prepare a blueprint to server the combined list of swagger document objects and register it
servers = [{"url": "http://szaroletta.de:41851"}, {"url": "http://localhost:41851"}]

SWAGGER_URL = '/api/doc'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'swagger.json'  # Our API url (can of course be a local resource)

# app.config.setdefault('SWAGGER_BLUEPRINT_URL_PREFIX', '/swagger')

swagger_blueprint = get_swagger_blueprint(
    user_resources.open_api_object,
    swagger_prefix_url=SWAGGER_URL,
    swagger_url=API_URL,
    title='Example', version='1', servers=servers)


app.register_blueprint(swagger_blueprint)


@app.route('/ui5')
def UI5():
    return render_template('index.html')


#-----------------------------------------------------------------------------------------------
#   Socket IO
#-----------------------------------------------------------------------------------------------
@socketio.on('connect', namespace='')
def onConnect():
    print()
    print("------------------------------------------------------------------")
    print ("Socket IO Client connected :Session ID: " + str( request.sid ))
    print("------------------------------------------------------------------")
    
@socketio.on('disconnect', namespace='')
def onDiscconnect():
    print ("Client disconnected: " + str( request.sid ))
   

if __name__ == '__main__':
    debug = True
    socketio.run(app, host='0.0.0.0', debug=debug)
    #app.run(debug=True, host='0.0.0.0')
