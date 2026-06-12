import socket
import threading

HOST = "172.24.174.181"
PORT = 8000

def handle_client(client_socket):

    # menerima request dari client
    request = client_socket.recv(1024).decode()

    print("Request diterima:")
    print(request)

    # buka file html
    file = open("index.html", "r")
    html = file.read()
    file.close()

    # membuat response HTTP
    response = "HTTP/1.1 200 OK\r\n\r\n" + html

    # kirim ke client
    client_socket.send(response.encode())

    # tutup koneksi
    client_socket.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print("Web Server berjalan di {}:{}".format(HOST, PORT))

while True:

    client_socket, address = server.accept()

    print("Client terhubung:", address)

    # membuat thread baru
    thread = threading.Thread(
        target=handle_client,
        args=(client_socket,)
    )

    thread.start()