import socketio
import requests

service_address = ''
server_address = ''

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
    server_address = input('Server address(https://example.com): ')
    service_address = input('Service address(http://example.com): ')

    auth = {'username': input('username: '),
            'password': input('password: ')}
    sio.connect(server_address, auth=auth)
    sio.wait()