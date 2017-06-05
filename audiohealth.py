import shlex
import subprocess
from docopt import docopt
from tempfile import NamedTemporaryFile

VERSION  = '0.1.0'
APP_NAME = 'audiohealth ' + VERSION

def preprocess(audiofile):
    tmpfile = NamedTemporaryFile(suffix='.wav')
    command = 'sox {input} {output} remix 1,2 gain -n sinc 1-2250 rate 6300'.format(input=audiofile, output=tmpfile.name)
    print 'command:', command
    cmd = shlex.split(command)
    print 'cmd:', cmd
    status = subprocess.check_call(cmd)
    print 'status:', status
    tmpfile.close()


def main():
    """
    Usage:
      audiohealth --file audiofile [--debug]
      audiohealth --version
      audiohealth (-h | --help)

    Options:
      --file=<audiofile>        Process audiofile. Please use sox-compatible input formats.
      --debug                   Enable debug messages
      -h --help                 Show this screen

    """

    # Parse command line arguments
    options = docopt(main.__doc__, version=APP_NAME)
    #print options

    inputfile = options.get('--file')
    #print inputfile

    preprocess(inputfile)
