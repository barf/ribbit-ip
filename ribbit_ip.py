#!/usr/bin/env python3
#
# Ribbit-IP TUN driver by Stuart MacIntosh ZL3TUX <stuart@macintosh.nz>
# built upon the Ribbit COFDM modem by Ahmet: https://github.com/aicodix/modem
#
# Installation:
# some basic Linux programs are required:
#	mpv
#	sox
#	su
#	runuser
#
# required Python modules:
#	alsaaudio
#	tuntap
#	scapy
#	zmq
#
# special prerequisites. the ribbit modem executables:
#	modem-next
#	modem-master (TODO, for the other frame types)
#

#
# Usage: run (as root, or use setcap etc to grant TUN driver permissions):
#
#	./ribbit_ip.py
#

import alsaaudio
import binascii
import threading
import argparse
import tempfile
import sys
import os
import subprocess
import time
import wave

import zmq
# note 'socket' is used later for zmq, not the socket module

from tuntap import TunTap
from scapy.layers.inet import IP, ICMP
from scapy.layers.inet6 import IPv6, IPv46

# B=count=1 byte
# MODE=6  # modem-master 	# 5380B # 43040b
# MODE=23 # modem-next 		# 256B
# MODE=24 # modem-next 		# 512B
# MODE=25 # modem-next 		# 1024B
# MODE=26 # 256
# MODE=27 # 512
# MODE=28 # 1024
# MODE=29 # 512
# MODE=30 # 1024

#
# transmitter
# 
class Transmitter:
	# TODO: def init, move the modem_tx.sh stuff here
	def __init__(self, freq, mode):
		self.running=True
		self.tx_frequency = freq
		self.tx_mode = mode

	def loop(self):
		print('Transmitter thread...')
		while self.running==True:
			try:
				n = tun.read()
			except BlockingIOError:
				tx_running=False
				rx_running=False
				sys.exit(1)
			print('len: %s' % len(n))

			PAYLOAD_fp, PAYLOAD_fn = tempfile.mkstemp()
			PAYLOAD_fp = open(PAYLOAD_fn, 'wb')
			PAYLOAD_fp.write(n)
			PAYLOAD_fp.close()
			os.chmod(PAYLOAD_fn, 0o755)

			WAVOUT_fp, WAVOUT_fn = tempfile.mkstemp()
			os.chmod(WAVOUT_fn, 0o755)
			os.chown(WAVOUT_fn, UID, GID)

			if len(n) <=256:
				# print('sending 256 byte frame')
				MODE=23

			if len(n) > 256:
				# print('sending 512 byte frame')
				MODE=24

			if len(n) > 512:
				# print('sending 1024 byte frame')
				MODE=25

			if len(n) > 1024:
				# TODO
				# send jumbo frame with count=5380 bytes
				# or if not, ICMP packet too big error goes here:
				# scapy.layers.inet6.ICMPv6PacketTooBig(_pkt, /, *, type=2, code=0, cksum=None, mtu=1024)
				# print('sending 5380 byte frame')
				MODE=6
				# $ENCODE out.wav $RATE $BITS $CHANNELS $CFO $MODE $CALLSIGN $PAYLOAD
				env_encode = { **os.environ, 'CALLSIGN': args.callsign, 'MODE': str(MODE), 'CFO': str(args.cfo), 'PAYLOAD': PAYLOAD_fn, 'WAVOUT': WAVOUT_fn }
				cmd_encode = ['/usr/bin/su', args.username, '-c', cmd_encode_master, WAVOUT_fn, str(args.rate), str(args.bits), str(args.channels), str(args.cfo), str(MODE), str(args.callsign), PAYLOAD_fn]
				# print(env_encode)
				print(cmd_encode)
				proc_encode = subprocess.run(cmd_encode, env=env_encode)
				# stdout, stderr = proc_encode.communicate()
				# exit_code = proc_encode.wait()

				# play audio with mpv 
				# TODO: play the wav in python like https://github.com/larsimmisch/pyalsaaudio/blob/main/playwav.py
				cmd_mpv = ['/usr/bin/su', args.username, '-c', 'mpv', '--quiet', '--volume=100', WAVOUT_fn]
				# print(cmd_mpv)
				proc_mpv = subprocess.run(cmd_mpv, env=env_encode, capture_output=True)
				# stdout, stderr = proc_mpv.communicate()
				# exit_code = proc_mpv.wait()
			else:
				env_encode = { **os.environ, 'CALLSIGN': args.callsign, 'MODE': str(MODE), 'CFO': str(args.cfo), 'PAYLOAD': PAYLOAD_fn }
				cmd_encode = ['/usr/bin/su', args.username, '-c', SCRIPT_DIR + os.sep + 'modem_tx.sh']
				# print(env_encode)
				print(cmd_encode)
				proc_encode = subprocess.run(cmd_encode, env=env_encode, capture_output=True)
				# stdout, stderr = proc_encode.communicate()
				# exit_code = proc_encode.wait()

			# transmit packet (model)
			# my_env = { **os.environ, 'CALLSIGN': args.callsign, 'MODE': str(MODE), 'CFO': str(args.cfo), 'PAYLOAD': PAYLOAD_fn }
			# my_cmd = ['/usr/bin/su', args.username, '-c', 'modem_tx.sh']
			# print(my_env)
			# print(my_cmd)
			# subprocess.run(my_cmd, env=my_env)

			sent = 'sent %s %s MODE=%s\tLEN=%s\tpayload: %s' % (PAYLOAD_fn, IPv46(n), MODE, len(n), binascii.hexlify(n).decode('ascii'))
			print(sent)

			# os.remove(fn)
			os.remove(PAYLOAD_fn)
			os.remove(WAVOUT_fn)

