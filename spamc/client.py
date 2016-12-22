#!/usr/bin/env python3

import re
import socket

from spamc.requests import *
from spamc.responses import *


SERVER_SIGNATURE = re.compile(r'^SPAMD/\d+\.\d+ ') 

class BadResponse(Exception):
    def __init__(self, response):
        self.response = response
        
class Client:
    def __init__(self, host = 'localhost', port = 783, ip_version = socket.AF_INET, ssl = False):
        self.host = host
        self.port = port
        self.ip_version = ip_version
        self.ssl = ssl
        
    def connect(self):
        sock = socket.socket(self.ip_version)
        if self.ssl:
            try:
                import ssl
            except ImportError:
                conn = None
            else:
                context = ssl.create_default_context()
                conn = context.wrap_socket(sock,
                                           server=self.host)
                conn.connect((self.host, self.port))
                return conn
        else:
            sock.connect((self.host, self.port))
            return sock
        
    def send(self, request):
        conn = self.connect()
        conn.send(bytes(request))
        conn.shutdown(socket.SHUT_WR)
        data = bytes()
        while True:
            received = conn.recv(4096)
            if not received:
                break
            data += received
        response = SpamdResponse.parse(data.decode())
        conn.close()
        
        return response
    
    def check(self, message):
        request = Check(message)
        response = self.send(bytes(request))
        
        return response
        
    def ping(self):
        request = Ping()
        response = self.send(bytes(request))
        
        return response
    
    def report(self, message):
        request = Report(message)
        response = self.send(bytes(request))
        
        return response
    
    def report_if_spam(self, message):
        request = ReportIfSpam(message)
        response = self.send(bytes(request))
        
        return response
    
    def symbols(self, message):
        request = Symbols(message)
        response = self.send(bytes(request))
        
        return response