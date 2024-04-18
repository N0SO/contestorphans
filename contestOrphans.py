#!/usr/bin/env python3
"""
Search the MOQP database callsigns that have not yet submitted a log
for this contest.

Update History is in file __init__.py
"""
DEBUG = True

from contestorphans.__init__ import VERSION
from moqputils.moqpdbutils import *
from moqputils.configs.moqpdbconfig import *
from datetime import datetime
from htmlutils.htmldoc import *
from cabrilloutils.CabrilloUtils import CabrilloUtils
from qrzutils.qrz.qrzlookup import QRZLookup


class findOrphans(): 
    def __init__(self, lookupcalls=True):
        self.orphans = dict()
        self.getOrphans(lookupcalls=True)
 
    def getOrphans(self, lookupcalls=True):
        db = MOQPDBUtils(HOSTNAME, USER, PW, DBNAME)
        db.setCursorDict()
        cu = CabrilloUtils()
        """
        Get one unique urcall (stations worked) for every QSO in the DB
        """
        stationsWorked = db.read_query("""SELECT UNIQUE URCALL
                     FROM QSOS WHERE 1 order by URCALL""") 
        for st in stationsWorked:
            orphancall = cu.stripCallsign(st['URCALL'])
            if (db.CallinLogDB(orphancall) == None) and \
                   (orphancall not in self.orphans.keys()):
                oc= orphanCall(callsign = orphancall, 
                               db=db,
                               lookupcall=lookupcalls)
                if(len(oc.workedBy)) > 0:
                    self.orphans[orphancall]=oc
        self._saveToTable(db)
        return self.orphans   
        
    def _saveToTable(self, db):
        dquery ='DROP TABLE IF EXISTS ORPHANS'
        dquery1 = """CREATE TABLE `ORPHANS` ( 
        `ID` INT NOT NULL AUTO_INCREMENT , 
        `ORPHANCALL` VARCHAR(16) NULL DEFAULT NULL ,
        `UNIQUESTATIONS` INT NULL,
        `TOTALQSOS` INT NULL, 
        `OPNAME` VARCHAR(40) NULL DEFAULT NULL,
        `OPEMAIL` VARCHAR(40) NULL DEFAULT NULL,
        `WORKEDBY` VARCHAR(4096) NULL DEFAULT NULL , 
        PRIMARY KEY (`ID`)) ENGINE = InnoDB;"""
        db.write_query(dquery) # Delete old digital tables  
        db.write_query(dquery1) # create new empty table 
        calllist= list(self.orphans.keys())
        for call in calllist:
            workedby=''
            totalqs = len( db.read_query("""SELECT URCALL FROM QSOS 
                    WHERE URCALL = '{}';""".format(call)) )
            #print('{} totalqs = {}'.format(call, totalqs))
            for wk in self.orphans[call].workedBy:
                workedby += wk + ' '
            print('Saving log orphan {} to database...'.format(\
                                           self.orphans[call].callsign))
            orphanid = db.write_pquery(\
               """INSERT INTO ORPHANS 
                  (ORPHANCALL, UNIQUESTATIONS, TOTALQSOS, OPNAME,
                     OPEMAIL, WORKEDBY)
                  VALUES (%s, %s, %s, %s, %s, %s)""",
               [ self.orphans[call].callsign,
                len(self.orphans[call].workedBy), 
                totalqs,
                self.orphans[call].opname,
                self.orphans[call].opemail,
                workedby ] )
            """
            print('Writing {}\n{}\n{}'.format(orphanid,
                                          self.orphans[call].callsign,
                                          self.orphans[call].workedBy))
            """        
      

