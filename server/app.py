import flask
from flask import request, jsonify
from flask_socketio import SocketIO
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True
sio = SocketIO(app, cors_allowed_origins="*")

service = None

@app.route('/', methods=['GET'])
def home():
    data = request.args
    print(f'GET request received: {request}')
    res = sio.call('message', {'data': data}, to=service)
    print(f'\n\n received: {res} \n\n')
    return res

@sio.on('connect')
def on_connect(auth):
    global service
    if auth['username'] == os.getenv('RT_USERNAME', 'admin') and auth['password'] == os.getenv('RT_PASSWORD', 'admin'):
        if service:
            sio.disconnect(service)
        print(f'Service connected. id: {request.sid}')
        service = request.sid
    else:
        print('Service tried to connect with wrong credentials')
        sio.disconnect()

@sio.on('disconnect')
def on_disconnect():
    print('Service disconnected')


if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=os.getenv('PORT', 5000))