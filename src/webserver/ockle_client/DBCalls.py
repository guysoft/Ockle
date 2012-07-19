"""  Ockle PDU and servers manager
Client calls to the Ockle Database

Created on Jul 18, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

from ConfigParser import SafeConfigParser
from common.common import appendProjectPath

from sqlalchemy import  create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import json

config = SafeConfigParser()
import os.path, sys
ETC_DIR= os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),'..',"etc")
config.read(os.path.join(ETC_DIR,"config.ini"))
LOG_DB = config.get('plugins.Logger', 'LOG_DB')
LOG_DB = LOG_DB.replace("%HOME%", os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])).replace("/src", "/")))


#Database declaration
Base = declarative_base()
class Log(Base):
    '''This is the SQLiteAlchemy database structure, in the declarative form
    '''
    __tablename__ = 'log'
    
    id = Column(Integer, primary_key=True)
    server = Column(String)
    dataDict = Column(String)
    time = Column(String)
    
    def __init__(self, server, dataDict, time):
        self.server = server
        self.dataDict = json.dumps(dataDict)
        self.time = time
    
    def __repr__(self):
        return "<LogEntry('%s','%s', '%s')>" % (self.server, self.time, self.dataDict)
        Base.metadata.create_all(self.engine)
        return

class Reader():
    def __init__(self):
        self.LOG_DB = LOG_DB
        self.Log = Log
        
        self.engine = create_engine(self.LOG_DB)
        return
    def getDBInfo(self,server,fromTime,toTime):
        ''' Get the data information from the log between a given timeframe
        @return: A table with the results
        '''
        
        connection = self.engine.connect()
        if server==None:
            sql = "SELECT * FROM " + self.Log.__tablename__ + " WHERE time>=? AND time<=?"
            variables = (fromTime,toTime)
        else:
            sql = "SELECT * FROM " + self.Log.__tablename__ + " WHERE time>=? AND time<=? AND server=?"
            print sql
            variables = (fromTime,toTime,server)
            
        result = connection.execute(sql,variables)
        returnValue = result.fetchall()
        connection.close()
        
        return returnValue
    
    def ConnectionHandlerServerLog(self,dataDict):
        '''
        Connection handler command to get the server log
        @param dataDict: The data dict 
        '''
        
        #check if to return all servers, or a specific one
        if not dataDict.has_key("fromTime") or not dataDict.has_key("toTime"):
            self.debug("Got invalid ServerLog request")
            return {}
        
        result = {}
        if dataDict.has_key("server"):
            result = self.getDBInfo(dataDict["server"], dataDict["fromTime"], dataDict["toTime"])
        else:
            result = self.getDBInfo(None, dataDict["fromTime"], dataDict["toTime"])
        
        #Convert RowProxy type to dict
        returnValue = {}
        i=0
        for row in result:
            returnValue[str(i)] = dict(row)
            i=i+1
            
        return returnValue
    

def getDataFromDB(sql):
    request = None
    return request

READER = Reader()
def getServerStatistics(server,fromtime,totime):   
    #return html.fromstring(str(response)).text 
    #response = getDBInfo(server,fromtime,totime)
    response = READER.ConnectionHandlerServerLog({"server":server, "fromTime" : "1", "toTime" : "2342355321.28"})
    if response == None:
        return {}#error
    else:
        return response
    return