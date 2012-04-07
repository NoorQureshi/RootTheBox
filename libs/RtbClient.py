#!/usr/bin/env python

'''
Created on Feb 24, 2012

@author: moloch
'''

import os
import sys
import time
import socket
import random
import urllib
import httplib
import platform

from hashlib import sha256

BUFFER_SIZE = 1024

class RtbClient():
    ''' Root the Box Reporter '''

    def __init__(self, display_name):
        self.listen_port = None
        self.user = urllib.urlencode({'handle': display_name})
        self.remote_host = self.__rhost__()
        self.linux_root_path = "/root/garbage"
        self.linux_user_path = "/var/garbage"
        self.windows_root_path = "C:\\root_garbage.txt"
        self.windows_user_path = "C:\\user_garbage.txt"
        self.level = None
    
    def start(self):
        ''' Main entry point '''
        self.load_key_file()
        if self.register():
            self.reporter()
        else:
            sys.stdout.write('[!] Error: Failed to acquire configuration infomation\n')
    
    def load_key_file(self):
        ''' Loads the key file '''
        if platform.system().lower() == "linux":
            sys.stdout.write('[*] Detected Linux operating system (%s) \n' % (platform.release(),))
            sys.stdout.write('[*] Attempting to load root key from %s ... ' % (self.linux_root_path,))
            sys.stdout.flush()
            level = 'root'
            key_value = self.__load__(self.linux_root_path)
            if key_value == None:
                sys.stdout.write("failure\n[*] Attempting to read user key from %s ... " % (self.linux_user_path,))
                sys.stdout.flush()
                level = 'user'
                key_value = self.__load__(self.linux_user_path)
                if key_value == None:
                    sys.stdout.write("failure\n[!] Error: Unable to read key file(s)\n")
                    os._exit(1)
        elif platform.system().lower() == "windows":
            sys.stdout.write("[*] Detected Windows %s operating system\n" % (platform.release(),))
            sys.stdout.write("[*] Attempting to load root key from %s ... " % (self.windows_root_path,))
            sys.stdout.flush()
        else:
            sys.stdout.write("[!] Error: Platform not supported (%s)\n" % (platform.release(),))
            sys.stdout.flush()

    def __load__(self, path):
        ''' Reads a file at path returns the file contents or None '''
        if os.path.exists(path) and os.path.isfile(path):
            key_file = open(path, 'r')
            key_data = key_file.read()
            key_file.close
            return key_data
        else:
            return None

    def __rhost__(self):
        ''' Finds the ip address of the scoring engine '''
        sys.stdout.write("[*] Finding scoring engine address, please wait ...")
        sys.stdout.flush()
        ip = socket.gethostbyname('game.rootthebox.com')
        sys.stdout.write("\r[*] Found scoring engine at %s             \n" % ip)
        return ip

    def reporter(self):
        ''' Listens for the scoring engine '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sys.stdout.write('[*] Binding to port %d \n' % self.listenPort)
        sock.bind(("", self.listen_port))
        sock.listen(1)
        while True:
            try:
                sys.stdout.write('\r[*] Reporter listening ...\t\t\t\t\t\r ')
                sys.stdout.flush()
                connection, address = sock.accept()
                sys.stdout.write('\r[*] Connection from %s' % address[0])
                sys.stdout.flush()
                if address[0] != self.remote_host:
                    sys.stdout.write('\n[!] Warning: Connection attempt from unkown address (%s)\n' % address[0])
                    sys.stdout.flush()
                    connection.sendall(" >:( Go away!\r\n")
                    connection.close()
                else:
                    checksum = sha256()
                    connection.sendall(self.level)
                    xid = connection.recv(BUFFER_SIZE)
                    sys.stdout.write('\r[*] Got xid: %s' % xid)
                    sys.stdout.flush()
                    checksum.update(self.key_value + xid)
                    result = checksum.hexdigest()
                    time.sleep(0.1)
                    connection.sendall(result)
                    sys.stdout.write('\r[*] Sent checksum: %s' % result)
                    sys.stdout.flush()
                    time.sleep(0.5)
            except socket.error, err:
                sys.stdout.write('\n[!] Unable to configure socket (%s)\n' % err)
                sys.stdout.flush()
                os._exit(1)
    
    def register(self):
        ''' Retrieves configuration information from the scoring engine '''
        connection = httplib.HTTPConnection(self.remote_host)
        connection.request("GET", "/reporter/register?%s" % self.user)
        response = connection.getresponse()
        if response.status == 200:
            data = response.read()
            try:
                self.listen_port = int(data)
                return True
            except:
                sys.stdout.write('[!] Error: %s' % data)
                sys.stdout.flush()
        return False

def help():
    ''' Displays a helpful message '''
    sys.stdout.write("Root the Box VII - Reporter - v0.1 \n")
    sys.stdout.write("Usage:\n\treporter.py <hacker name>\n")
    sys.stdout.write("Options:\n")
    sys.stdout.write("\t--help...............................Display this helpful message\n")
    sys.stdout.flush()
  
if __name__ == '__main__':
    ''' float main() '''
    if "--help" in sys.argv or "-h" in sys.argv or "/?" in sys.argv:
        help()
    elif 2 <= len(sys.argv):
        sys.stdout.write("[*] Root the Box VII - Good Hunting!\n")
        client = RtbClient(sys.argv[1])
        client.start()
    else:
        sys.stdout.write("[!] PEBKAC: Too few or too many arguments, see --help\n")
        sys.stdout.flush()
    os._exit(0)
