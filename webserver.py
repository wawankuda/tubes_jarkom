import socket
import threading
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 8000

def log_request(client_ip, filename, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[{timestamp}] "
        f"IP: {client_ip} | "
        f"File: {filename} | "
        f"Status: {status}"
    )


def handle_client(client_socket, address):

    try:

        request = client_socket.recv(1024).decode()

        if not request:
            client_socket.close()
            return

        print("\n===== REQUEST =====")
        print(request)

        # contoh:
        # GET /index.html HTTP/1.1
        first_line = request.split("\r\n")[0]

        parts = first_line.split()

        if len(parts) < 2:
            client_socket.close()
            return

        path = parts[1]

        # jika akses root
        if path == "/":
            path = "/index.html"

        filename = path.lstrip("/")

        # cek file ada atau tidak
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

        html = """
        <html>
        <body>
            <h1>500 Internal Server Error</h1>
        </body>
        </html>
        """

        response = (
            "HTTP/1.1 500 Internal Server Error\r\n"
            f"Content-Length: {len(html.encode())}\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            + html
        )

        try:
            client_socket.send(response.encode())
        except:
            pass

    finally:
        client_socket.close()


def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Web Server berjalan di {HOST}:{PORT}")

    while True:

        client_socket, address = server.accept()

        print(f"\nClient terhubung: {address}")

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address)
        )

        thread.start()


if __name__ == "__main__":
    start_server()