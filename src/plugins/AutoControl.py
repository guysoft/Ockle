#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to automatically start up and manage the servers

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
import time

p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)

from plugins.ModuleTemplate import ModuleTemplate
from outlets.OutletTemplate import OutletOpState
from networkTree.ServerNode import ServerNodeOpState

class AutoControl(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.WAIT_TIME = self.getConfigVar("WAIT_TIME")
        return
    
    def run(self):
        self.turnOnSequence()
                        
        '''
        
        failedOutlets = server.setOutletsState(True)

        if self.mainDaemon.servers.canTurnOn(nextServer):
            nextServer.turnOn()
        self.debug("\n")
        
        for server in self.mainDaemon.servers.getSortedNodeList():
            self.startup(server)
        '''
        return
    
    def startup(self,server):
        return
    
    def turnOnSequence(self):
        first = True
        while not first or self.mainDaemon.servers.turningOn():#go in the loop and stay until we don't have any servers that are in intermediate states
            first = False
            for server in self.mainDaemon.servers.getSortedNodeList():
                if server.state == ServerNodeOpState.OK:
                        pass
                elif self.mainDaemon.servers.isReadyToTurnOn(server.getName()):
                    server.turnOn()# should be threaded
                else: #server is either on already or is dependent on servers that are not on yet
                    pass
                    
            time.sleep(self.WAIT_TIME)

if __name__ == "__main__":
    a = AutoControl(None)