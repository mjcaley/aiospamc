#!/usr/bin/env python3

import re
import socket

from spamc.requests import *
from spamc.responses import *


SERVER_SIGNATURE = re.compile(r'^SPAMD/\d+\.\d+ ') 

class BadResponse(Exception):
    def __init__(self, response):
        self.response = response
        
class NoSSL(Exception):
    def __init__(self, description):
        self.description = description
        
class Client:
    def __init__(self, host = 'localhost', port = 783, ip_version = 4, ssl = False, **ssl_options):
        self.host = host
        self.port = port
        self.ip_version = ip_version
        self.ssl = ssl
        self.ssl_options = ssl_options
        
    def connect(self):
        if self.ip_version is 4:
            sock = socket.socket(socket.AF_INET)
        elif self.ip_version is 6:
            sock = socket.socket(socket.AF_INET6)
        else:
            raise OSError('Invalid address family, must be IPv 4 or 6')
        sock.connect((self.host, self.port))
        
        if self.ssl:
            try:
                import ssl
            except ImportError:
                raise NoSSL('SSL is not supported by this installation')
                
            ssl_sock = ssl.wrap_socket(sock, **self.ssl_options)
            return ssl_sock
        else:
            return sock
        
    def send(self, request):
        conn = self.connect()
        conn.send(bytes(request))
        data = bytes()
        while True:
            received = conn.recv(1024)
            if not received:
                break
            data += received
        response = SpamdResponse.parse(data.decode())
        conn.close()
        
        return response
    
    def check(self, message, user = None):
        request = Check(message = message)
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
        
    def headers(self, message, user = None):
        request = Headers(message = message)
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
        
    def ping(self, user = None):
        request = Ping()
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
    
    def process(self, message, user = None):
        request = Process(message = message)
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
    
    def report(self, message, user = None):
        request = Report(message = message)
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
    
    def report_if_spam(self, message, user = None):
        request = ReportIfSpam(message = message)
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
    
    def symbols(self, message, user = None):
        request = Symbols(message = message)
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
    
    def tell(self,
             message_class: MessageClassOption,
             message,
             set_destinations = {'local': False, 'remote': False},
             remove_destinations = {'local': False, 'remote': False}, 
             user = None
            ):
        request = Tell(message,
                       [ MessageClass(message_class),
                         Set(**set_destinations),
                         Remove(**remove_destinations)
                       ])
        if user:
            request.headers.append(User(user))
        response = self.send(bytes(request))
        
        return response
        