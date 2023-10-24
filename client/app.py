import socketio
import requests

service_address = ('http://0.0.0.0:50135')
server_address = 'http://54.94.45.183:5000'
# server_address = 'http://0.0.0.0:5000'

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('connection established')

@sio.on('disconnect')
def on_disconnect():
    print('disconnected from server')

@sio.on('message')
def on_message(data):
    # redirect message to local service
    print('message received with ', data)
    
    res = requests.request(data['method'], service_address + data['path'], data=data['data'], headers=data['headers'])
    return res.content, res.status_code, dict(res.headers)

if __name__ == '__main__':
    auth = {'username': 'admin', 'password': 'admin'}
    sio.connect(server_address, auth=auth)
    sio.wait()