# -*- coding: utf-8 -*-
# (c) 2017 Richard Pobering <richard@hiveeyes.org>
# (c) 2017 Andreas Motl <andreas@hiveeyes.org>
import os
import sys
import shlex
import shutil
import subprocess
from docopt import docopt
from tempfile import NamedTemporaryFile
from operator import itemgetter
from colors import color
from scipy import signal
import scipy.io.wavfile as wav
try:
    import matplotlib.pyplot as plt
except:
    pass
import numpy as np


VERSION  = '0.4.0'
APP_NAME = 'audiohealth ' + VERSION

def resample(audiofile):
    tmpfile = NamedTemporaryFile(suffix='.wav', delete=False)

    # Number of channels?
    cmd = ['soxi', '-c', audiofile]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()

    remix_option = ''
    if process.returncode == 0:
        if stdout.strip() == '2':
            remix_option = 'remix 1,2'
    else:
        print("Error while downsampling: Could not determine number of audio channels.")
        print("The command was:")
        print(cmd)
        sys.exit(2)

    command = 'sox "{input}" "{output}" --norm=-3 {remix_option} gain -n sinc 30-3150 rate 6300'.format(input=audiofile, output=tmpfile.name, remix_option=remix_option)
    cmd = shlex.split(command)
    try:
        status = subprocess.check_call(cmd)
        if status == 0:
            return tmpfile.name
    except:
        print("Error while downsampling: Did you install sox?")
        print("The command was:")
        print(command)
        raise

def wav_to_dat(audiofile):
    sampFreq, snd = wav.read(audiofile)

    duration = snd.shape[0] / sampFreq
    print("Duration: {}s".format(duration))

    # Convert sound array to floating point values ranging from -1 to 1
    # http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
    snd = snd / (2.0 ** 15)

    outfile = audiofile + ".dat"
    snd.tofile(outfile, "\n")

    return outfile

def analyze(datfile, analyzer=None, strategy=None):
    strategy = strategy or 'lr-2.0'

    # Run "osbh-audioanalyzer" command
    cmd = [analyzer, datfile, strategy]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print
        print('Error: osbh-audioanalyzer failed!')
        sys.exit(process.returncode)

    states = stdout.decode('utf-8').split('\n')

    # Sanitize
    states = [state.strip() for state in states]
    states = [state for state in states if state]

    return states

def report(states):

    # The audio is chunked into segments of 10 seconds each, see:
    #   - tools/osbh-audioanalyzer/params.h: float windowLength=2; //Window Length in s
    #   - tools/osbh-audioanalyzer/main.cpp: DetectedStates.size()==5
    window_length = 2 * 5

    chronology = []
    aggregated = {}
    current = None
    applied = False
    for i, state in enumerate(states):

        aggregated.setdefault(state, 0)
        aggregated[state] += window_length

        applied = False
        time_begin = i * window_length
        time_end   = time_begin + window_length
        if state == current:
            chronology[-1].update({'time_end': time_end})
        else:
            entry = {'time_begin': time_begin, 'time_end': time_end, 'state': state}
            chronology.append(entry)
            current = state
            applied = True

    # Properly handle the last state
    if chronology and not applied:
        chronology[-1].update({'time_end': time_end})


    print('==================')
    print('Sequence of states')
    print('==================')
    print(', '.join(states))
    print

    print('===================')
    print('Compressed timeline')
    print('===================')
    for i, entry in enumerate(chronology):
        duration = None
        try:
            #duration = chronology[i+1]['time'] - chronology[i]['time']
            duration = entry['time_end'] - entry['time_begin']
        except IndexError:
            pass
        entry['duration'] = duration
        entry['duration_vis'] = None
        if duration:
            entry['duration_vis'] = int(duration / window_length) * "="

        #line = '{time:3}t {state:15} {duration_vis}'.format(**entry)
        line = '{time_begin:3}s - {time_end:3}s   {state:15} {duration_vis}'.format(**entry)
        print(line)
    print

    print('==============')
    print('Total duration')
    print('==============')
    aggregated_sorted = sorted(aggregated.items(), key=itemgetter(1), reverse=True)
    for state, duration in aggregated_sorted:
        duration_vis = int(duration / window_length) * "="
        line = '{duration:10}s   {state:15} {duration_vis}'.format(**locals())
        print(line)
    print

    print('======')
    print('Result')
    print('======')
    print('The most common events (i.e. the events with the highest total duration) are:')
    print

    try:
        winner_state, winner_duration = aggregated_sorted[0]
        print('     The colony is mostly in »{state}« state, which is going on for {duration} seconds.'.format(state=emphasize(winner_state.upper()), duration=emphasize(winner_duration)))
    except:
        pass

    try:
        second_state, second_duration = aggregated_sorted[1]
        print('     Sometimes, the state oscillates to »{state}«, for {duration} seconds in total.'.format(state=emphasize(second_state.upper()), duration=emphasize(second_duration)))
    except:
        pass

    print

    print('==========')
    print('Disclaimer')
    print('==========')
    print('THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. NO LIABILITY FOR ANY DAMAGES WHATSOEVER.')

    print

