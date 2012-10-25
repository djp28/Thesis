'''dropBox backend's script to get the replay tags from the original dropBox files.
'''

__author__ = 'Miguel Ojeda'
__copyright__ = 'Copyright 2012, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida', 'Miguel Ojeda', 'Andreas Pfeiffer']
__license__ = 'Unknown'
__maintainer__ = 'Miguel Ojeda'
__email__ = 'mojedasa@cern.ch'


import os
import logging
import tarfile
import json

import replay


def main():
    outputPairs = set([])

    files = replay.getFiles()

    i = 0
    for fileName in files:
        i += 1
        logging.info('[%s/%s] %s: Getting replay tags...', i, len(files), fileName)

        tarFile = tarfile.open(os.path.join(replay.dropBoxReplayFilesFolder, fileName))

        names = tarFile.getnames()
        if len(names) != 2:
            raise Exception('%s: Invalid number of files in tar file.', fileName)

        baseFileName = names[0].rsplit('.', 1)[0]
        dbFileName = '%s.db' % baseFileName
        txtFileName = '%s.txt' % baseFileName
        if set([dbFileName, txtFileName]) != set(names):
            raise Exception('%s: Invalid file names in tar file.', fileName)
        
        destDB = None
        tag = None
        metadata = tarFile.extractfile(txtFileName).readlines()
        for line in metadata:
            if line.startswith('destDB'):
                if destDB is not None:
                    raise Exception('%s: destDB twice.', fileName)
                destDB = line.split('destDB', 1)[1].strip()
            elif line.startswith('tag'):
                if tag is not None:
                    raise Exception('%s: tag twice.', fileName)
                tag = line.split('tag', 1)[1].strip()

        if destDB is None:
            raise Exception('%s: destDB not found.', fileName)
        if tag is None:
            raise Exception('%s: tag not found.', fileName)

        tarFile.close()

        outputPairs.add((destDB, tag))

    with open('outputPairs.json', 'w') as f:
        json.dump(list(outputPairs), f, sort_keys = True, indent = 4)

    outputDict = {}
    for (destDB, tag) in outputPairs:
        outputDict.setdefault(destDB, []).append(tag)

    logging.info('Writing output file...')
    with open('outputDict.json', 'w') as f:
        json.dump(outputDict, f, sort_keys = True, indent = 4)


if __name__ == '__main__':
    main()

