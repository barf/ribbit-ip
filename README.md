About
=====
Ribbit IP COFDM modem and TUN driver for Debian GNU/Linux
Tested on Raspberry Pi400
Created by Stuart MacIntosh ZL3TUX <stuart@macintosh.nz>
Based upon the Ribbit COFDM modem by Ahmet 

Installation
============
Prerequisites:
$ sudo apt install siggen sox ffmpeg python3-alsaaudio python3-zmq python3-scapy

Usage
=====
usage: sudo ./ribbit_ip.py [-h] [-n CALLSIGN] [-j] [-i INTERFACE] [-v VOLUME] 
					[-r RATE] [--cfo CFO] [--verbose] [--username USERNAME] 
					[-p WORKDIR] [--rx-only] [--tx-only]

options:
  -h, --help            show this help message and exit
  -n, --callsign CALLSIGN
                        station callsign (RIBBITIP) up to 9 base 37 style characters
  -j, --jumbo           Enable 5kB Jumbo frames (WIP)
  -i, --interface INTERFACE
                        interface name (tun0)
  -v, --volume VOLUME   audio output volume (0-100)
  -r, --rate RATE       audio input/output sample rate (8000)
  --cfo CFO             Carrier Frequency Offset (CFO) frequency (1600)
  -d, --device DEVICE   ALSA audio device name (hw:CARD=Device,DEV=0)
  --verbose             verbose output
  --username USERNAME   username for tempfile I/O (defaults to current directory owner)
  -p, --workdir WORKDIR
                        working directory (/tmp/ribbit-ip)
  --rx-only             disable TX for testing (monitor mode)
  --tx-only             disable RX for testing (TX only mode)
