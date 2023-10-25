import flask
from flask import request, Response, jsonify
from flask_socketio import SocketIO
import os
import sys

app = flask.Flask(__name__)
app.config["DEBUG"] = True
sio = SocketIO(app, cors_allowed_origins="*")

service = None

@app.route('/', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'], defaults={'path': ''})
def index(path):
    if not service:
        return jsonify({'error': 'Service not connected to proxy'}), 503
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']

    req_headers = {name: value for (name, value) in request.headers if name.lower() not in excluded_headers}
    req_headers['X-Forwarded-For'] = f'''{request.remote_addr},{req_headers.get('X-Forwarded-For', '')}'''
    resp = sio.call('message', {'method': request.method, 'path': path, 'data': request.get_data(), 'headers': req_headers}, to=service)
    headers = [(name, value) for (name, value) in  resp[2].items() if name.lower() not in excluded_headers]
    
    response = Response(resp[0], resp[1], headers)
    
    return response

@app.route('/<path:path>', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def proxy(path):
    if not service:
        return jsonify({'error': 'Service not connected to proxy'}), 503
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']

    req_headers = {name: value for (name, value) in request.headers if name.lower() not in excluded_headers}
    req_headers['X-Forwarded-For'] = f'''{request.remote_addr},{req_headers.get('X-Forwarded-For', '')}'''
    resp = sio.call('message', {'method': request.method, 'path': path, 'data': request.get_data(), 'headers': req_headers}, to=service)
    headers = [(name, value) for (name, value) in  resp[2].items() if name.lower() not in excluded_headers]
    
    response = Response(resp[0], resp[1], headers)
    
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
        print('A service tried to connect with wrong credentials')
        sio.disconnect()

@sio.on('disconnect')
def on_disconnect():
    global service
    print(f'{request.sid} disconnected')
    if service == request.sid:
        service = None
        print('Service disassociated')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        port = int(args[0])
    elif len(args) == 0:
        port = os.getenv('PORT', 5000)

    sio.run(app, host='0.0.0.0', port=port)