#
# receiver
#
class Receiver:
	# TODO: def init and run the modem_rx.sh script, or move it here
	def __init__(self, freq, mode):
		self.running = True
		self.rx_frequency = freq
		self.rx_mode = mode

	def loop(self):
		print('Receiver thread...')

		# IDEA: open FIFO for receiver instead of zmq
		# TODO: stream sound in python and pipe to decode
		# TODO: like a pythonic "arecord -c 1 -f S16_LE -r $RATE - | $DECODE - $OUT"

		# alsa_in = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
		# 	channels=args.channels, rate=args.rate, format=alsaaudio.PCM_FORMAT_S16_LE,
		# 	periodsize=160, device=args.device)

		# while self.running == True:
		# 	PAYLOAD_fp, PAYLOAD_fn = tempfile.mkstemp()

		# 	os.chmod(PAYLOAD_fn, 0o755)
		# 	os.chown(PAYLOAD_fn, UID, GID)
			
		# 	# env_decode = { **os.environ, 'CALLSIGN': args.callsign } # callsign not needed for decode
		# 	cmd_decode = ['/sbin/runuser', '-u', args.username, cmd_decode_next, '-', PAYLOAD_fn]
		# 	env_decode = os.environ
		# 	# print(cmd_decode)
		# 	proc_decode = subprocess.Popen(cmd_decode, env=env_decode, cwd=args.workdir, 
		# 		shell=False, 
		# 		stdin=subprocess.PIPE, 
		# 		stdout=subprocess.PIPE)
		# 	if args.verbose: print('decode subprocess PID: %s' % proc_decode.pid)

		# 	wf = wave.open(proc_decode.stdin, 'wb')
		# 	wf.setnchannels(args.channels)
		# 	wf.setsampwidth(int(args.bits/8))
		# 	wf.setframerate(args.rate)
		# 	wf.setnframes(0)
		# 	if args.verbose: print(wf)

		# 	read_loop = True
		# 	while read_loop == True:
		# 		# read ALSA input
		# 		l, alsa_data = alsa_in.read() # .read() blocks in PCM_NORMAL mode, returns (0,'') in PCM_NONBLOCK

		# 		if l < 0:
		# 			print("Capture buffer overrun!")
		# 		elif l == 0:
		# 			print('empty PCM buffer (OK in PCM_NONBLOCK mode)')
		# 		else:
		# 			# write alsa_data to decode process stdin:
		# 			# stdout, stderr = proc_decode.communicate(alsa_data) # communicate() is blocking until exit?
		# 			# proc_decode.stdin.write(alsa_data) # works kinda?
		# 			# wf.writeframes(alsa_data) # illegal seek
		# 			# wf.setnframes(n_audio_frame)
		# 			wf.writeframesraw(alsa_data) # illegal seek?

		# 	# block until clean exit from decode subprocess
		# 	exit_code = proc_decode.wait()

		# 	fp = open(PAYLOAD_fn, 'rb')
		# 	message = fp.read()
		# 	fp.close()
		# 	tun.write(message)

		# # close any files/objs?
		# alsa_in.close()	

		# zmq shell script
		env_decode = { **os.environ, 'CALLSIGN': args.callsign }
		cmd_decode = ['/usr/bin/su', args.username, '-c', SCRIPT_DIR + os.sep + 'modem_rx.sh']
		proc_decode = subprocess.Popen(cmd_decode, env=env_decode, cwd=SCRIPT_DIR, 
				shell=False,
				stdin=subprocess.PIPE, 
				stdout=subprocess.PIPE)
		print('PID: %s' % proc_decode.pid)

		while self.running==True:
			# pop packet off zmqueue
			print('ZMQ receiver ready')
			message = socket.recv()
			s = "Received: %s" % binascii.hexlify(message).decode('ascii')
			print(s)
			tun.write(message)
			socket.send_string(s) # return result to zmq script
			# proc_decode.poll()
			
			# o = proc_decode.stdout.read()
			# print(o)

		proc_decode.wait()

