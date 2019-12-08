#!/usr/bin/python3
'''
Applies a specific logtool analyzer to all the sim logs in a tournament,
using TournamentGameIterator.csvIterator to pull in the game logs.
'''

import TournamentGameIterator as ti
import string, re, os, subprocess, sys
from pathlib import Path
import logging

processEnv = {'JAVA_HOME': os.environ.get('JAVA_HOME'),
              'Path' : os.environ.get('PATH') }

list_logs_per = ['BrokerAccounting']
list_logs = ['BrokerBalancingActions','BrokerImbalanceCost','ImbalanceStats','ImbalanceSummary','BrokerCosts','BrokerMktPrices','BrokerPriceAnomaly','CapacityAnalysis','CapacityValidator','CustomerBalancingCapacity','CustomerProductionConsumption','DemandResponseStats','EnergyMixStats','GameBrokerInfo','MeritOrder','MktPriceStats','ProductionConsumption','SolarProduction','TariffAnalysis','TariffMktShare','TotalDemand']

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
    print(str(dataPath))
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
                print(['mvn exec:exec -Dexec.args=\"' + args + '\"'])
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
    for data in dataFileIter(url, tournamentDir,
                             extractorClass, dataPrefix,
                             options, force=force):
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
    #path= Path.cwd().parents[0]/'data'  #adapt to name of logfile
    #iterate('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', str(path), 'org.powertac.logtool.example.TariffMktShare', 'TariffMktShare_','')
    #iterate('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', '/Volumes/WD/data', 'org.powertac.logtool.example.BrokerAccounting', 'BrokerAccounting_','--per-broker')
    number = 21
    iterate('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', '/Volumes/WD/data', 'org.powertac.logtool.example.{}'.format(list_logs_per[0]), '{}_'.format(list_logs_per[0]),'--per-broker')

    #print('https://powertac.org/wordpress/wp-content/uploads/2019/11/finals_2019_07.games_.csv', str(path), 'org.powertac.logtool.example.BrokerAccounting', 'BrokerAccounting_','')
    #print(Path('data').absolute())

