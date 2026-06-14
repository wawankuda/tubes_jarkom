import socket
import threading
import os
from datetime import datetime

HOST = "0.0.0.0"

TCP_PORT = 8000
UDP_PORT = 9000


def log_request(client_ip, filename, status):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[{timestamp}] "
        f"IP: {client_ip} | "
        f"File: {filename} | "
        f"Status: {status}"
    )


# ==========================
# TCP HANDLER
# ==========================
def handle_client(client_socket, address):

    try:

        request = client_socket.recv(4096).decode()

        if not request:
            return

        print("\n===== TCP REQUEST =====")
        print(request)

        first_line = request.split("\r\n")[0]
        parts = first_line.split()

        if len(parts) < 2:
            return

        path = parts[1]

        if path == "/":
            path = "/index.html"

        filename = path.lstrip("/")

        if os.path.exists(filename):

            with open(filename, "r", encoding="utf-8") as file:
                html = file.read()

            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Length: {len(html.encode())}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                + html
            )

            status = "200 OK"

        else:

            html = """
            <html>
            <body>
                <h1>404 Not Found</h1>
            </body>
            </html>
            """

            response = (
                "HTTP/1.1 404 Not Found\r\n"
                f"Content-Length: {len(html.encode())}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                + html
            )

            status = "404 Not Found"

        client_socket.send(response.encode())

        log_request(
            address[0],
            filename,
            status
        )

    except Exception as e:

        print("ERROR:", e)

    finally:

        client_socket.close()


# ==========================
# TCP SERVER
# ==========================
def start_tcp_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.bind((HOST, TCP_PORT))
    server.listen(5)

    print(f"[TCP] Web Server berjalan di {HOST}:{TCP_PORT}")

    while True:

        client_socket, address = server.accept()

        print(f"\n[TCP] Client terhubung: {address}")

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address)
        )

        thread.start()


# ==========================
# UDP SERVER
# ==========================
def start_udp_server():

    udp_server = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    udp_server.bind((HOST, UDP_PORT))

    print(f"[UDP] Echo Server berjalan di {HOST}:{UDP_PORT}")

    while True:

        data, addr = udp_server.recvfrom(1024)

        message = data.decode()

        print(
            f"[UDP] Dari {addr} : {message}"
        )

        # Echo kembali
        udp_server.sendto(
            data,
            addr
        )


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":

    tcp_thread = threading.Thread(
        target=start_tcp_server
    )

    udp_thread = threading.Thread(
        target=start_udp_server
    )

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()