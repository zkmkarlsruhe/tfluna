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

import requests
from concurrent.futures import ThreadPoolExecutor

# ThingsBoard message sender
class TBSender:

    # init with thingsboard url (including access token) and optional threading
    def __init__(self, url, threading=False):
        self.url = url
        self.message = "isThere" # message name
        self.is_there = False # is someone/something there? ie. blocking sensor
        self.verbose = False
        self.pool = None
        if(threading):
            self.pool = ThreadPoolExecutor(16) # worker thread pool

    # send event on change
    def send(self, distance, tfluna):
        is_there = distance < tfluna.max_distance
        if is_there == self.is_there:
            return
        self.is_there = is_there
        if self.verbose:
            print(f"tb sender: {self.message} {self.is_there}")
        payload = {self.message: int(self.is_there == True)}
        if self.pool:
            self.pool.submit(self._post, (payload))
        else:
            self._post(payload)

    # print settings
    def print(self):
        print(f"tb sender: {self.url}")
        print(f"tb sender: sending {self.message}")

    # send the post request with json payload
    def _post(self, payload):
        try:
            req = requests.post(self.url, json=payload)
            if req.status_code != 200:
                print(f"tb sender: send error {req.status_code}")
        except Exception as e:
            print(f"tb sender: send error: {e}")
