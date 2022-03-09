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

import sys
import signal
import argparse
import luna

##### parser

parser = argparse.ArgumentParser(description='''
Send TF-Luna LIDAR proximity distance measurements over OSC (default) or UDP
and optional "isThere" presence events to a ThingsBoard URL.

Distance format is cm integer or normalized float (inverted, 1 near to 0 far).

Message format: message [id] distance

  Ex. OSC: "/tfluna" distance

  Ex. UDP: "tfluna" distance

The default "tfluna" message can be overridden via --message and an additional
device identifier can be added with --id:

  $ --message /proximity --id 2
  OSC: "/proximity" 2 distance

Optionally, a boolean "isThere" event can be sent to a ThingsBoard URL whenever
someone moves in front or away from the sensor:

  $ --tb-url http://board.mydomain.com/api/v1/TOKEN/telemetry
  TB: {"isThere": 0}

The default "isThere" message name can be overridden via --tb-message:

  $ --tb-url http://board.mydomain.com/api/v1/TOKEN/telemetry \\
    --tb-message proximity
  TB: {"proximity": 0}

''', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "dev", type=str, nargs="?", metavar="DEV",
    default="/dev/ttyAMA0", help="serial port device, default: dev/ttyAMA0")
parser.add_argument(
    "-d", "--destination", dest="destination", metavar="HOST",
    default="127.0.0.1", help="destination hostname or IP address, default: 127.0.0.1")
parser.add_argument(
    "-p", "--port", type=int, dest="port", metavar="PORT",
    default="5005", help="destination port to send to, default: 5005")
parser.add_argument(
    "-i", "--interval", type=float, dest="interval", metavar="INTERVAL",
    default=0.1, help="read interval in seconds, default: 0.1")
parser.add_argument(
    "-e", "--epsilon", type=int, dest="epsilon", metavar="EPSILON",
    default=1, help="min distance change in cm to send a message, default: 2")
parser.add_argument(
    "-m", "--max-distance", type=int, dest="max_distance", metavar="MAX_DISTANCE",
    default=200, help="max allowed distance in cm, rest is clipped")
args = parser.add_argument(
    "-n", "--normalize", action="store_true", dest="normalize",
    help="send normalized values instead of cm: 1 near to 0 far (max distance)")
parser.add_argument(
    "-u", "--udp", action="store_true", dest="udp",
    default=False, help="send raw UDP message instead of OSC")
args = parser.add_argument(
    "--message", type=str, nargs=1, dest="message", metavar="MESSAGE",
    default=None, help="set OSC message address or UDP message text")
args = parser.add_argument(
    "--id", type=int, dest="devid", metavar="DEVID",
    default=None, help="set device identifier to include in message")
args = parser.add_argument(
    "--tb-url", type=str, dest="tb_url", metavar="TB_URL",
    default=None, help="send \"isThere\" bool message to a ThingsBoard url")
args = parser.add_argument(
    "--tb-message", type=str, nargs=1, dest="tb_message", metavar="TB_MESSAGE",
    default="isThere", help="set ThingsBoard \"isThere\" message name")
args = parser.add_argument(
    "-v", "--verbose", action="store_true", dest="verbose",
    help="enable verbose printing")

##### signal

# signal handler for nice exit
def sigint_handler(signum, frame):
    tfluna.stop()

##### main

if __name__ == '__main__':

    # parse
    args = parser.parse_args()

    # sensor
    try:
        tfluna = luna.TFLuna(dev=args.dev, verbose=args.verbose)
    except Exception as e:
        print(e)
        exit(1)
    tfluna.max_distance = args.max_distance
    tfluna.epsilon = args.epsilon
    tfluna.interval = args.interval
    tfluna.normalize = args.normalize
    tfluna.devid = args.devid
    if args.verbose:
        tfluna.print()

    # sender(s)
    if args.udp:
        sender = luna.UDPSender(addr=(args.destination, args.port))
        sender.message = " ".join(args.message) if args.message else "tfluna" 
        tfluna.add_sender(sender)
    else:
        sender = luna.OSCSender(addr=(args.destination, args.port))
        sender.address = " ".join(args.message) if args.message else "/tfluna"
        tfluna.add_sender(sender)
    if args.tb_url:
        sender = luna.TBSender(url=args.tb_url, threading=True)
        sender.message = "".join(args.tb_message)
        sender.verbose = args.verbose
        tfluna.add_sender(sender)
    if args.verbose:
        for sender in tfluna.senders:
            sender.print()

    # start
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        tfluna.open()
        tfluna.start()
    finally:
        tfluna.close()
