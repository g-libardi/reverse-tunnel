# reverse tunnel server
import socket
from threading import Thread, Event
import signal
import os
import json

service = None
server = None

def main():
    global server

    host = '0.0.0.0'
    port = os.getenv('PORT', default=5000)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, int(port)))
    server.listen(os.getenv('MAX_CONNECTIONS', default=5))

    print(f"Servidor Socket escutando em {host}:{port}")
    print(f"Para encerrar o servidor aperte ctrl+c")

    while True:
        cliente, endereco = server.accept()
        print(f"Conexão recebida de {endereco[0]}:{endereco[1]}")

        # Inicia uma nova thread para lidar com a conexão
        th = Thread(target=handle_connection, args=(cliente,))
        th.start()

def handle_close(sig, frame):
    global server
    if server:
        server.close()
    print("\nServer closed.")
    exit(0)

def handle_connection(client_socket):
    # receive the HTTP request from the client
    request = client_socket.recv(1024).decode('utf-8')
    print('HTTP request received from client:', request)

    # parse the HTTP request to get the method and path
    method, path, _ = request.split(' ', 2)

    # check if the request is valid
    if path == '/' and method == 'GET':
        handle_client(client_socket)
    elif path == '/new-service' and method == 'POST':
        handle_service(request, client_socket)
    else:
        response = 'HTTP/1.1 404 Not Found\n\n'

    # send the HTTP response to the client
    
    
    
    

def handle_client(socket):
    # handle the cleint request from browser, foward request and return the response from service to the client, then closes
    response = 'HTTP/1.1 200 OK\n\ncontent-type: text/html\n\n <h1> Hello World! </h1>'
    socket.send(response.encode('utf-8'))
    socket.close()

def handle_service(data, socket):
    global service

    data = data.decode('utf-8')
    # get password from http data
    # packet example: 'POST /new-service HTTP/1.1\r\
    password = data.split('password=')[1].split('&')[0]
    if password == os.getenv('PASSWORD'):
        service = socket
        socket.send('HTTP/1.1 200 OK Service updated.\n\n'.encode('utf-8'))
    else:
        socket.send('HTTP/1.1 401 Unauthorized\n\n'.encode('utf-8'))
        socket.close()

        

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_close)
    main()