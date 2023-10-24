import flask
from flask import request, Response, jsonify
from flask_socketio import SocketIO
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True
sio = SocketIO(app, cors_allowed_origins="*")

service = None


@app.route('/', methods=['GET','POST','DELETE'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST','DELETE'])
def proxy(path):
    if not service:
        return jsonify({'error': 'Service not connected to proxy'}), 503

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    resp = sio.call('message', {'method': request.method, 'path': path, 'data': request.get_data}, to=service)
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
    sio.run(app, host='0.0.0.0', port=os.getenv('PORT', 5000))