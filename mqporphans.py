#!/usr/bin/env python3
import os.path
import sys

whereami = os.path.split( os.path.realpath(__file__) )
pathsplit = os.path.split(whereami[0])
#print("here I am :", whereami, pathsplit)

DEVMODPATH = [pathsplit[0],'/home/pi/Projects/moqputils']
#print('Using DEVMODPATH=',DEVMODPATH)
#os.chdir(pathsplit[0])

for mypath in DEVMODPATH:
        if ( os.path.exists(mypath) and \
          (os.path.isfile(mypath) == False) ):
            sys.path.insert(0, mypath)

import argparse
from contestorphans.__init__ import VERSION

USAGE = \
"""
mqporphans
"""

DESCRIPTION = \
"""
Search the MOQP QSO records for QSOs with call signs that have not yet 
submitted a log for the current contest. Display the list as a TSV (Tab
Separated List) or in HTML.

"""

EPILOG = \
"""
That is all!
"""

def parseMyArgs():
    parser = argparse.ArgumentParser(\
                    description = DESCRIPTION, usage = USAGE)
    parser.add_argument('-v', '--version', 
                        action='version', 
                        version = VERSION)
    
    parser.add_argument('-c', '--createTable',
                                   action='store_true', 
                                   default=False,
            help="""Run the QSO database search and (re)create the
                    ORPHANS table in the MOQP database. The old table
                    will be replace, so if a backup is required,
                    run it first.""")

    parser.add_argument('-d', '--dontLookupCalls',
                                   action='store_false', 
                                   default=True,
            help="""Do not attempt to look up orphan callsigns on 
                    QRZ.COM. Note that call lookup adds significant 
                    time to the 
                    --createTable run time. """)

    parser.add_argument('-t', '--reportType',
                                   default = 'csv',
            help="""Set report type for output. Only valid if more than
                    one report output type is avaible. Options are: 
                    csv (Comma Separated Variables) for printing or
                    for import to a spreadsheet, or 
                    html for web page use.
                    default value is csv""")

    parser.add_argument('-u', '--unitTest',
                                   default = None,
            help="""Unit test class orphanCalls""")


    args = parser.parse_args()
    return args
    
    
if __name__ == '__main__':
    args = parseMyArgs()
    if args.unitTest:
        from contestorphans.contestOrphans import orphanCall
        c = orphanCall(callsign = args.unitTest, 
                                  lookupcall=args.dontLookupCalls)
        print(c.getCSV())
        #print(c.getDict())
        #print(c.getHTML())
        exit()
        
    if args.createTable:
        from contestorphans.contestOrphans import findOrphans
        app=findOrphans(lookupcalls=args.dontLookupCalls)
    if args.reportType:
        reptype = args.reportType.lower()
        if reptype == 'csv':
            from contestorphans.contestOrphans import orphanReport
            app = orphanReport()
        elif reptype == 'html':
            from contestorphans.contestOrphans import htmlOrphan
            app = htmlOrphan()
    else:
        print('No action specified: {}'.format(args))
