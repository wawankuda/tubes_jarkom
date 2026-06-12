import threading
import socket
import time

PROXY = ("172.24.174.243", 8080)
URLS = ["/index.html", "/index.html", "/page1.html", "/page2.html", "/index.html"]

def fetch(i, url):
    """Mengirim HTTP GET Request via Proxy dan menghitung RTT."""
    start = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect(PROXY)
        s.sendall(f"GET {url} HTTP/1.1\r\nHost: {PROXY[0]}\r\n\r\n".encode())
        
        # Ekstrak baris pertama respons (contoh: HTTP/1.1 200 OK)
        status = s.recv(4096).decode(errors='ignore').split('\r\n')[0]
        s.close()
        
        rtt = (time.time() - start) * 1000
        print(f"[Thread-{i}] {url} -> {status} ({rtt:.1f} ms)")
    except Exception as e:
        print(f"[Thread-{i}] {url} -> Error: {e}")

if __name__ == "__main__":
    print(f"=== Memulai Simulasi Multi-Client ({len(URLS)} Thread) ===")
    
    # Membuat dan menjalankan thread secara bersamaan
    threads = [threading.Thread(target=fetch, args=(i+1, url)) for i, url in enumerate(URLS)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    print("=== Simulasi Selesai ===")
