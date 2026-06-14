import socket
import threading
import os
import time

HOST = "0.0.0.0"
PORT = 8080
SERVER_HOST = "192.168.100.123"
SERVER_PORT = 8000
CACHE_DIR = "proxy_cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def handle_tcp_client(client_socket, client_address):
    start_time = time.time()
    client_ip = client_address[0]
    
    try:
        request_data = client_socket.recv(4096)
        if not request_data:
            client_socket.close()
            return
            
        request_string = request_data.decode(errors='ignore')
        parts = request_string.split(' ')
        
        if len(parts) > 1:
            url = parts[1]
        else:
            url = "/"
            
        safe_url = url.replace("/", "_")
        if safe_url == "" or safe_url == "_":
            safe_url = "_index.html"
            
        cache_path = os.path.join(CACHE_DIR, safe_url)
        
        if os.path.exists(cache_path):
            # CACHE HIT
            with open(cache_path, "rb") as file:
                response_data = file.read()
            status = "HIT"
            
        else:
            # CACHE MISS
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(5.0)
                server_socket.connect((SERVER_HOST, SERVER_PORT))
                server_socket.send(request_data)
                
                response_data = b""
                while True:
                    chunk = server_socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                
                server_socket.close()
                
                with open(cache_path, "wb") as file:
                    file.write(response_data)
                status = "MISS"
                
            except socket.timeout:
                html_error = "<h1>504 Gateway Timeout</h1>"
                response_data = ("HTTP/1.1 504 Gateway Timeout\r\n\r\n" + html_error).encode()
                status = "ERROR 504"
                
            except Exception:
                html_error = "<h1>502 Bad Gateway</h1>"
                response_data = ("HTTP/1.1 502 Bad Gateway\r\n\r\n" + html_error).encode()
                status = "ERROR 502"
                
        client_socket.send(response_data)
        
        response_time = time.time() - start_time
        print(f"[TCP LOG] IP: {client_ip} | URL: {url} | Status: {status} | Waktu: {response_time:.4f}s")
        
    except Exception as e:
        print(f"Error TCP pada client {client_ip}: {e}")
        
    finally:
        client_socket.close()

def start_tcp_proxy():
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_server.bind((HOST, PORT))
    proxy_server.listen(50)
    print(f"Proxy Server (TCP) Berjalan di Port {PORT}")

    while True:
        client_socket, client_address = proxy_server.accept()
        client_thread = threading.Thread(
            target=handle_tcp_client, 
            args=(client_socket, client_address)
        )
        client_thread.start()

def start_udp_proxy():
    proxy_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_udp.bind((HOST, 9000))
    print(f"Proxy Forwarder (UDP) Berjalan di Port 9000")
    
    while True:
        data, client_addr = proxy_udp.recvfrom(1024)
        print(f"[UDP LOG] Meneruskan PING dari {client_addr[0]} ke Web Server")
        
        # Buat socket sementara untuk menghubungi Web Server
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.settimeout(2.0)
        
        try:
            # Lempar ke Web Server
            temp_socket.sendto(data, (SERVER_HOST, 9000))
            
            # Terima pantulan dari Web Server
            response_data, _ = temp_socket.recvfrom(1024)
            
            # Kembalikan pantulan itu ke Client
            proxy_udp.sendto(response_data, client_addr)
        except socket.timeout:
            pass # Abaikan jika timeout, Client yang akan mencatat Packet Loss
        finally:
            temp_socket.close()

if __name__ == "__main__":
    # Jalankan Proxy TCP dan UDP secara bersamaan
    threading.Thread(target=start_tcp_proxy, daemon=True).start()
    start_udp_proxy()
