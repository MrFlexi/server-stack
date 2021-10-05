import time
import os
import socket
import redis
from flask import Flask, request, jsonify, render_template, send_file, Response
from flask_mongoengine import *
from flask_apscheduler import APScheduler
from flask_cors import CORS
from PIL import Image
import urllib 
import json
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from flask_socketio import SocketIO, emit, disconnect
import requests
#import numpy as np
#import cv2
#from IPython.display import Image


app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

cache = redis.Redis(host='redis', port=6379)

username = 'mrflexi'
password = 'nc:13Arequipa'
database = 'sensors'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

client = InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org="-")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()


#app.config["MONGODB_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']


app.config['MONGODB_SETTINGS'] = {
    'db': 'admin',
    'host': 'mongodb',
    'username':'mrflexi_root',
    'password':'nc:13Arequipa',    
    'port': 27017,   
}


db = MongoEngine(app)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def sendImagetoYolo():
    url = "http://yolo.szaroletta.de/detect"
    data = {'Street':'Im Kieroth', 'test2':2}
    filename = './webcam/lastimage.jpg'


    my_img = {'image': open(filename, 'rb')}
    result = requests.post(url, files=my_img)
    print("HTTP result code from YOLO API call:")
    #print(result.status_code)
    #print(result.json())
    return result.json()
    


def old_send():
    with open(filename, 'w') as f:
        url = "http://yolo.szaroletta.de/detect"
        files = [
                ('document', (filename, open(filename, 'rb'), 'application/octet')),
                ('data', ('data', json.dumps(data), 'application/json'))
                ]

        r = requests.post(url, files=files)
        print(r)


class db_device(db.Document):
    device_id = db.StringField()    
    name = db.StringField()
    sleep_time = db.StringField()
    age = db.StringField()  
    image = db.ImageField(thumbnail_size=(150,150))
    def to_json(self):
        return {"device_id": self.device_id,
                "name": self.name,
                "sleep_time": self.sleep_time}       



@app.route('/')
def hello():
    p = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    #write_api.write(bucket=bucket, record=p)

    count = get_hit_count()
    return 'Hello World Jochen3! I have been seen {} times.\n'.format(count)

@app.route('/l')
def launchpad():
    return render_template("index.html", title = 'Projects' , async_mode=socketio.async_mode)


@app.route('/device', methods=['GET'])
def query_records():
    name = request.args.get('name')
    lo_device = db_device.objects(name=name).first()
    if not lo_device:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(lo_device.to_json())


@app.route('/image', methods=['GET'])
def display_image():
    name = request.args.get('name')
    lo_device = db_device.objects(name=name).first()
    if not lo_device:
        return jsonify({'error': 'data not found' + name})
    else:
        photo = lo_device.image.read()
        content_type = lo_device.image.content_type
        return send_file(photo, as_attachment=True, attachment_filename='myfile.jpg')

@app.route('/get_last_image', methods=['GET'])
def get_last_image():
    #name = request.args.get('name')    
    return send_file('./webcam/lastimage.jpg', as_attachment=True, attachment_filename='lastimage.jpg', mimetype='image/jpg')


@app.route('/get_numer_of_cars')
def get_numer_of_cars():
    d = { "cars": "16", "people": 20 }
    return (jsonify(d), 200)

@app.route('/add2', methods=['POST'])
def add_records(): 
    body = request.get_json()
    print ("add: " + str(body))

    lo_device = db_device(**body).save
    
     # Push data to  client
    out = db_device.objects().to_json()
    socketio.emit('Devices',  {'DeviceList': out }, broadcast=True)
    
    lo_device = db_device.objects()
    return  jsonify(lo_device), 200


@app.route('/update', methods=['PUT'])
def update_records(): 
    body = request.get_json()

    name = 'Flo'    
    lo_device = db_device.objects(name=name).first()
    if lo_device:     
        lo_device.age = lo_device.age + 1
        lo_device.sleep_time = '50'    

        image_bytes = open("Foto.jpg", "rb")
        lo_device.image.replace(image_bytes, content_type='image/jpg', filename='test123.jpg')
        lo_device.save()
        #Image(lo_device.image.thumbnail.read())


     # Push data to  client
    out = db_device.objects().to_json()
    socketio.emit('Devices',  {'DeviceList': out }, broadcast=True)
    
    lo_device = db_device.objects()
    return  jsonify(lo_device), 200   

@app.route('/b', methods=['GET'])
def breadcast_records(): 
    body = request.get_json()

     # Push data to  client
    out = db_device.objects().to_json()
    socketio.emit('Devices',  {'DeviceList': out }, broadcast=True)
    
    lo_device = db_device.objects()
    return  jsonify(lo_device), 200   


@app.route('/device_list')
def  get_movies():
    lo_device = db_device.objects()
    return jsonify(lo_device), 200

@app.route("/add", methods=["POST"])
def process_image():
    file = request.files['image']
    payload = request.form.to_dict(flat=True)
    file.save('./webcam/lastimage.jpg')

    # Read the image via file.stream
    img = Image.open(file.stream)
    return jsonify({'msg': 'success', 
                    'size': [img.width, img.height],
                    'payload' : payload})

@app.route('/upload_and_detect', methods=['POST','GET'])
def upload_and_detect():
    print("Upload Image")
    
    received = request
    
    print(received.files)
    img = None
    if received.files:
        print("Files received")
        print(received.files['image'])
        # convert string of image data to uint8
        file  = received.files['image']
        file.save('./webcam/lastimage.jpg')
        
         # call detection API
        result_json = sendImagetoYolo()
        print('After detection API...')
        print(result_json)

        url=result_json['url']    
        print('URL last image:'+ url)             
                
        return jsonify(result_json)
    else:
        print("No files found")
        return "[FAILED] Image Not Received", 204


@socketio.on('test')
def onTest(message):
    print ("Ping received :Session ID: " + str( request.sid ))

    # Push data to  client
    out = db_device.objects().to_json()
    emit('Devices',  {'DeviceList': out }) 


@socketio.on('connected')
def onConnect(message):
    print ("New Client connected :Session ID: " + str( request.sid ))

    # Push data to  client
    out = db_device.objects().to_json()
    emit('Devices',  {'DeviceList': out })
    emit('message',  'Hallo Welt')


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)

    socketio.run(app, host='0.0.0.0', debug=True)
    #app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
