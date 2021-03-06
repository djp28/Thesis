'''Script that uses upload.py to upload to the new dropBox.
'''

__author__ = 'Miguel Ojeda'
__copyright__ = 'Copyright 2012, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida', 'Miguel Ojeda', 'Andreas Pfeiffer']
__license__ = 'Unknown'
__maintainer__ = 'Miguel Ojeda'
__email__ = 'mojedasa@cern.ch'


import socket
import subprocess


frontendHost = socket.gethostname()
frontendUrlTemplate = 'https://%s:8095/dropBox/'


class UploadError(Exception):
    def __init__(self, message):
        self.args = (message, )


def upload(fileName, backend):
    '''Uploads a file to the frontend.
    '''

    process = subprocess.Popen('../dropBox/upload.py -b %s -H %s -u %s %s' % (backend, frontendHost, frontendUrlTemplate, fileName), shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    result = process.communicate()
    returnCode = process.returncode

    error = result[1].rsplit('\n', 1)[-2].partition('ERROR: ')[2]

    if len(error) > 0:
        raise UploadError('Upload failed: %s (full msg:\n%s)' % (error, result))
    elif returnCode != 0:
        raise Exception('Error while running the upload script:\n%s' % result[1])

