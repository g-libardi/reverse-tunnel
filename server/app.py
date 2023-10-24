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
    print(f"Para encerrar o servidor pressione ctrl+c")

    while True:
        client, address = server.accept()
        print(f"Conexão recebida de {address[0]}:{address[1]}")

        # Inicia uma nova thread para lidar com a conexão
        th = Thread(target=handle_connection, args=(client,))
        th.start()

def handle_connection(client_socket):
    # check if the request is http or raw
    data = client_socket.recv(1024).decode('utf-8')
    if data.split(' ')[0] == 'NEW_SERVICE':
        handle_service(data, client_socket)
    else:
        handle_client(data, client_socket)

def handle_client(data, socket):
    # handle the cleint request from browser, foward request and return the response from service to the client, then closes
    if not service:
        socket.send('HTTP/1.1 503 Service Unavailable\n\n'.encode('utf-8'))
        socket.close()
        return
    service.send(data.encode('utf-8'))
    response = service.recv(1024)
    socket.send(response)
    socket.close()

def handle_service(data, socket):
    global service

    username = data.split('username=')[1].split('&')[0]
    password = data.split('password=')[1].split('&')[0]
    if username == os.getenv('USERNAME') and password == os.getenv('PASSWORD'):
        service = socket
        response = json.dumps({
            'status': 0,
            'message': 'Service connected to server.'
        })
        socket.send(response.encode('utf-8'))
    else:
        response = json.dumps({
            'status': 1,
            'message': 'Invalid username or password.'
        })
        socket.send(response.encode('utf-8'))
        socket.close()

def handle_close(sig, frame):
    global server
    if server:
        server.shutdown(socket.SHUT_RDWR)
        server.close()
    print("\nServer closed.")
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_close)
    main()