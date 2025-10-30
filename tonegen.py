#!/usr/bin/env python3
#
# tone / sine wave generator
# creates IEEE 32b float WAV
# by Stuart MacIntosh ZL3TUX <stuart@macintosh.nz>
#

import sys
import argparse
import numpy as np
from scipy.io.wavfile import write as write_wav

def create_wav_tone(filename, frequency, duration, sample_rate, amplitude):
	"""Generates a pure sine wave tone and saves it as a WAV file."""
	sample_rate = int(sample_rate)
	duration = float(duration)
	frequency = float(frequency)
	amplitude = float(amplitude)

	# Generate sine wave samples
	samples = (np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate)).astype(np.float32) * amplitude

	# Save as WAV file
	write_wav(filename, sample_rate, samples)


if __name__=='__main__':
	parser = argparse.ArgumentParser(
				prog=sys.argv[0],
				description='Python Tone Generator by ZL3TUX <stuart@macintosh.nz>',
				epilog='')

	parser.add_argument('frequency', default=1500, type=float, help='frequency (1500 Hz)')
	parser.add_argument('-o', '--output', default='out.f32', help='output WAV file (out.f32)')

	parser.add_argument('-s', '--sample_rate', type=float, default=48000, help='sample rate (48000)')
	parser.add_argument('-d', '--duration', default=1.0, help='duration (1.0)')
	parser.add_argument('-a', '--amplitude', default=0.5, help='signal amplitude (0.5)')
	
	args = parser.parse_args()

	# Example usage: Create a 600 Hz tone WAV file
	# create_wav_tone("tone.wav", 600, 1)
	create_wav_tone(args.output, args.frequency, args.duration, args.sample_rate, args.amplitude)

	print('Frequency:\t%s\nDuration:\t%s\nFilename:\t%s' % (args.frequency, args.duration, args.output))
