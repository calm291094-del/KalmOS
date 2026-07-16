"""Registro global de instancias del sistema"""

dns_server = None
proxy_server = None
web_server = None

def set_dns_server(server):
    global dns_server
    dns_server = server

def set_proxy_server(server):
    global proxy_server
    proxy_server = server

def set_web_server(server):
    global web_server
    web_server = server

def get_dns_server():
    return dns_server

def get_proxy_server():
    return proxy_server