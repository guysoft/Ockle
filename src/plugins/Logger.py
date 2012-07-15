#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to log server and outlet information to a database

Created on Jul 5, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
import time
from sqlalchemy import  create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)

from common.common import appendProjectPath
from plugins.ModuleTemplate import ModuleTemplate
from outlets.OutletTemplate import OutletOpState
from networkTree.ServerNode import ServerNodeOpState

import json

class Logger(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        #config variables init
        self.LOG_DB = self.getConfigVar("LOG_DB")
        self.LOG_DB = self.LOG_DB.replace("%HOME%", appendProjectPath())
        self.LOG_DB
        self.LOG_RESOLUTION = int(self.getConfigVar("LOG_RESOLUTION"))
        
        self.engine = create_engine(self.LOG_DB)
        
        self.InitDB()
        return
    
    def InitDB(self):
        ''' Subroutine to make sure the DB is good to go
        '''
        Base = declarative_base()
        
        #Database declaration
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
        
        Base.metadata.create_all(self.engine)
        
        #With this the DB structure is available across the logger module
        self.Log = Log
        return
    
    def run(self):
        #communication command binding
        self.mainDaemon.communicationHandler.AddCommandToList("ServerLog",lambda dataDict: self.ConnectionHandlerServerLog(dataDict))
        
        while True:
            self.appendToLog()
            self.debug("Appended server data to log")
            time.sleep(self.LOG_RESOLUTION)
        return
    
    def appendToLog(self):
        ''' Appends to the log the current status
        '''
        connection = self.engine.connect()
        for server in self.mainDaemon.servers.getSortedNodeList():
            sql = "insert into " + self.Log.__tablename__ + " values (?,?,?,?)"
            variables = (None,server.getName(),json.dumps(server.getOutletsDataDict()),str(time.time()))
            
            connection.execute(sql,variables)

        connection.close()
        return
    
    def clearDB(self):
        ''' Clears all the database!
        @return: The SQLAlchemy result
        '''
        connection = self.engine.connect()
        retult = connection.execute("DELETE FROM " + self.Log.__tablename__)
        connection.close()
        return retult
    
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
            result = self.getDBInfo(dataDict["server"][0], dataDict["fromTime"][0], dataDict["toTime"][0])
        else:
            result = self.getDBInfo(None, dataDict["fromTime"][0], dataDict["toTime"][0])
        
        #Convert RowProxy type to dict
        returnValue = {}
        i=0
        for row in result:
            returnValue[str(i)] = row
            i=i+1
            
        return returnValue

if __name__ == "__main__":
    a = Logger(None)
