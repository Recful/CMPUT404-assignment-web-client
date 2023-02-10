#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        o = urllib.parse.urlparse(url)
        host = o.netloc.split(':')[0]
        if ':' not in o.netloc:
            port = 80
        else:
            port = int(o.netloc.split(':')[1])
        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.splitlines()
        code = code[0].split()[1]
        
        return int(code)

    def get_headers(self,data):
        
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        host = self.get_host_port(url)[0]
        port = self.get_host_port(url)[1]
        # print(host)
        # print(port)
        # print(type(port))
        # path = urllib.parse.urlparse(url)
        # print(path)
        text = "GET %s" % url
        text += " HTTP/1.1\r\n"
        text += "Host: "
        text += "%s:%d" % (host, port)
        text += "\r\n"
        text += "Connection: close"
        text += "\r\n\r\n"
        self.connect(host, port)
        self.sendall(text)
        return_info = self.recvall(self.socket)
        # print("here's your response: ")
        # print(return_info)
        header = self.get_headers(return_info)
        code = self.get_code(return_info)
        body = self.get_body(return_info)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        post_content = ""
        host = self.get_host_port(url)[0]
        port = self.get_host_port(url)[1]
        if args: #change the input into the format of: key1=value1&key2=value2
            for key,value in args.items():
                post_content += "%s=%s" % (key, value)
                post_content += "&"
            #get rid of the last &
            post_content = post_content[:-1]
        # print("post_content:")
        # print(post_content)
        text = "POST %s" % url
        text += " HTTP/1.1\r\n"
        text += "Host: "
        text += "%s:%d" % (host, port)
        text += "\r\n"
        text += "Connection: close\r\n"
        text += "Content-Type: application/x-www-form-urlencoded\r\n"
        text += "Content-Length: %d\r\n\r\n" % (len(post_content))
        #add the post content into the message that will be sent
        text += post_content
        text += "\r\n\r\n"

        self.connect(host, port)
        self.sendall(text)
        return_info = self.recvall(self.socket)
        header = self.get_headers(return_info)
        code = self.get_code(return_info)
        body = self.get_body(return_info)
        self.close()

        return HTTPResponse(code, body)

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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
