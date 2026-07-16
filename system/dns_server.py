"""Servidor DNS interno"""
import socket
import threading
from system.config import DNS_FILE, load_json, save_json, log

class KalmDNSServer:
    def __init__(self, port):
        self.port = port
        self.rules = load_json(DNS_FILE, {
            "kalm.local": "127.0.0.1",
            "api.kalm.local": "127.0.0.1",
            "tempest.local": "127.0.0.1",
            "nazarick.local": "127.0.0.1",
            "d.local": "127.0.0.1"
        })
        self.running = False
    
    def get_rules(self):
        return self.rules
    
    def add_rule(self, domain, ip):
        self.rules[domain] = ip
        save_json(DNS_FILE, self.rules)
        log(f"DNS: {domain} -> {ip}")
    
    def remove_rule(self, domain):
        if domain in self.rules:
            del self.rules[domain]
            save_json(DNS_FILE, self.rules)
    
    def parse_query(self, data):
        try:
            idx, domain = 12, ""
            while idx < len(data):
                l = data[idx]
                if l == 0: break
                idx += 1
                domain += data[idx:idx+l].decode("ascii") + "."
                idx += l
            return domain.rstrip(".")
        except:
            return None
    
    def build_response(self, qd, domain, ip):
        try:
            hdr = qd[:4] + b"\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00"
            ans = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + socket.inet_aton(ip)
            return hdr + qd[12:] + ans
        except:
            return None
    
    def handle(self, data, addr, sock):
        domain = self.parse_query(data)
        if domain:
            log(f"DNS Query: {domain}")
            ip = self.rules.get(domain)
            if ip:
                r = self.build_response(data, domain, ip)
                if r: sock.sendto(r, addr)
            else:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(3)
                    s.sendto(data, ("8.8.8.8", 53))
                    resp, _ = s.recvfrom(4096)
                    sock.sendto(resp, addr)
                    s.close()
                except:
                    pass
    
    def run(self):
        self.running = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", self.port))
            log(f"🌐 DNS en puerto {self.port}")
            while self.running:
                try:
                    sock.settimeout(1.0)
                    data, addr = sock.recvfrom(4096)
                    threading.Thread(target=self.handle, args=(data, addr, sock), daemon=True).start()
                except socket.timeout:
                    continue
        except PermissionError:
            log(f"⚠️ Puerto {self.port} requiere admin", "WARN")
        finally:
            sock.close()
    
    def stop(self):
        self.running = False