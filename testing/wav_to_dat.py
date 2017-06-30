#!/usr/bin/env python
import sys
#import scipy.signal
import scipy.io.wavfile as wav

# https://www.youtube.com/channel/UCuZyNH62qFiR0hpcuOF7eqQ

# download the playlist, extract to audio only
# youtube-dl --yes-playlist -x --audio-format vorbis  https://www.youtube.com/playlist\?list\=PL13A84135EDC8A06A

# Stereo->Mono remixing, bandpass and downsampling
# https://stackoverflow.com/questions/6882125/reducing-removing-clipping-in-sox-when-converting-the-sample-rate
# sox beehive_swarming_15_to_25.ogg beehive_swarming_15_to_25_compressed.wav remix 1,2 gain -n sinc 1-2250 rate 6300

# Trimming (optional)
# sox beehive_swarming_15_to_25_bandpass_mono.wav beehive_swarming_15_to_25_p_0.wav trim 0 120
# sox beehive_swarming_15_to_25_bandpass_mono.wav beehive_swarming_15_to_25_p_120.wav trim 120 120
# sox beehive_swarming_15_to_25_bandpass_mono.wav beehive_swarming_15_to_25_p_240.wav trim 240 120
# sox beehive_swarming_15_to_25_bandpass_mono.wav beehive_swarming_15_to_25_p_360.wav trim 360 120
# sox beehive_swarming_15_to_25_bandpass_mono.wav beehive_swarming_15_to_25_p_480.wav trim 480

# Convert to .dat file
# python wav_to_dat.py beehive_swarming_5_to_5_bandpass_mono.wav

# Run beehive health state detection
# ./test beehive_swarming_5_to_5_bandpass_mono.wav.fft.dat

def convert(filename):
    sampFreq, snd = wav.read(filename)
    #print 'snd:', snd

    print 'sampFreq:', sampFreq
    #print dir(snd)
    #print snd.nbytes

    print 'dtype:', snd.dtype
    print 'shape:', snd.shape
    print 'size:', snd.size
    duration = snd.shape[0] / sampFreq
    print 'duration:', duration

    if snd.ndim == 1:
        print 'mono'
    else:
        print 'stereo: will select channel 1'
        snd = snd.T[0]

    #print snd


    # Downsampling
    # https://stackoverflow.com/questions/37120969/how-can-we-use-scipy-signal-resample-to-downsample-the-speech-signal-from-44100
    """
    secs = len(snd) / sampFreq # Number of seconds in signal X
    samps = secs * 6300     # Number of samples to downsample
    snd = scipy.signal.resample(snd, samps)
    """

    # Convert sound array to floating point values ranging from -1 to 1
    # http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
    snd = snd / (2.0 ** 15)

    """
    chunksize = 130
    if duration > chunksize:

        interval = chunksize * sampFreq

        print len(snd)
        steps = range(0, snd.size, interval)
        print 'steps:', steps
        for step in steps:
            part = snd[step:step+interval]
            print 'len:' + str(len(part))
    """

    #print snd
    outfile = filename + ".fft.dat"
    snd.tofile(outfile, "\n")
    print('Success:', outfile)

if __name__ == '__main__':
    filename = sys.argv[1]
    convert(filename)
