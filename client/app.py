import socket
import json

service_ip = '0.0.0.0'
service_port = 50135

host = '0.0.0.0'
port = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

username = input('username: ')
password = input('password: ')

client.send(f'NEW_SERVICE \n\nusername={username}& \n\npassword={password}& \n\n'.encode('utf-8'))
data = client.recv(1024).decode('utf-8')

data = json.loads(data)
if data['status'] == 0:
    print('Service connected to server.')
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as service:
            service.connect((service_ip, service_port))
            data = client.recv(1024).decode('utf-8')
            print('New request from client')
            # make a request to local service
            service.send(data.encode('utf-8'))
            response = service.recv(1024)
            client.send(response)
            print('Response sent to client')
else:
    print('Error connecting to server.')
    print(data['message'])

print('raw response:')
print(data)

client.close()