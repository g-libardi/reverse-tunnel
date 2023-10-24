import socketio
import requests

service_address = ('http://0.0.0.0:50135')
# server_address = 'http://54.94.45.183:5000'
server_address = 'http://0.0.0.0:5000'

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
    res = None

    if data['method']=='GET':
        res = requests.get(service_address + data['path'])
        
    elif data['method']=='POST':
        res = requests.post(service_address + data['path'], json=data['json'])
        
    elif data['method']=='DELETE':
        res = requests.delete(service_address + data['path'])
    
    return res.content, res.status_code, dict(res.headers)

if __name__ == '__main__':
    auth = {'username': 'admin', 'password': 'admin'}
    sio.connect(server_address, auth=auth)
    sio.wait()