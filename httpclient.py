#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Eric Lam, Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    client_socket = socket.socket();

    # Get the Host, Port, and Path which will be stored in 'data' in that order
    def get_host_port(self,url):
        data = []
        url = url.split("/")
        if ':' in url[2]:
            #print url
            data.append(url[2].split(":")[0])
            data.append(int(url[2].split(":")[1]))
            path = ""
            for x in range(3, len(url)):
                path += "/" + url[x]

            data.append(path)
        else:
            #print url
            data.append(url[2])
            data.append(80)
            path = ""
            for x in range(3, len(url)):
                path += "/" + url[x]
            data.append(path)
        
        #print "DATA IS HERE"
        #print data

        return data

    # Connect to the server
    def connect(self, host, port):
        # use sockets!
        #create an INET, STREAMing socket
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()
            
        print 'Socket Created'
        
        try:
            remote_ip = socket.gethostbyname( host )
        except socket.gaierror:
            #could not resolve
            print 'Hostname could not be resolved. Exiting'
            sys.exit()
         
        #Connect to remote server
        self.client_socket.connect((remote_ip , port))
        print 'Socket Connected to ' + host + ' on ip ' + remote_ip
        
        return None

    # Get the HTTP Status Code
    def get_code(self, data):
        data = data.split(' ')
        return int(data[1])

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        data = self.get_host_port(url)
        self.connect(data[0], data[1])
        
        request = "GET " + data[2] + " HTTP/1.1\r\nHost: "+data[0]+":"+str(data[1])+"\r\nConnection: keep-alive\r\nContent-Type: text/html\r\n"

        if(args != None):
            args = urllib.urlencode(args)
            request += 'Content-Length: %s \r\n' % (len(args))
            request += "\r\n"  
            request += args + "\r\n"

        request += "\r\n"

        #print "GET REQUEST IS HERE"
        #print request

        self.client_socket.send(request)

        body = self.recvall(self.client_socket)

        #print "GET BODY IS HERE"
        #print body
        
        code = self.get_code(body)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        data = self.get_host_port(url)
        self.connect(data[0], data[1])

        request = "POST " + data[2] + " HTTP/1.1\r\nHost:"+data[0]+":"+str(data[1])+"\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n"

        if(args != None):
            args = urllib.urlencode(args)
            request += 'Content-Length: %s \r\n' % (len(args))
            request += "\r\n"  
            request += args + "\r\n"

        request += "\r\n"

        #print "REQUEST IS HERE" 
        #print request

        self.client_socket.send(request)
        body = self.recvall(self.client_socket)

        #print "BODY IS HERE"
        #print body

        code = self.get_code(body)

        body = body.splitlines()
        body = body[len(body)-1]

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
