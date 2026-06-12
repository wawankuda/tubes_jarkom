import socket
import threading
import os
import time

HOST = "172.24.174.243"  # IP Proxy Anda
PORT = 8080

SERVER_HOST = "172.24.174.181"  # IP Web Server teman
SERVER_PORT = 8000

# Spek: Menyimpan response HTTP ke "local storage"
CACHE_DIR = "proxy_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def handle_client(client_socket, address):
    start_time = time.time()
    client_ip = address[0]
    
    try:
        # Terima request dari client
        request = client_socket.recv(4096)
        if not request:
            client_socket.close()
            return
            
        request_str = request.decode(errors='ignore')
        
        # Spek: Ekstrak URL untuk Logging
        try:
            url = request_str.split(' ')[1]
        except IndexError:
            url = "/"
            
        # Penamaan file cache di local storage
        safe_url = url.replace("/", "_")
        if safe_url == "_" or safe_url == "":
            safe_url = "_index.html"
        cache_path = os.path.join(CACHE_DIR, safe_url)
        
        # Spek: Cek Cache (HIT/MISS)
        if os.path.exists(cache_path):
            # --- CACHE HIT ---
            with open(cache_path, "rb") as f:
                response = f.read()
            client_socket.send(response)
            
            response_time = time.time() - start_time
            # Spek Logging: IP Client, URL, HIT/MISS, Response Time
            print(f"[LOG] IP: {client_ip} | URL: {url} | Status: HIT | Response Time: {response_time:.4f}s")
            
        else:
            # --- CACHE MISS ---
            try:
                # Hubungi Web Server
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(5.0) # Timeout 5 detik untuk cek 504
                server_socket.connect((SERVER_HOST, SERVER_PORT))
                
                # Forward request ke server
                server_socket.send(request)
                
                # Terima response dari server
                response = b""
                while True:
                    data = server_socket.recv(4096)
                    if len(data) > 0:
                        response += data
                    else:
                        break
                        
                server_socket.close()
                
                # Spek: Menyimpan Cache ke Local Storage
                with open(cache_path, "wb") as f:
                    f.write(response)
                    
                # Kirim balik ke client
                client_socket.send(response)
                
                response_time = time.time() - start_time
                print(f"[LOG] IP: {client_ip} | URL: {url} | Status: MISS | Response Time: {response_time:.4f}s")
                
            except socket.timeout:
                # Spek Penanganan Error: 504 Gateway Timeout
                error_504 = "HTTP/1.1 504 Gateway Timeout\r\n\r\n<h1>504 Gateway Timeout</h1>"
                client_socket.send(error_504.encode())
                response_time = time.time() - start_time
                print(f"[LOG] IP: {client_ip} | URL: {url} | Status: ERROR 504 | Response Time: {response_time:.4f}s")
                
            except Exception as e:
                # Spek Penanganan Error: 502 Bad Gateway
                error_502 = "HTTP/1.1 502 Bad Gateway\r\n\r\n<h1>502 Bad Gateway</h1>"
                client_socket.send(error_502.encode())
                response_time = time.time() - start_time
                print(f"[LOG] IP: {client_ip} | URL: {url} | Status: ERROR 502 | Response Time: {response_time:.4f}s")

    except Exception as e:
        print(f"Error handling client {client_ip}: {e}")
    finally:
        client_socket.close()

# Inisiasi Proxy Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(50)

print(f"Proxy Server (Multithreaded) berjalan di {HOST}:{PORT}")
print(f"Meneruskan request ke Web Server di {SERVER_HOST}:{SERVER_PORT}")

while True:
    # Spek: Multithreading (menangani banyak client bersamaan)
    client_socket, address = server.accept()
    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, address)
    )
    thread.start()
