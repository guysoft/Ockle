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

import threading
 
class FuncThread(threading.Thread):
    '''
    A class to make functions threadable
    '''
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
        return
 
    def run(self):
        self._target(*self._args)
        return

class AutoControl(ModuleTemplate):
    ''' Automatic on/off Control of servers'''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.WAIT_TIME = self.getConfigVar("WAIT_TIME")
        self.MAX_START_ATTEPMTS = self.getConfigVar("MAX_START_ATTEPMTS")
        
        self.setEnabled(True) 
        
        #Communication commands
        self.mainDaemon.communicationHandler.AddCommandToList("getAutoControlStatus",lambda dataDict: self.getAutoControlStatus(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("setAutoControlStatus",lambda dataDict: self.getAutoControlStatus(dataDict["state"]))
        return
    
    def setEnabled(self,state):
        ''' Set if the Auto control is turned on
        '''
        self.enabled=state
        
    def isEnabled(self):
        ''' Get if auto control is enabled
        @return: True if auto control is enabled
        '''
        return self.enabled
    
    def run(self):
        t1 = FuncThread(self.turnOnSequence)
        t1.start()
        t1.join()
                        
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
        attemptsToTurnOn=0#counter to count how many iterations went without turning something on
        while (first or self.mainDaemon.servers.turningOn()) and self.isEnabled():#go in the loop and stay until we don't have any servers that are in intermediate states
            attemptsToTurnOn+=1
            first = False
            for server in self.mainDaemon.servers.getSortedNodeList():
                if server.getOpState() == ServerNodeOpState.OK or server.getOpState() == ServerNodeOpState.permanentlyFailedToStart:
                        pass
                elif self.mainDaemon.servers.isReadyToTurnOn(server.getName()):
                    self.mainDaemon.debug("Turning on " + server.getName())
                    server.turnOn()#TODO should be threaded
                    attemptsToTurnOn = 0
                else: #server is either on already or is dependent on servers that are not on yet
                    pass
            #Turn off loop
            if  attemptsToTurnOn >= int(self.MAX_START_ATTEPMTS) or self.mainDaemon.servers.isAllOn():
                self.setEnabled(False)
            time.sleep(float(self.WAIT_TIME))
        return
    
    def getAutoControlStatus(self,dataDict):
        ''' Check if Auto Control is on from the network
        @param dataDict: The dataDict
        @return: The response dict, answer in value 'status'
        '''
        if self.isEnabled():
            return {'status' : 'on'}
        else:
            return {'status' : 'off'}
        return {}
    
    def setAutoControlStatusCommand(self,state):
        if state == "true":
            self.setEnabled(True)
        else:
            self.setEnabled(False)
        return {"succeeded" : True}

if __name__ == "__main__":
    a = AutoControl(None)
