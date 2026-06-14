import socket
import time
import argparse

# Konfigurasi IP dan Port sesuai dengan file proxy.py dan webserver.py
PROXY_HOST = "192.168.100.16"  # IP Proxy
PROXY_PORT = 8080              # Port Proxy TCP

SERVER_HOST = "192.168.100.123" # IP Web Server
UDP_PORT = 9000                # Port UDP Web Server (Echo Server)

def run_tcp():
    """Fungsi untuk menjalankan mode TCP (HTTP Request via Proxy)"""
    print(f"[*] Menghubungi Proxy Server di {PROXY_HOST}:{PROXY_PORT}")
    try:
        # Inisiasi socket TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((PROXY_HOST, PROXY_PORT))
        
        # Format HTTP Request
        request = f"GET /index.html HTTP/1.1\r\nHost: {PROXY_HOST}\r\n\r\n"
        client_socket.send(request.encode())
        
        # Menerima response
        response = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            response += data
            
        print("\n=== RESPONSE DARI PROXY/SERVER ===")
        print(response.decode(errors='ignore'))
        
    except Exception as e:
        print(f"[!] Error TCP: {e}")
    finally:
        client_socket.close()

def run_udp():
    """Fungsi untuk menjalankan mode UDP (QoS Test ke Server langsung via Proxy)"""
    print(f"[*] Mengirim paket QoS (UDP) ke {PROXY_HOST}:{UDP_PORT}")
    
    # Inisiasi socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(2.0) # Timeout 2 detik jika paket hilang
    
    num_pings = 10
    received = 0
    rtt_list = []
    total_bytes = 0
    
    start_test = time.time()
    
    for i in range(1, num_pings + 1):
        send_time = time.time()
        # Payload pesan sesuai spesifikasi
        message = f"Ping {i} {send_time}"
        
        try:
            client_socket.sendto(message.encode(), (PROXY_HOST, UDP_PORT))
            data, addr = client_socket.recvfrom(1024)
            recv_time = time.time()
            
            # Hitung RTT dalam satuan milidetik (ms)
            rtt = (recv_time - send_time) * 1000
            rtt_list.append(rtt)
            received += 1
            total_bytes += len(data)
            
            print(f"Reply dari {addr[0]}: seq={i} time={rtt:.2f} ms")
        except socket.timeout:
            print(f"Request timeout untuk seq={i}")
            
    end_test = time.time()
    
    # Kalkulasi Parameter QoS
    loss = ((num_pings - received) / num_pings) * 100
    avg_rtt = sum(rtt_list) / len(rtt_list) if received > 0 else 0
    
    # Hitung Jitter (Variasi delay antar paket yang berurutan)
    jitter = 0
    if len(rtt_list) > 1:
        diffs = [abs(rtt_list[j] - rtt_list[j-1]) for j in range(1, len(rtt_list))]
        jitter = sum(diffs) / len(diffs)
        
    # Hitung Throughput (bps)
    duration = end_test - start_test
    throughput = (total_bytes * 8) / duration if duration > 0 else 0
    
    print("\n=== STATISTIK QoS ===")
    print(f"Packet Loss : {loss:.1f}%")
    print(f"Average RTT : {avg_rtt:.2f} ms")
    print(f"Jitter      : {jitter:.2f} ms")
    print(f"Throughput  : {throughput:.2f} bps")
    
    client_socket.close()

if __name__ == "__main__":
    # Parsing argumen command line
    parser = argparse.ArgumentParser(description="Client untuk Tugas Besar Jaringan Komputer")
    parser.add_argument('--mode', choices=['tcp', 'udp'], required=True, help="Pilih mode: tcp (HTTP via Proxy) atau udp (QoS monitoring)")
    
    args = parser.parse_args()
    
    if args.mode == 'tcp':
        run_tcp()
    elif args.mode == 'udp':
        run_udp()