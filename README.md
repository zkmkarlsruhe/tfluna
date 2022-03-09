tfluna
======

![tfluna icon](media/icon.png)

Forward TF-Luna LIDAR sensor events over OSC, UDP, or Thingsboard.

This code base has been developed by [ZKM | Hertz-Lab](https://zkm.de/en/about-the-zkm/organization/hertz-lab) as part of the project [»The Intelligent Museum«](#the-intelligent-museum). 

Copyright (c) 2022 ZKM | Karlsruhe.
Copyright (c) 2022 Dan Wilcox.
Copyright (c) 2020 Daniel Heiss <heiss@zkm.de>
Copyright (c) 2020 Marc Schütze <mschuetze@zkm.de>

BSD Simplified License.

Description
-----------

This script sends TF-Luna 1D ToF (Time of Flight) LIDAR sensor proximity distance measurements over OSC (default) or UDP
and optional "isThere" presence events to a [ThingsBoard URL](https://thingsboard.io).

The distance measurement format is an integer in cm (default) or a normalized float (inverted, 1 near to 0 far).

Dependencies
------------

* Python 3
* [pyserial library](https://github.com/pyserial/pyserial/)
* [python-osc library](https://github.com/attwad/python-osc)
* [requests library](https://github.com/psf/requests)

Setup
-----

Install Python 3, if not already available. For instance, on macOS using [Homebrew](http://brew.sh):

```shell
brew install python3
```

Create a virtual environment and install the script's dependencies:

```shell
make
```

### Enable Raspberry Pi serial port for TF-Luna

The TF-Luna can be read over one of the built-in serial ports connected to the GPIO pins. Older boards (RPi 3) can use UART 1 or 2 while newer boards (RPi 4+) have additional UARTs available.

https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts

![pi tfluna wiring diagram](media/pi%20tfluna%20wiring%20diagram.png)

_Note: RX/TX wires may be different colors._

#### UART 1

RPi 3 or RPi 4

GPIO pin connections
* GPIO 14: sensor TX
* GPIO 15: sensor RX
* 5V+: sensor 5V (red)
* GND: sensor GND (black)

This serial port is used for bluetooth by default. Disable this service and ensure the mini UART uses UART 0 by adding the following to `/boot/config.txt`:

~~~
dtoverlay=pi3-disable-bt,pi3-miniuart-bt
~~~

Then reboot:

~~~
sudo reboot
~~~

The serial port should now be available as `/dev/ttyAMA0`.

If the port cannot be read (permissions issues), try the following [suggested on Stack Exchange](https://raspberrypi.stackexchange.com/a/48258 ):

1. Remove anything that looks like `console=serial0,115200
, console=tty1` in `/boot/cmdline.txt` file
2. Disable the default tty and give the user access to the `dialout` group
~~~
sudo systemctl mask serial-getty@ttyAMA0.service
sudo adduser $USER dialout
~~~
3. Reboot
~~~
sudo reboot
~~~

#### UART 3

RPi 4+

GPIO pin connections
* GPIO 4: sensor TX
* GPIO 5: sensor RX
* 5V+: sensor 5V (red)
* GND: sensor GND (black)

This UART is disabled by default. Enable it by adding the following to `/boot/config.txt`

~~~
dtoverlay=uart3
~~~

Then reboot:

~~~
sudo reboot
~~~

The serial port should now be available as `/dev/ttyAMA1`.

### USB to TTL dongle

Some versions of the TF-Luna come with an included "USB to TTL" dongle which is essentially a USB serial port adapter with bare pins for the sensor. 

On macOS, once the adapter is plugged in, it's serial port should be available at some variation of `/dev/tty.usbserial-*` such as `/dev/tty.usbserial-410` or `/dev/tty.usbserial-510`.

Running
-------

Start reading the sensor at serial port `DEV` on the commandline via the virtual environment wrapper script:

    ./tfluna DEV

For example:

    ./tfluna /dev/ttyAMA1

It can simply sit in the background and send events over a networking connection. To configure the send address and ports as well as various other options, see the commandline argument help for tfluna by running:

    ./tfluna -h

Defaults are:

* OSC to 127.0.0.1 on port 5005
* message format: `/tfluna distance`
* distance format: centimeters
* max distance: 200 cm

Messages are sent over UDP either formatted as OSC messages (default) or raw UDP packets by using the `--udp` option. The message name is `tfluna` by default but can be overridden by using the `--message` option:

Multiple instances can be run at the same time by providing a different serial port DEV argument. Additionally, an optional device identifier can be added to the message to differentiate between instances via the `--id` option. 

~~~
Message format: message [id] distance

  Ex. OSC: "/tfluna" distance

  Ex. UDP: "tfluna" distance
~~~

Distance measurements can be sent in a normalized format by using the `--normalize` option which uses an inverted range of 1 near and 0 far to the max distance which can also be specified in cm with the `--max-distance` option.

Optionally, a boolean "isThere" event can be sent to a ThingsBoard URL whenever
someone moves in front or away from the sensor:

~~~
$ --tb-url http://board.mydomain.com/api/v1/TOKEN/telemetry
TB: {"isThere": 0}
~~~

The default "isThere" message name can be overridden via --tb-message:

~~~
$ --tb-url http://board.mydomain.com/api/v1/TOKEN/telemetry \\
--tb-message proximity
TB: {"proximity": 0}
~~~

Test Client
-----------

A simple test client is provided which receives UDP messages on the default 127.0.0.1 address and port 5005 and prints their contents to the console.

To use, start the client:

    ./tests/udpreceive.py

Next, start tfluna in another shell:

    ./tfluna --udp

_Note: This client can also receive and print OSC messages, however the message content is printed in it's raw byte format._

The Intelligent Museum
----------------------

An artistic-curatorial field of experimentation for deep learning and visitor participation

The [ZKM | Center for Art and Media](https://zkm.de/en) and the [Deutsches Museum Nuremberg](https://www.deutsches-museum.de/en/nuernberg/information/) cooperate with the goal of implementing an AI-supported exhibition. Together with researchers and international artists, new AI-based works of art will be realized during the next four years (2020-2023).  They will be embedded in the AI-supported exhibition in both houses. The Project „The Intelligent Museum” is funded by the Digital Culture Programme of the [Kulturstiftung des Bundes](https://www.kulturstiftung-des-bundes.de/en) (German Federal Cultural Foundation) and funded by the [Beauftragte der Bundesregierung für Kultur und Medien](https://www.bundesregierung.de/breg-de/bundesregierung/staatsministerin-fuer-kultur-und-medien) (Federal Government Commissioner for Culture and the Media).

As part of the project, digital curating will be critically examined using various approaches of digital art. Experimenting with new digital aesthetics and forms of expression enables new museum experiences and thus new ways of museum communication and visitor participation. The museum is transformed to a place of experience and critical exchange.

![Logo](media/Logo_ZKM_DMN_KSB.png)
