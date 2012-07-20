#!/usr/bin/env python
"""  Ockle PDU and servers manager
This is the db Structure used both in the Logger plugin for logging,
  and the webserver for knowing what tables to access

Created on Jul 20, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

from sqlalchemy import  create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
    '''
    def __repr__(self):
        return "<LogEntry('%s','%s', '%s')>" % (self.server, self.time, self.dataDict)
        Base.metadata.create_all(self.engine)
        return
    '''