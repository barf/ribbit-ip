#!/bin/bash
#
# Ribbit-IP modem receiver loop
# Stuart MacIntosh ZL3TUX <stuart@macintosh.nz>
#

RATE=8000
SCRIPT_DIR=`pwd`
# modem-next: 256 - 1024 bytes only
# usage: ./decode INPUT OUTPUT..
DECODE=$SCRIPT_DIR/bin/decode-`uname -m`

# modem-master: sends 5380 bytes
# usage: modem-master/decode OUTPUT INPUT [SKIP]
# dd if=/dev/urandom of=uncoded.dat bs=1 count=5380
# DECODE=modem-master/decode

# modem-ribbit
# DECODE=modem-ribbit/decode

# modem-short: rattlegram mode
# DECODE=modem-short/decode

WORKDIR="/tmp/ribbit-ip"
mkdir -p $WORKDIR
cd $WORKDIR

killall arecord
sleep 2
while true
do
	echo "ALSA receiver loop entry"
	OUT=$WORKDIR/`date +%s`.dat
	# arecord -c 1 -f S16_LE -r 8000 - | $DECODE - -
	arecord -D hw:2,0 -c 1 -f S16_LE -r $RATE - | $DECODE - $OUT
	hexdump -C $OUT
	# push packet to zmq/tun driver
	$SCRIPT_DIR/packet_to_zmq.py $OUT &
	echo 'packet sent to ZMQ'
done