class orphanCall():
    
    def __init__(self, callsign = None, 
                       workedby = [],
                       opname = None,
                       opemail = None,
                       db = None,
                       lookupcall = True):
        self.callsign = callsign
        self.workedBy = workedby
        self.opname = opname
        self.opemail = opemail
        if callsign and lookupcall:
            self.getOpData(callsign)
        if db:
            self.fillworkedBy(db)
            
    def getOpData(self, callsign):
        self.qrz=QRZLookup('/home/pi/Projects/moqputils/moqputils/configs/qrzsettings.cfg')
        if DEBUG: 
            print('Looking up orphan {} ...'.format(callsign))

        try:
            opdata = self.qrz.callsign(callsign.strip())
            qrzdata=True
            #print(opdata
            if 'name_fmt' in opdata:
                self.opname = opdata['name_fmt'].upper()
            elif ('fname' in opdata) and ('name' in opdata):
                self.opname = ('{} {}'.format(\
                                                 opdata['fname'].upper(),
                                                 opdata['name'].upper()))
            elif ('attn' in opdata) and ('name' in opdata):
                self.opname = ('{} ATTN {}'.format(\
                                                 opdata['name'].upper(),
                                                 opdata['att1'].upper()))
            elif ('name' in opdata):
                self.opname = ('{}'.format(\
                                                 opdata['name'].upper()))
            else:
                self.opname=('***NO NAME FOR {} ***'.format(\
                                                 op.upper()))
            if ('email' in opdata):
                self.opemail = opdata['email'].upper()                       
            else:                        
                self.opemail = ''                       
           
        except:
            qrzdata=False
            print('NO QRZ for {}'.format(callsign))

    def fillworkedBy(self, db):
        if DEBUG:
                print('Filling in stations workedBy for log orphan {}...'.format(self.callsign))
        #print(self.workedBy)
        qsos = db.read_query("""SELECT UNIQUE URCALL,MYCALL FROM QSOS 
                         WHERE URCALL LIKE '{}' ORDER BY MYCALL""".format(self.callsign))
        #print(len(qsos))
        self.workedBy = []
        for q in qsos:
            #print(q['MYCALL'])
            self.workedBy.append(q['MYCALL'])
            
        #print(self.workedBy)
        return self.workedBy
        
    def getVals(self):
        return (self.callsign, self.opname, self.opemail, self.workedBy)
        
    def getCSV(self):
        return ('{}\t{}\t{}\t{}'.format(self.callsign,
                                       self.opname,
                                       self.opemail,
                                       self.workedBy))
                                       
    def getHTML(self):
      return('<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.\
              format(self.callsign,
                     self.opname,
                     self.opemail,
                     self.workedBy))

   
    def getDict(self):
        return {'callsign':self.callsign,
                    'opname':self.opname,
                    'opemail':self.opemail,
                    'workedBy':self.workedBy}
        
class orphanReport():
    def __init__(self, reportdata =  None):
        self. reportData = reportdata
        if reportdata == None:
            self.fetchReport()
        self.appMain()
        
    def fetchReport(self):
        db = MOQPDBUtils(HOSTNAME, USER, PW, DBNAME)
        db.setCursorDict()
        tableData = db.read_query("""SELECT * FROM ORPHANS WHERE 1 ORDER BY UNIQUESTATIONS DESC;""")
        if (tableData == None) or (len(tableData) == 0):
            print("No data - run mqporphans --create first.")
            exit(0)
        self.reportData = self.makeReport(tableData)
        return tableData

    def makeReport(self, td):
        reportdata = [\
          'ORPHAN CALL\tUNIQUE STATION COUNT\tTOTAL QSOS\tWORKED BY']
        
        for uc in td:
            reportdata.append('{}\t{}\t{}\t{}'.format(\
                                                  uc['ORPHANCALL'],
                                                  uc['UNIQUESTATIONS'],
                                                  uc['TOTALQSOS'],
                                                  uc['WORKEDBY'])) 
                                                  
        self.reportData = reportdata
        return reportdata
        
    def showReport(self):
        for l in self.reportData:
            print(l)
            
    def appMain(self):
        self.showReport()
 
class htmlOrphan(orphanReport):
    def appMain(self):
        htmld = self.makeHTML(self.reportData)
        #print (htmd)
        d = htmlDoc()
        d.openHead(\
           '{} Missouri QSO Orphaned Calls Report'\
               .format(YEAR),'./styles.css')
        d.closeHead()
        d.openBody()
        d.addTimeTag(prefix='Report Generated On ', 
                    tagType='comment') 
                         
        d.add_unformated_text(\
           """<h2 align='center'>{} Missouri QSO Party Orphaned Calls Report</h2>\n""".format(YEAR))

        d.add_unformated_text(\
           """<p align='center'>The ORPHANCALL stations appear in other
              people's logs, but they HAVE NOT yet submitted a log.</p> """)
        
        d.addTable(htmld, header=True)
        d.closeBody()
        d.closeDoc()

        d.showDoc()

        
    def makeHTML(self, csvd):
        htmd = []
        for crow in csvd:
            hrow = crow.split('\t')
            htmd.append(hrow)
        #print(htmd)
        return htmd

