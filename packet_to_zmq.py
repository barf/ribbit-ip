#!/usr/bin/env python3
#
# send packet from file/fifo to zmq tun driver
# Stuart MacIntosh <stuart@macintosh.nz>
#

import os
import zmq
import sys
# from IPython import embed
# from scapy.all import *
from scapy.layers.inet import IP, ICMP
from scapy.layers.inet6 import IPv6, IPv46

try:
	WORKDIR = os.environ['WORKDIR']
except:
	WORKDIR = '/tmp/ribbit-ip'

context = zmq.Context()

# def ip_version(packet):
# 	print(type(packet))
# 	print(type(IP))
# 	if IP in packet:
# 		return 4
# 	elif IPv6 in packet:
# 		return 6
# 	else:
# 		return -1

# scapy.layers.inet6.IPv46

def ip_version(packet):
	try:
		v4 = IP(packet)
		if v4.len > 1024 or v4.len == 0:
			# probably v6?
			raise
		return 4
	except:
		try:
			v6 = IPv6(packet)
			return 6
		except:
			return -1


#  Socket to talk to server
print("Connecting to ribbit modem server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5555")

try:
	fp = open(sys.argv[1], 'rb')
except IndexError:
	print('Usage: %s <packet.dat>' % sys.argv[0])
	sys.exit(1)
except:
	sys.exit(1)

message = fp.read()
fp.close()

v = ip_version(message)
# print('ip version: %s' % v)
# prune to len from IP header
if v==4:
	i = IP(message)
	print("sending packet IP.len: %s" % i.len)
	# embed()
	out = message[:i.len]
elif v==6:
	i=IPv6(message)
	print("sending packet IPv6.plen: %s" % (i.plen+40))
	# embed()
	out = message[:i.plen+40]
else:
	print("sending packet, untrimmed")
	# embed()
	out = message

socket.send(out)
reply = socket.recv_string()
print(reply)
socket.close()
sys.exit(0)