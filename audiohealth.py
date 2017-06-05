import sys
import shlex
import subprocess
from docopt import docopt
from tempfile import NamedTemporaryFile
import scipy.io.wavfile as wav


VERSION  = '0.1.0'
APP_NAME = 'audiohealth ' + VERSION

def resample(audiofile):
    tmpfile = NamedTemporaryFile(suffix='.wav', delete=False)
    command = 'sox "{input}" "{output}" remix 1,2 gain -n sinc 1-2250 rate 6300'.format(input=audiofile, output=tmpfile.name)
    print(command)
    cmd = shlex.split(command)
    print('cmd:', cmd)
    status = subprocess.check_call(cmd)
    print('status:', status)
    #tmpfile.close()
    if status == 0:
      return tmpfile.name

def wav_to_dat(audiofile):
    sampFreq, snd = wav.read(audiofile)

    duration = snd.shape[0] / sampFreq
    print("Duration:", duration)

    # Convert sound array to floating point values ranging from -1 to 1
    # http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
    snd = snd / (2.0 ** 15)

    outfile = audiofile + ".dat"
    snd.tofile(outfile, "\n")

    return outfile
 
def analyze(datfile, analyzer=None):
    #program = 
    #print(sys.argv[0])
    cmd = [analyzer, datfile]
    print(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout)
    states = stdout.decode('utf-8').split('\n')
    #print(states)
    return states

def report(states):
    # see tools/osbh-audioanalyzer/params.h and main.cpp: DetectedStates.size()==5
    window_length = 2 * 5
    chronology = []
    aggregated = {}
    current = None
    for i, state in enumerate(states):
        state = state.strip()
        if not state: continue

        aggregated.setdefault(state, 0)
        aggregated[state] += window_length

        if state != current:
            time = (i + 1) * window_length
            entry = {'time': time, 'state': state}
            #line = '{time}s {state}'.format(time=time, state=state)
            #print(line)
            chronology.append(entry)
            current = state

    for i, entry in enumerate(chronology):
        duration = None
        try:
            duration = chronology[i+1]['time'] - chronology[i]['time']
        except IndexError:
            pass
        entry['duration'] = duration
        entry['duration_vis'] = None
        if duration:
            entry['duration_vis'] = int(duration / window_length) * "="
        line = '{time:3}s {state:15} {duration_vis}'.format(**entry)
        print(line)

    print(aggregated)


def main():
    """
    Usage:
      audiohealth --file audiofile --analyzer /path/to/osbh-audioanalyzer [--debug]
      audiohealth --version
      audiohealth (-h | --help)

    Options:
      --file=<audiofile>        Process audiofile. Please use sox-compatible input formats.
      --analyzer=<analyzer>     Path to OSBH audioanalyzer binary
      --debug                   Enable debug messages
      -h --help                 Show this screen

    """

    # Parse command line arguments
    options = docopt(main.__doc__, version=APP_NAME)
    #print options

    inputfile = options.get('--file')
    analyzer = options.get('--analyzer')
    #print inputfile

    tmpfile = resample(inputfile)
    if tmpfile:
        datfile = wav_to_dat(tmpfile)
        print(datfile)
        states = analyze(datfile, analyzer=analyzer)
        report(states)

