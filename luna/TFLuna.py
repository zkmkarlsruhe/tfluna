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

import serial
import time

##### math

# map a value within an input range min-max to an output range
def map_value(value, inmin, inmax, outmin, outmax):
    # the following is borrowed from openframeworks ofMath.cpp
    if abs(inmin - inmax) < 0.0001:
        return outmin
    else:
        outval = ((value - inmin) / (inmax - inmin) * (outmax - outmin) + outmin)
        if outmax < outmin:
            if outval < outmax:
                outval = outmax
            elif outval > outmin:
                outval = outmin
        else:
            if outval > outmax:
                outval = outmax
            elif outval < outmin:
                outval = outmin
        return outval

# clamp a value to an output range min-max
def clamp_value(value, outmin, outmax):
    return max(min(value, outmax), outmin)

##### TFLuna

class TFLuna:

    # init with dev path/name and optional baud rate, device identifier, or verbosity
    def __init__(self, dev, rate=115200, devid=None, verbose=True):
        self.serial = serial.Serial(dev, rate)
        self.devid = devid      # optional device identifier, unrelated to serial dev
        self.prev_distance = 0  # previous distance in cm
        self.max_distance = 200 # distance threshold in cm
        self.epsilon = 2        # change threshold in cm
        self.interval = 0.1     # sleep idle time in s
        self.normalize = False  # normalize measured distance?
        self.is_running = True
        self.senders = []
        self.verbose = verbose
        if self.verbose:
            print(f"tfluna: created {dev} {rate}")

    # add a distance sender which implements the following method:
    # send(self, distance, tfluna)
    def add_sender(self, sender):
        self.senders.append(sender)

    # open serial port for reading
    def open(self):
        if not self.serial.is_open:
            self.serial.open()
            if self.verbose:
                print("tfluna: open")

    # close serial port
    def close(self):
        if self.serial.is_open:
            self.serial.close()
            if self.verbose:
                print("tfluna: close")

    # start synchronous run loop
    def start(self):
        self.is_running = True
        if self.verbose:
            print("tfluna: start")
        while self.is_running:
            self.update()
            time.sleep(self.interval)
        self.is_running = False
        if self.verbose:
            print("tfuna: stop")

    # stop synchronous run loop
    def stop(self):
        self.is_running = False

    # read one chunk of data, parse into distance value, and send
    def update(self):
        count = self.serial.in_waiting
        if count > 4:
            recv = self.serial.read(4)
            self.serial.reset_input_buffer()

            # check if input is valid
            if recv[0] == 89 and recv[1] == 89:
                #print(f"{str(recv[0])} {str(recv[1])} {str(recv[2])} {str(recv[3])}")

                # interpret upper two bytes as one 16 bit int
                low = int(recv[2])
                high = int(recv[3])
                distance = clamp_value(low + high * 256, 0, self.max_distance)
            
                # ignore if difference from prev value is too small
                if abs(distance - self.prev_distance) < self.epsilon:
                    return
                self.prev_distance = distance

                # map to normalized range? 0 far to 1 near
                if self.normalize:
                    distance = map_value(distance, 0, self.max_distance, 1, 0)

                # send
                if self.verbose:
                    print(f"tfluna: {distance}")
                for sender in self.senders:
                    sender.send(distance, self)

    # print settings
    def print(self):
        print(f"tfluna: device id {self.devid}")
        print(f"tfluna: max distance {self.max_distance}")
        print(f"tfluna: epsilon {self.epsilon}")
        print(f"tfluna: interval {self.interval}")
        print(f"tfluna: normalize {self.normalize}")
