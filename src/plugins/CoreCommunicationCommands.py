#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to add a bunch of basic communication commands

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
from plugins.ModuleTemplate import ModuleTemplate
import pygraph.readwrite.dot
from common.common import iniToDict

from outlets.OutletTemplate import OutletOpState

import json

class CoreCommunicationCommands(ModuleTemplate):
    ''' Add of basic communication commands'''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def getDotGraph(self,dataDict):
        dot = pygraph.readwrite.dot.write(self.mainDaemon.servers.graph,False) 
        return {"Dot" :  dot}
    
    def getPDUDict(self):
        returnValue = {}
        for pdu in os.listdir(self.mainDaemon.OUTLETS_DIR):
            pdu = os.path.join(self.mainDaemon.OUTLETS_DIR,pdu)
            pduDict = iniToDict(pdu)
            pduName = os.path.splitext(os.path.basename(pdu))[0]
            returnValue[pduName] = pduDict
            
        return {"pdus" : json.dumps(returnValue)}
    
    def getServerInfo(self,dataDict):
        ''' Get the data dict of a server
        @param dataDict: The data dict from the communication call, should contain the key "server"
        @return: the server information, empty dict if invalid request
        '''
        try:
            server = self.mainDaemon.servers.getServernode(dataDict["server"])
        except:
            return {} #no server found
        server.getName()
        outlets={}
        outletNumber=1;
        for outlet in server.getOutlets():
            outletIndex="outlet"+str(outletNumber)
            outlets[outletIndex] ={} 
            outlets[outletIndex]["type"] = outlet.getOutletType()
            outlets[outletIndex]["OpState"] = outlet.getOpState()
            outlets[outletIndex]["state"] = outlet.getState()
            outlets[outletIndex]["data"] = outlet.getData()
            outlets[outletIndex]["name"] = outlet.getName()
            outletNumber=outletNumber+1
            
        return {"Name" :  server.getName(),
                "OpState" : server.getOpState(),
                "outlets" : json.dumps(outlets),
                "StartAttempts" : server.getStartAttempts()
                }
    
    def switchOutlet(self,dataDict):
        serverName = dataDict["server"]
        outletName = dataDict["outlet"]
        
        outletState = dataDict["state"] == "on" 
        
        outlet = self.mainDaemon.servers.getServer(serverName).getOutletByName(outletName)
        outlet.setState(outletState)
        if outletState:
            outlet.setOpState(OutletOpState.forcedOn)
        else:
            outlet.setOpState(OutletOpState.forcedOff)
        return {}
    
    def run(self):
        self.debug("\n")
        self.mainDaemon.communicationHandler.AddCommandToList("dotgraph",lambda dataDict: self.getDotGraph(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("ServerView",lambda dataDict: self.getServerInfo(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("getPDUDict",lambda dataDict: self.getPDUDict())
        self.mainDaemon.communicationHandler.AddCommandToList("switchOutlet",lambda dataDict: self.switchOutlet(dataDict))

        return 

if __name__ == "__main__":
    a = CoreCommunicationCommands(None)