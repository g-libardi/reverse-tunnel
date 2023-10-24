import flask
from flask import request, Response, jsonify
from flask_socketio import SocketIO
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True
sio = SocketIO(app, cors_allowed_origins="*")

service = None

@app.route('/', methods=['GET','POST','DELETE'])
def home(path = '/'):
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response = None

    if request.method=='GET':
        resp = sio.call('message', {'method': 'GET', 'path': path}, to=service)
        headers = [(name, value) for (name, value) in  resp[2].items() if name.lower() not in excluded_headers]
        response = Response(resp[0], resp[1], headers)
        
    elif request.method=='POST':
        resp = sio.call('message', {'method': 'POST', 'path': path, 'json': request.get_json}, to=service)
        headers = [(name, value) for (name, value) in resp[2].items() if name.lower() not in excluded_headers]
        response = Response(resp[0], resp[1], headers)
        
    elif request.method=='DELETE':
        resp = sio.call('message', {'method': 'DELETE', 'path': path}, to=service)
        response = Response(*resp)
    
    return response

@app.route('/<path:path>', methods=['GET','POST','DELETE'])
def proxy(path):
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response = None

    if request.method=='GET':
        resp = sio.call('message', {'method': 'GET', 'path': path}, to=service)
        headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        
    elif request.method=='POST':
        resp = sio.call('message', {'method': 'POST', 'path': path, 'json': request.get_json}, to=service)
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        
    elif request.method=='DELETE':
        resp = sio.call('message', {'method': 'DELETE', 'path': path}, to=service)
        response = Response(resp.content, resp.status_code, headers)
    
    return response

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