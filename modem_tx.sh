#!/bin/bash
#
# modem transmit
# Stuart MacIntosh <stuart@macintosh.nz>
#
# https://www.hfunderground.com/wiki/index.php/11_meter
# 	27.255 MHz USB - WSPR weak signal digital modes - also alternate ROS datamode, PSK31 and packet radio channel - CB channel 23 
#
# usage: CALLSIGN="ANONYMOUS" MODE=23 PAYLOAD=message.txt ./modem_tx.sh
#

export XDG_RUNTIME_DIR=/run/user/$UID

SCRIPT_DIR=`pwd`
WORKDIR="/tmp/ribbit-ip"
RATE=8000
BITS=16
CHANNELS=1

if [[ -z "${CFO}" ]]; then
  CFO=1700
else
  CFO="${CFO}"
fi

if [[ -z "${CALLSIGN}" ]]; then
  CALLSIGN="ANONYMOUS"
else
  CALLSIGN="${CALLSIGN}"
fi

if [[ -z "${MODE}" ]]; then
  MODE=23
else
  MODE="${MODE}"
fi

mkdir -p $WORKDIR

# MODE=23 # modem-next # 256b
# MODE=24 # modem-next # 512b
# MODE=25 # modem-next # 1024b
# MODE=26 # 256
# MODE=27 # 512b
# MODE=28 # 1024
# MODE=29 # 512b
# MODE=30 # modem-next # 1024b
# MODE=6 # modem-master

# PAYLOAD=$*
# PAYLOAD=${@: -1}
# PAYLOAD=${BASH_ARGV[0]}
# echo $PAYLOAD
# file $PAYLOAD

if [[ -z "${PAYLOAD}" ]]; then
  PAYLOAD=${@: -1}
else
  PAYLOAD="${PAYLOAD}"
fi

rm -f $WORKDIR/out.wav $WORKDIR/msg.wav $WORKDIR/out_trim.wav $WORKDIR/out_mono.wav

# make unsquelch CFO tone # apt install siggen
TONES="/usr/bin/tones"
# $TONES -vv -c 1 -s $RATE -16 -f -w $CFO.wav sine :333 $CFO
$TONES -c 1 -s $RATE -16 -f -w $WORKDIR/$CFO.wav sine :333 $CFO

# modem-master:
# usage: ./encode OUTPUT RATE BITS CHANNELS OFFSET MODE CALLSIGN INPUT..
# ENCODE=$WORKDIR/modem-master/encode
# $ENCODE $WORKDIR/out.wav $RATE $BITS $CHANNELS $CFO $MODE $CALLSIGN $PAYLOAD

# modem-next:
# ./encode encoded.wav 8000 16 1 1500 23 CALLSIGN uncoded.dat
ENCODE=$SCRIPT_DIR/bin/encode-`uname -m`
$ENCODE $WORKDIR/out.wav $RATE $BITS $CHANNELS $CFO $MODE $CALLSIGN $PAYLOAD

# modem-ribbit:
# ENCODE=$WORKDIR/modem-ribbit/encode
# $ENCODE $WORKDIR/out.wav $PAYLOAD

# assemble and play
ffmpeg -loglevel quiet -y -i $WORKDIR/out.wav -ac 1 $WORKDIR/out_mono.wav
sox $WORKDIR/out_mono.wav $WORKDIR/out_trim.wav silence 1 0.0 0.0% -1 0 1%

# with start and tail
# sox $WORKDIR/1700_start.wav $WORKDIR/out_trim.wav $WORKDIR/1700_end.wav $WORKDIR/msg.wav

# with start
sox $WORKDIR/$CFO.wav $WORKDIR/out_trim.wav $WORKDIR/msg.wav

# normal play
# sox $WORKDIR/out_trim.wav $WORKDIR/msg.wav

#
# morseALSA -w 13 -v 1.0 RIB BIT
#aplay /tmp/msg.wav
mpv --quiet --volume=100 $WORKDIR/msg.wav
