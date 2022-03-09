#! /usr/bin/env python3
#
# Copyright (c) 2020 ZKM | Museums Technik
# Daniel Heiss <heiss@zkm.de>
# Marc Schütze <mschuetze@zkm.de>
#
# BSD Simplified License.
# For information on usage and redistribution, and for a DISCLAIMER OF ALL
# WARRANTIES, see the file, "LICENSE.txt," in this distribution.
#
# ref: http://sfriederichs.github.io/how-to/python/udp/2017/12/07/UDP-Communication.html

import socket
from time import sleep

UDP_IP = "" # any address
UDP_PORT = 5005
is_running = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)

try:
    while is_running:
        try:
            data, addr = sock.recvfrom(1024)
            print("received message: %s" % data)
        except socket.error:
            pass
        sleep(0.1)
except KeyboardInterrupt:
    is_running = False
