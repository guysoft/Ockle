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

from common.workerEngine import workerEngine

class AutoControl(ModuleTemplate):
    ''' Automatic on/off Control of servers'''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.WAIT_TIME = self.getConfigVar("WAIT_TIME")
        self.MAX_START_ATTEPMTS = self.getConfigVar("MAX_START_ATTEPMTS")
        
        self.setEnabled(False)
        
        #Add variable to all server Nodes
        for server in self.mainDaemon.servers.getSortedNodeList():
            
            server.desiredOpState=ServerNodeOpState.OK
        
        #Communication commands
        self.mainDaemon.communicationHandler.AddCommandToList("getAutoControlStatus",
                                                              lambda dataDict: self.getAutoControlStatus(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("setAutoControlStatus",
                                                              lambda dataDict: self.setAutoControlStatusCommand(dataDict["state"]))
        
        self.workers = workerEngine()
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
        '''
        self.turnOnSequence()

        print "SHUTTING DOWN!!!!!!!!!!!!!!!!!!!!!"
        print self.workers.getWorkers()
        time.sleep(1)
        self.turnOffSequence()
        '''
        self.mainDaemon.servers.updateNetwork()
                        
        return
    
    def startup(self,server):
        return
    
    def turnOnSequence(self):
        destOpStates = [ServerNodeOpState.permanentlyFailedToStart,ServerNodeOpState.SwitcingOn,ServerNodeOpState.SwitchingOff]
        return self.actionSquence("on",self.mainDaemon.servers.turnOnServer,self.mainDaemon.servers.isReadyToTurnOn,destOpStates,ServerNodeOpState.OK)

    def turnOffSequence(self):
        destOpStates = [ServerNodeOpState.failedToStop,ServerNodeOpState.SwitcingOn,ServerNodeOpState.SwitchingOff]
        return self.actionSquence("off",self.mainDaemon.servers.turnOffServer,self.mainDaemon.servers.isReadyToTurnOff,destOpStates,ServerNodeOpState.OFF)
    
    def actionSquence(self,action,actionCallback,isReadyCallback,destOpStates,goalOpState):
        ''' Since turn on and turn of are the same in reverse,
        This function unifies the logic of the two
        @param action: the action name
        @param isReadyCallback: callback to check if we are ready to turn on/off
        @param destOpStates: List of server OpStates that we don't need to run the action on
        @param actionCallback: The action to be performed, takes in the sewer name as a variable
        @return: False if we are already running, True if ran
        '''
        
        if self.isEnabled():
            return False
        else:
            self.setEnabled(True)
        
        first = True
        attemptsToTurnOn=0#counter to count how many iterations went without turning something on
        #go in the loop and stay until we don't have any servers that are in intermediate states
        
        #TODO: make a better while condition
        while (first or self.mainDaemon.servers.turningOn()) and self.isEnabled() or self.isEnabled() and action == "off":
            attemptsToTurnOn+=1
            first = False
            for server in self.mainDaemon.servers.getSortedNodeList():
                serverName = server.getName()
                
                #Have we reached an end state?
                destOpStates = destOpStates + [goalOpState]
                if server.getOpState() in destOpStates:
                    pass
                elif isReadyCallback(serverName) and (not self.workers.isWorker(serverName)):
                    self.debug("Turning "+ action +" " + serverName)
                    
                    #TODO: BUG, commented line messes up order
                    if action =="on":
                        self.workers.addWorker(serverName,server.turnOn)
                    elif action == "off":
                        self.workers.addWorker(serverName,server.turnOff) 
                    #self.addWorker(serverName,server.turnOn)
                    attemptsToTurnOn = 0
                else: #server is either on already or is dependent on servers that are not on yet
                    pass
            self.workers.cleanDoneWorkers()
            
            
            #Turn off loop
            if  attemptsToTurnOn >= int(self.MAX_START_ATTEPMTS) or self.mainDaemon.servers.isAllOpState(goalOpState):
                self.setEnabled(False)
                self.workers.waitForWorkers()
            time.sleep(float(self.WAIT_TIME))
            self.workers.waitForWorkers()
            self.runningState = "standby"
        return True
    
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
        if state == "True":
            self.setEnabled(True)
                
        else:
            self.setEnabled(False)
        return {"succeeded" : True,"state": self.isEnabled()}

if __name__ == "__main__":
    a = AutoControl(None)
