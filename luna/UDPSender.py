#! /usr/bin/env python3
#
# Copyright (c) 2020 ZKM | Museums Technik
# Daniel Heiss <heiss@zkm.de>
# Marc Schütze <mschuetze@zkm.de>
#
# Copyright (c) 2021 ZKM | Hertz-Labor
# Dan Wilcox <dan.wilcox@zkm.de>
# Paul Bethge <bethge@zkm.de>
#
# BSD Simplified License.
# For information on usage and redistribution, and for a DISCLAIMER OF ALL
# WARRANTIES, see the file, "LICENSE.txt," in this distribution.
#
# This code has been developed at ZKM | Hertz-Lab as part of „The Intelligent
# Museum“ generously funded by the German Federal Cultural Foundation.

import socket

# raw UDP message sender
class UDPSender:

    # init with address pair: (host, port)
    def __init__(self, addr):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = addr
        self.message = "distance" # message text

    # send distance value
    # TODO: ignore sending until timeout after a send error?
    def send(self, distance, tfluna):
        message = self.message + " " + str(tfluna.devid) if tfluna.devid else self.message
        message = (message + " " + str(distance)).encode()
        try:
            self.client.sendto(message, self.addr)
        except Exception as e:
            print(f"udp sender: send error: {e}")

    # print settings
    def print(self):
        host,port = self.addr
        print(f"udp sender: {host} {port}")
        print(f"udp sender: sending {self.message}")
