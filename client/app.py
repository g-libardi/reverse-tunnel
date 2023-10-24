import socket
import json

host = 'veecks-rt.zeabur.app'
port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

username = input('username: ')
password = input('password: ')

client.send(f'NEW_SERVICE \n\nusername={username}& \n\npassword={password}& \n\n'.encode('utf-8'))
data = client.recv(1024).decode('utf-8')

data = json.loads(data)
if data['status'] == 0:
    print('Service connected to server.')
else:
    print('Error connecting to server.')
    print(data['message'])

print('raw response:')
print(data)

client.close()