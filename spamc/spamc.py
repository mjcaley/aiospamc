#!/usr/bin/env python3.5

import re
import socket


class BadResponse(Exception):
    def __init__(self, response):
        self.response = response

class SpamC:
    """Implements basic SPAMC protocol."""
    
    def __init__(self, host = '127.0.0.1', port = 783, default_buffer_size = 1024, user_agent_name = 'SPAMC'):
        self.host = host
        self.port = port
        self.default_buffer_size = default_buffer_size
        self.user_agent_name = user_agent_name
        self.user_agent_version = '1.5'
        
    def _connect(self):
        conn = socket.create_connection((self.host, self.port))
        return conn
    
    def _get_response(self, conn: socket.socket, buffer_size: int):
        response = conn.recvmsg(buffer_size)
        conn.close()
        return response[0].decode()
    
    def _build_user_agent(self, name: str = None, version: str = None):
        if not name:
            name = self.user_agent_name
        if not version:
            version = self.user_agent_version
        return '{}/{}'.format(name, version)
    
    def _build_request(self, header: str, options: list = None, body = None):
        if type(options) is str:
            request = '\r\n'.join([header, options])
        elif type(options) is list:
            request = '\r\n'.join([header, *options])
        else:
            request = header
        
        # add trailing newline and body if present
        request += '\r\n\r\n'
        if body:
            request += body
        
        return request.encode()
    
    def _build_header(self, command: str):
        return '{} {}'.format(command, self._build_user_agent())
    
    def _build_option(self, option: str, value: str):
        return '{} : {}'.format(option, value)
    
    def _send(self, request: bytes, buffer_size = None) -> str:
        if not buffer_size:
            buffer_size = self.default_buffer_size
        conn = self._connect()
        conn.send(request)
        return self._get_response(conn, buffer_size)
    
    def _verify_response(self, response: str) -> bool:
        valid_response = re.compile(r'^SPAMD/\d+\.\d+ ')
        result = valid_response.match(response)
        if result:
            return True
        else:
            return False
    
    def _parse_ping_response(self, response: str):
        valid_response = re.compile(r'.+ (?P<time>\d+) (?P<method>PONG)')
        return valid_response.match(response).groups()
    
    def ping(self):
        header = self._build_header('PING')
        request = self._build_request(header)
        response = self._send(request)
        if self._verify_response(response):
            return self._parse_ping_response(response)
        else:
            raise BadResponse(response)