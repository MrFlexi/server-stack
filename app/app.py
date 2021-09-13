import time
import os
import redis
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
import urllib 
import json
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__)

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


class go_device(db.Document):
    device_id = db.StringField()    
    name = db.StringField()
    sleep_time = db.StringField()
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


@app.route('/device', methods=['GET'])
def query_records():
    name = request.args.get('name')
    lo_device = go_device.objects(name=name).first()
    if not lo_device:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(lo_device.to_json())


@app.route('/add', methods=['POST'])
def add_records(): 
    body = request.get_json()
    lo_device = go_device(**body).save()

    lo_device = go_device.objects()
    return  jsonify(lo_device), 200


@app.route('/device_list')
def  get_movies():
    lo_device = go_device.objects()
    return jsonify(lo_device), 200


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
