import socketio
import requests

service_address = ('0.0.0.0', 50135)

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
    res = requests.get(f'http://{service_address[0]}:{service_address[1]}', params=data).content
    return res

if __name__ == '__main__':
    auth = {'username': 'admin', 'password': 'admin'}
    sio.connect('http://localhost:5000', auth=auth)
    sio.wait()