if __name__=='__main__':
	parser = argparse.ArgumentParser(
					prog=sys.argv[0],
					description='Ribbit IP TUN adaptor for Linux',
					epilog='')

	# parser.add_argument('frequency', default=27385000, help='receive frequency (27835kHz)')           # positional argument
	parser.add_argument('-f', '--frequency', default=27385000, help='receive frequency (27835kHz)')
	parser.add_argument('-m', '--mode', default='USB', help='receive mode (USB)')
	parser.add_argument('-n', '--callsign', default='RIBBITIP', help='station callsign (RIBBITIP) up to 9 base 37 style characters')
	parser.add_argument('-j', '--jumbo', action='store_true', default=False, help='Enable 5kB Jumbo frames (WIP)')
	parser.add_argument('-i', '--interface', default='tun0', help='interface name (tun0)')
	parser.add_argument('-o', '--output_dir', default='out', help='save received packets to directory (out/)')
	parser.add_argument('-v', '--volume', default=100, help='audio output volume (0-100)')
	parser.add_argument('-b', '--bits', default=16, help='audio input/output bits/sample (8,16)')
	parser.add_argument('-c', '--channels', default=1, help='audio input/output channels (1-2)')
	parser.add_argument('-r', '--rate', default=8000, help='audio input/output sample rate (8000)')
	parser.add_argument('--cfo', default=1600, help='Carrier Frequency Offset (CFO) frequency (1600)')
	parser.add_argument('-d', '--device', default='hw:CARD=Device,DEV=0', help='ALSA audio device name (hw:CARD=Device,DEV=0)')
	parser.add_argument('--verbose', action='store_true', default=False, help='verbose output')
	parser.add_argument('--username', default=os.getlogin(), help='username for tempfile I/O (defaults to workdir owner)')
	parser.add_argument('-p', '--workdir', default=os.getcwd(), help='working directory (defaults to current directory)')

	parser.add_argument('--debug', action='store_true', default=False, help='drop to IPython shell when certain stuff happens (requires IPython)')
	parser.add_argument('--rx-only', action='store_true', default=False, help='disable TX for testing (monitor mode)')
	parser.add_argument('--tx-only', action='store_true', default=False, help='disable RX for testing (TX only mode)')

	args = parser.parse_args()
	if args.debug:
		from IPython import embed
		print('debug mode: IPython embed() breakpoints enabled')
		
	wd = os.stat(args.workdir)
	UID=wd.st_uid
	GID=wd.st_gid
	SCRIPT_DIR=os.getcwd()
	os.environ['SCRIPT_DIR'] = SCRIPT_DIR

	# TODO: actually check prerequisites installed:
	# - mpv
	# - sox
	# - siggen
	# - modem-next
	# - modem-master

	# global tun
	tun = TunTap(nic_type="Tun", nic_name=args.interface)
	tun.config(ip="0.0.0.0", mask="255.255.255.255") # default to no ipv4 address, v6 only
	# subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.disable_ipv6=1' % tun.name]) # TODO: v4 or v6 mode switch
	subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.router_solicitation_delay=15' % tun.name])
	subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.router_solicitation_interval=15' % tun.name])
	subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.accept_ra_mtu=0' % tun.name])

	# subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.autoconf=0' % tun.name])
	# subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.accept_dad=0' % tun.name])
	# subprocess.Popen(['/usr/sbin/sysctl', '-w', 'net.ipv6.conf.%s.accept_ra=0' % tun.name])

	print('TUN driver installed')
	if args.verbose: print(tun.name, tun.ip, tun.mask)

	# global context, socket
	context = zmq.Context()
	# context = zmq.Context.instance() # for when in thread/class?
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:5555")
	print('ZMQ socket ready')

	threads = []

	if not args.tx_only:
		rx = Receiver(args.frequency, args.mode)
		rx_thread = threading.Thread(target=rx.loop)
		threads.append(rx_thread)

	if not args.rx_only:
		tx = Transmitter(args.frequency, args.mode)
		tx_thread = threading.Thread(target=tx.loop)
		threads.append(tx_thread)

	# Start each thread
	for t in threads:
		t.start()

	# Wait for all threads to finish
	for t in threads:
		t.join()

	# embed()
	try:
		tun.close()
		socket.close()
	except:
		print('unclean exit')
		sys.exit(100)
	
	sys.exit(0)