def emphasize(text):
    return color(text, fg='yellow', style='bold')

def power_spectrum(wavfile):

    fs, x = wav.read(wavfile)

    """
    # https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.signal.spectrogram.html
    f, t, Sxx = signal.spectrogram(x, fs)
    print(f, t, Sxx)
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
    return
    """

    # Compute power spectrum
    # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.welch.html
    f, Pxx_spec = signal.welch(x, fs, 'flattop', 1024, scaling='spectrum')

    # Compute peaks in power spectrum
    #peak_indices = signal.find_peaks_cwt(Pxx_spec, np.arange(3, 15), min_snr=0.1)
    peak_indices = signal.argrelmax(Pxx_spec)
    #peak_indices = signal.argrelextrema(Pxx_spec, np.greater)
    peak_freq  = f[peak_indices]
    peak_power = Pxx_spec[peak_indices]


    # Plot power spectrum and peaks
    #plt.rcParams.update({'font.size': 10})
    plt.rc('xtick', labelsize=10)
    plt.figure()

    plt.xlim((30, 1500))
    #plt.ylim((10**2, 10**4))
    #plt.ylim((10**2, 5000000))
    plt.ylim((0, 2500))

    plt.xticks(range(0, 1501, 100))

    plt.xlabel('frequency [Hz]')
    plt.ylabel('Linear spectrum [V RMS]')

    # Plot power spectrum
    #plt.semilogy(f, np.sqrt(Pxx_spec), 'b')
    plt.plot(f, np.sqrt(Pxx_spec), 'b')

    # Plot peak points as dots
    #plt.semilogy(peak_freq, np.sqrt(peak_power), 'ro')
    plt.plot(peak_freq, np.sqrt(peak_power), 'ro')


    # Aggregate dictionary of peak frequencies mapping to their power
    peak_data = dict(zip(peak_freq, peak_power))

    # Filter < 1500 Hz
    peak_data = {freq: power for freq, power in peak_data.iteritems() if freq <= 1500}

    # Display power spectrum report
    print('==================')
    print('Peaks by frequency')
    print('==================')
    for freq, power in sorted(peak_data.items(), key=itemgetter(0)):
        line = '{freq:15.2f} Hz   {power:15.2f} RMS'.format(**locals())
        print(line)
    print

    print('==============')
    print('Peaks by power')
    print('==============')
    for freq, power in sorted(peak_data.items(), key=itemgetter(1), reverse=True):
        line = '{power:15.2f} RMS   {freq:15.2f} Hz'.format(**locals())
        print(line)
    print

    tmpfile = NamedTemporaryFile(suffix='.png', delete=False)
    plt.savefig(tmpfile.name)
    #plt.show()

    return tmpfile.name


def main():
    """
    Usage:
      audiohealth analyze --audiofile audiofile --analyzer /path/to/osbh-audioanalyzer [--strategy lr-2.0] [--debug] [--keep]
      audiohealth analyze --datfile datfile --analyzer /path/to/osbh-audioanalyzer [--strategy lr-2.0] [--debug]
      audiohealth convert --audiofile audiofile --wavfile wavfile
      audiohealth power   --audiofile audiofile --pngfile pngfile
      audiohealth power   --wavfile wavfile     --pngfile pngfile
      audiohealth --version
      audiohealth (-h | --help)

    Options:
      --wavfile=<wavfile>       Output .wav file for conversion
      --pngfile=<pngfile>       Output .png file of power spectrum
      --audiofile=<audiofile>   Process audiofile. Please use sox-compatible input formats.
      --datfile=<datfile>       Process datfile.
      --analyzer=<analyzer>     Path to OSBH audioanalyzer binary
      --strategy=<strategy>     The classification strategy. One of dt-0.9, dt-1.0, dt-2.0, lr-2.0
      --keep                    Keep (don't delete) downsampled and .dat file
      --debug                   Enable debug messages
      -h --help                 Show this screen

    """

    # Parse command line arguments
    options = docopt(main.__doc__, version=APP_NAME)
    #print('options:', options)


    if options.get('convert'):
        audiofile = options.get('--audiofile')
        wavfile   = options.get('--wavfile')
        tmpfile   = resample(audiofile)
        shutil.move(tmpfile, wavfile)

    if options.get('power'):
        audiofile = options.get('--audiofile')
        wavfile   = options.get('--wavfile')
        pngfile   = options.get('--pngfile')
        if audiofile:
            wavfile   = resample(audiofile)
        tmpfile   = power_spectrum(wavfile)
        if audiofile:
            os.unlink(wavfile)
        shutil.move(tmpfile, pngfile)

    elif options.get('analyze'):

        audiofile = options.get('--audiofile')
        analyzer = options.get('--analyzer')
        strategy = options.get('--strategy')

        if audiofile:
            tmpfile = resample(audiofile)
            datfile = wav_to_dat(tmpfile)

        else:
            datfile = options.get('--datfile')

        states = analyze(datfile, analyzer=analyzer, strategy=strategy)
        report(states)

        # Cleanup
        if not options.get('--keep'):
            if audiofile:
                os.unlink(tmpfile)
                os.unlink(datfile)

if __name__ == '__main__':
    main()
