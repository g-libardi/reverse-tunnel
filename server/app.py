# reverse tunnel server
import socket
from threading import Thread, Event
from threading import current_thread, enumerate as list_threads
import signal
import os
import json

service = None
server = None
exit_flag = False

def main():
    global server

    host = '0.0.0.0'
    port = os.getenv('PORT', default=5000)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server.bind((host, int(port)))
    server.listen(os.getenv('MAX_CONNECTIONS', default=5))

    print(f"Servidor Socket escutando em {host}:{port}")
    print(f"Para encerrar o servidor pressione ctrl+c")

    try:
        while True:
            client, address = server.accept()
            print(f"Conexão recebida de {address[0]}:{address[1]}")

            # Inicia uma nova thread para lidar com a conexão
            th = Thread(target=handle_connection, args=(client, address))
            th.start()
    except KeyboardInterrupt:
        print('\nEncerrando servidor...')
    finally:
        if service:
            service.close()
        
        for th in list_threads():
            if th != current_thread():
                th.join()

        server.close()
        print('Servidor encerrado.')

def handle_connection(client_socket, address):
    # check if the request is http or raw
    data = client_socket.recv(1024).decode('utf-8')
    if data.split(' ')[0] == 'NEW_SERVICE':
        handle_service(data, client_socket)
    else:
        handle_client(data, client_socket)

def handle_client(data, socket):
    # handle the cleint request from browser, foward request and return the response from service to the client, then closes
    try:
        if not service:
            socket.send('HTTP/1.1 OK \n\n Service not connected to server.'.encode('utf-8'))
            socket.close()
            return
        service.send(data.encode('utf-8'))
        print('Request sent to service')
        response = service.recv(1024)
        print('Response received from service')
        socket.send(response)
        print('Response sent to client')
        print(response, '\n\n\n\n')
    finally:
        socket.close()

def handle_service(data, socket):
    global service

    username = data.split('username=')[1].split('&')[0]
    password = data.split('password=')[1].split('&')[0]
    if username == os.getenv('USERNAME', 'admin') and password == os.getenv('PASSWORD', 'admin'):
        if service:
            service.close()
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


if __name__ == '__main__':
    main()