import socket

host = 'veecks-rt.zeabur.app'
port = 443

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

client.send(f'GET / HTTP/1.1\r\nHost: {host}\r\n\r\n'.encode('utf-8'))
data = client.recv(1024)
print(data.decode('utf-8'))

client.close()