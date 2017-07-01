# -*- coding: utf-8 -*-
# (c) 2017 Richard Pobering <richard@hiveeyes.org>
# (c) 2017 Andreas Motl <andreas@hiveeyes.org>
import os
import sys
import shlex
import subprocess
from docopt import docopt
from tempfile import NamedTemporaryFile
from operator import itemgetter
from colors import color
import scipy.io.wavfile as wav


VERSION  = '0.3.0'
APP_NAME = 'audiohealth ' + VERSION

def resample(audiofile):
    tmpfile = NamedTemporaryFile(suffix='.wav', delete=False)
    command = 'sox "{input}" "{output}" remix 1,2 gain -n sinc 30-3150 rate 6300'.format(input=audiofile, output=tmpfile.name)
    #print(command)
    cmd = shlex.split(command)
    #print('cmd:', cmd)
    status = subprocess.check_call(cmd)
    #print('status:', status)
    #tmpfile.close()
    if status == 0:
      return tmpfile.name

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

    # Run command
    cmd = [analyzer, datfile, strategy]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
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
    if not applied:
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

def main():
    """
    Usage:
      audiohealth --audiofile audiofile --analyzer /path/to/osbh-audioanalyzer [--strategy lr-2.0] [--debug] [--keep]
      audiohealth --datfile datfile --analyzer /path/to/osbh-audioanalyzer [--strategy lr-2.0] [--debug]
      audiohealth --version
      audiohealth (-h | --help)

    Options:
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
    #print options

    audiofile = options.get('--audiofile')
    analyzer = options.get('--analyzer')
    strategy = options.get('--strategy')
    #print inputfile

    if audiofile:
        tmpfile = resample(audiofile)
        if not tmpfile:
            print("Error whild downsampling: Did you install sox?")
            sys.exit(2)

        datfile = wav_to_dat(tmpfile)

    else:
        datfile = options.get('--datfile')

    #print(datfile)
    states = analyze(datfile, analyzer=analyzer, strategy=strategy)
    report(states)

    # Cleanup
    if not options.get('--keep'):
        if audiofile:
            os.unlink(tmpfile)
            os.unlink(datfile)
