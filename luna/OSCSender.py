#! /usr/bin/env python3
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

from pythonosc import udp_client

# Open Sound Control message sender
class OSCSender:

    # init with address pair: (host, port)
    def __init__(self, addr):
        host,port = addr
        self.client = udp_client.SimpleUDPClient(host, port)
        self.addr = addr
        self.address = "/distance" # OSC address

    # send distance value
    # TODO: ignore sending until timeout after a send error?
    def send(self, distance, tfluna):
        args = [tfluna.devid, distance] if tfluna.devid else distance
        try:
            self.client.send_message(self.address, args)
        except Exception as e:
            print(f"osc sender: send error: {e}")

    # print settings
    def print(self):
        host,port = self.addr
        print(f"osc sender: {host} {port}")
        print(f"osc sender: sending {self.address}")
