import socket
import threading
import ssl
import json
import time
from datetime import datetime

def banner_grab(ip, port, family):
    """Connect to a TCP port and send protocol-specific data to get a banner."""
    banner = ''
    try:
        # Create TCP socket based on IP version
        if family == socket.AF_INET6:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((ip, port))
    except Exception:
        return None  # Unable to connect (shouldn't happen if port was detected open)
    try:
        # HTTP
        if port == 80:
            payload = (b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n") if isinstance(ip, str) else b"HEAD / HTTP/1.0\r\n\r\n"
            sock.send(payload)
            banner = sock.recv(1024).decode(errors='ignore')
        # HTTPS
        elif port == 443:
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                secure_sock = context.wrap_socket(sock, server_hostname=ip if isinstance(ip, str) else None)
                secure_sock.settimeout(2.0)
                payload = (b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n") if isinstance(ip, str) else b"HEAD / HTTP/1.0\r\n\r\n"
                secure_sock.send(payload)
                banner = secure_sock.recv(1024).decode(errors='ignore')
                secure_sock.close()
            except Exception:
                # If TLS handshake fails, try plain HTTP (could get error banner)
                try:
                    payload = (b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n") if isinstance(ip, str) else b"HEAD / HTTP/1.0\r\n\r\n"
                    sock.send(payload)
                    banner = sock.recv(1024).decode(errors='ignore')
                except Exception:
                    banner = ''
        # FTP
        elif port == 21:
            banner = sock.recv(1024).decode(errors='ignore')
            try:
                sock.send(b"USER anonymous\r\n")
                _ = sock.recv(1024).decode(errors='ignore')
                sock.send(b"PASS anonymous\r\n")
                _ = sock.recv(1024).decode(errors='ignore')
            except Exception:
                pass
        # SMTP
        elif port in (25, 587):
            banner = sock.recv(1024).decode(errors='ignore')
        # POP3
        elif port in (110, 995):
            banner = sock.recv(1024).decode(errors='ignore')
        # IMAP
        elif port in (143, 993):
            banner = sock.recv(1024).decode(errors='ignore')
        # SSH
        elif port == 22:
            banner = sock.recv(1024).decode(errors='ignore')
        # Telnet
        elif port == 23:
            try:
                sock.send(b"\r\n")
                banner = sock.recv(1024).decode(errors='ignore')
            except Exception:
                banner = sock.recv(1024).decode(errors='ignore') or ''
        # Generic fallback: try to receive any initial data
        else:
            try:
                sock.send(b"\r\n")
            except Exception:
                pass
            try:
                banner = sock.recv(1024).decode(errors='ignore')
            except Exception:
                banner = ''
    except Exception:
        banner = ''
    finally:
        sock.close()
    return banner.strip()

def scan_ports(target, ports, results, lock, use_udp=False, family=socket.AF_INET):
    """Scan a list of ports on the target; record open ports and banners."""
    for port in ports:
        if use_udp:
            # UDP scanning: send empty packet and see if any response arrives
            try:
                if family == socket.AF_INET6:
                    udp_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                else:
                    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_sock.settimeout(1.0)
                udp_sock.sendto(b"", (target, port))
                try:
                    data, _ = udp_sock.recvfrom(1024)
                    # Received data: consider port open
                    banner = data.decode(errors='ignore').strip()
                    with lock:
                        results.append({"port": port, "protocol": "UDP", "banner": banner})
                except socket.timeout:
                    # No response (filtered or open)
                    pass
                except Exception:
                    # ICMP port unreachable (closed)
                    pass
                udp_sock.close()
            except Exception:
                continue
        else:
            # TCP scan: use connect_ex for non-blocking attempt
            try:
                if family == socket.AF_INET6:
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                res = sock.connect_ex((target, port))
                sock.close()
            except Exception:
                continue
            if res == 0:
                # Port is open; grab banner
                banner = banner_grab(target, port, family)
                with lock:
                    results.append({"port": port, "protocol": "TCP", "banner": banner})

def generate_report(data, filename):
    """Write scan results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("Threaded Port Scanner with Banner Grabbing and JSON Reporting")
    target = input("Enter target (IP or hostname): ").strip()
    ip_version = input("Scan IPv4 or IPv6? (4/6): ").strip()
    family = socket.AF_INET6 if ip_version == '6' else socket.AF_INET
    port_range = input("Enter port range (e.g., 1-1024): ").strip()
    if '-' in port_range:
        start_port, end_port = port_range.split('-')
    else:
        start_port = end_port = port_range
    start_port, end_port = int(start_port), int(end_port)
    ports = list(range(start_port, end_port + 1))
    proto_choice = input("Scan TCP or UDP? (tcp/udp): ").strip().lower()
    use_udp = (proto_choice == 'udp')
    try:
        thread_count = int(input("Enter number of threads: ").strip())
    except Exception:
        thread_count = 10

    print(f"\nStarting scan on {target} ({'IPv6' if family==socket.AF_INET6 else 'IPv4'}) ports {start_port}-{end_port} using {thread_count} threads ...")
    start_time = time.time()

    # Launch threads with balanced port distribution
    threads = []
    results = []
    lock = threading.Lock()
    for i in range(thread_count):
        chunk = ports[i::thread_count]  # balanced slice
        if not chunk:
            continue
        t = threading.Thread(target=scan_ports, args=(target, chunk, results, lock, use_udp, family))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nScan completed in {duration:.2f} seconds. Open ports:")
    if results:
        results.sort(key=lambda x: x["port"])
        for entry in results:
            port = entry["port"]
            proto = entry["protocol"]
            banner = entry["banner"] or "(no banner)"
            print(f" - Port {port}/{proto}: {banner}")
    else:
        print("No open ports found.")

    # Prepare and optionally save JSON report
    report = {
        "target": target,
        "ip_version": "IPv6" if family==socket.AF_INET6 else "IPv4",
        "protocol": proto_choice.upper(),
        "port_range": f"{start_port}-{end_port}",
        "thread_count": thread_count,
        "scan_duration_secs": round(duration, 2),
        "timestamp": datetime.now().isoformat(),
        "open_ports": results
    }
    save = input("\nSave report to JSON file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        generate_report(report, filename)
        print(f"Results saved to {filename}")
    print("Done.")

if __name__ == "__main__":
    main()