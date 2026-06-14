import socket, time
from concurrent.futures import ThreadPoolExecutor

PROXY = ("192.168.100.16", 8080)
URLS = ["/index.html", "/index.html", "/page1.html", "/page2.html", "/index.html"] * 10

def fetch(i, url):
    start = time.time()
    try:
        s = socket.socket()
        s.settimeout(5.0)
        s.connect(PROXY)
        s.sendall(f"GET {url} HTTP/1.1\r\nHost: {PROXY[0]}\r\n\r\n".encode())
        res = s.recv(4096)
        s.close()
        rtt = (time.time() - start) * 1000
        status = res.split(b'\r\n')[0].decode(errors='ignore')
        print(f"[{i}] {url} -> {status} ({rtt:.1f} ms) [{len(res)}B]")
        return rtt, len(res)
    except Exception as e:
        print(f"[Thread{i}] {url} -> Error: {e}")
        return None

if __name__ == "__main__":
    print(f"=== Memulai Simulasi ({len(URLS)} Thread) ===")
    t0 = time.time()
    
    with ThreadPoolExecutor() as ex:
        results = list(ex.map(lambda p: fetch(*p), enumerate(URLS, 1)))
        
    t_tot = time.time() - t0
    sukses = [r for r in results if r]
    rtts = [r[0] for r in sukses]
    total_bytes = sum(r[1] for r in sukses)
    
    gagal = len(URLS) - len(sukses)
    jitter = sum(abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))) / (len(rtts)-1) if len(rtts) > 1 else 0
    kbps = (total_bytes * 8) / t_tot / 1000 if t_tot > 0 else 0

    print(f"\n--- Hasil QoS ---")
    print(f"Total   : {len(URLS)} Request | {len(sukses)} Sukses | {gagal} Gagal")
    print(f"Waktu   : {t_tot:.2f} detik  | Data: {total_bytes} Bytes")
    print(f"Loss    : {gagal/len(URLS)*100:.1f} %")
    print(f"Delay   : {sum(rtts)/len(rtts) if rtts else 0:.1f} ms")
    print(f"Jitter  : {jitter:.1f} ms")
    print(f"Thrp    : {kbps:.1f} Kbps")
