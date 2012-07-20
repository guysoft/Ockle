#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to add a bounch of basic communication commands

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
from plugins.ModuleTemplate import ModuleTemplate
import pygraph.readwrite.dot

class CoreCommunicationCommands(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def getDotGraph(self,dataDict):
        dot = pygraph.readwrite.dot.write(self.mainDaemon.servers.graph,False) 
        return {"Dot" :  dot}
    
    def getServerInfo(self,dataDict):
        ''' Get the data dict of a server
        @param dataDict: The data dict from the communication call, should contain the key "server"
        @return: the server information, empty dict if invalid request
        '''
        try:
            server = self.mainDaemon.servers.getServernode(dataDict["server"][0])
        except:
            return {} #no server found
        server.getName()
        outlets={}
        i=0;
        for outlet in server.getOutlets():
            outletIndex="Outlet"+str(i)
            outlets[outletIndex] ={} 
            outlets[outletIndex]["type"] = outlet.getOutletType()
            outlets[outletIndex]["OpState"] = outlet.getOpState()
            outlets[outletIndex]["data"] = outlet.getData()
            i=i+1
            
        return {"Name" :  server.getName(),
                "OpState" : server.getOpState(),
                "outlets" : outlets,
                "StartAttempts" : server.getStartAttempts()
                }
    
    def run(self):
        self.debug("\n")
        self.mainDaemon.communicationHandler.AddCommandToList("dotgraph",lambda dataDict: self.getDotGraph(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("ServerView",lambda dataDict: self.getServerInfo(dataDict))

        return

if __name__ == "__main__":
    a = CoreCommunicationCommands(None)