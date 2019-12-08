#!/usr/bin/python3
'''
Applies a specific logtool analyzer to all the sim logs in a tournament,
using TournamentGameIterator.csvIterator to pull in the game logs.
'''

import TournamentGameIterator as ti
import string, re, os, subprocess, sys
from pathlib import Path
processEnv = {'JAVA_HOME': os.environ.get('JAVA_HOME'),
              'Path' : os.environ.get('PATH') }


def extractData (statefileName, gameId, extractorClass,
                 dataPrefix, extractorOptions,
                 logtoolDir, dataDir='data', force=False):
    '''
    Extracts data from individual game state log, using the specified
    logtool extractor class with the specified options, and leaving the
    result in dataDir/dataPrefix-gameId.csv relative to the logtool used.
    Requires working Java 8 and maven installations.
    '''
    #print("Processing ", statefileName)
    datafileName = dataPrefix + gameId + '.csv'
    dataPath = Path(logtoolDir, dataDir, datafileName)
    if force and dataPath.exists():
        dataPath.unlink()
    if not dataPath.exists():
        args = ''.join([extractorClass,' ',
                        extractorOptions, ' ',
                        statefileName, ' ',
                        dataDir + "/" + datafileName])
        args = args.replace("\\","/")
        #print(args)
        if os.name == 'nt':
            print(subprocess.check_output(['mvn', 'exec:exec',
                                 '-Dexec.args=' + args],
                                 shell = True,
                                env = processEnv,
                                cwd = logtoolDir))
        elif os.name == 'posix':
            try:
                subprocess.check_output(['mvn exec:exec -Dexec.args=\"' + args + '\"'],
                                    shell=True,
                                    env = processEnv,
                                    cwd = logtoolDir)
            except subprocess.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    return {'gameId': gameId, 'path': str(dataPath)}


def dataFileIter (tournamentCsvUrl, tournamentDir, extractorClass, dataPrefix,
                  extractorOptions='', logtype='sim',
                  logtoolDir = "../logtool-examples/",
                  force=False):
    '''
    Iterates through sim logs found in tournamentDir, running the specified
    data extractor. If force is False (the default), then the extractor will be
    run only on games for which no data output file already exists.
    '''
    return (extractData(log[logtype], log['gameId'],
                        extractorClass, dataPrefix,
                        extractorOptions, logtoolDir,
                        dataDir = tournamentDir + '/data', force=force)
            for log in ti.csvIter(tournamentCsvUrl, tournamentDir))


def iterate (url, tournamentDir, extractorClass, dataPrefix, options, force=False):
    for data in list(dataFileIter(url, tournamentDir,
                             extractorClass, dataPrefix,
                             options, force=force))[0]:
        print(data)
    

def main ():
    '''
    Command-line invocation
    '''
    if len(sys.argv) < 5:
        print('Usage: TournamentLogtoolProcessor [--force] url tournamentDir extractorClass dataPrefix options...')
    else:
        offset = 0
        force = False
        if sys.argv[1] == '--force':
            force = True
            offset = 1
        options = ''
        if len(sys.argv) > 5 + offset:
            for index in range(5 + offset, len(sys.argv)):
                options = options + ' ' + sys.argv[index]
            #print('options', options)

        iterate(sys.argv[1 + offset], sys.argv[2 + offset],
                sys.argv[3 + offset], sys.argv[4 + offset],
                options, force=force)

if __name__ == "__main__":
    #main()
    path= Path.cwd().parents[0]/'data'
    #iterate('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', str(path), 'org.powertac.logtool.example.TariffMktShare', 'TariffMktShare_','')
    iterate('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', str(path), 'org.powertac.logtool.example.BrokerAccounting', 'BrokerAccounting_','')
    #print('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', str(path), 'org.powertac.logtool.example.BrokerAccounting', 'BrokerAccounting_','')
    #print(Path('data').absolute())
