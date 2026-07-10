import socket
import requests
from datetime import datetime

def scan_target():
    """
    Scan the target m.facebook.com for open ports and services
    """
    target = "m.facebook.com"
    print(f"[{datetime.now()}] Scanning target: {target}")
    print("-" * 50)
    
    # Get IP address
    try:
        ip_address = socket.gethostbyname(target)
        print(f"Host : {ip_address} ({target})")
        print("State : up")
        print("-" * 10)
    except Exception as e:
        print(f"Error resolving hostname: {e}")
        return
    
    # Check common ports
    ports_to_check = [80, 443]
    port_info = {80: {"name": "http", "proxy": "proxygen-bolt"}, 443: {"name": "https", "proxy": ""}}
    
    print("Protocol : tcp")
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            proxy_info = f"    {port_info[port]['proxy']}" if port_info[port]['proxy'] else ""
            print(f"port : {port:<7} state : open    name : {port_info[port]['name']:<7}{proxy_info}")
        sock.close()
    
    # Save scan results
    with open("scan_results.txt", "w") as f:
        f.write(f"Scan Results for {target}\n")
        f.write(f"IP Address: {ip_address}\n")
        f.write(f"Scan Time: {datetime.now()}\n")
        f.write("Open Ports:\n")
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                f.write(f"  Port {port}: Open ({port_info[port]['name']})\n")
            sock.close()

if __name__ == "__main__":
    scan_target()