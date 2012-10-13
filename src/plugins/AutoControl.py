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

ID=0
THREAD=1

class AutoControl(ModuleTemplate):
    ''' Automatic on/off Control of servers'''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.WAIT_TIME = self.getConfigVar("WAIT_TIME")
        self.MAX_START_ATTEPMTS = self.getConfigVar("MAX_START_ATTEPMTS")
        
        #list of worker threads
        self.workers=[]
        
        self.setEnabled(True)
        
        #Add variable to all server Nodes
        for server in self.mainDaemon.servers.getSortedNodeList():
            
            server.desiredOpState=ServerNodeOpState.OK
        
        #Communication commands
        self.mainDaemon.communicationHandler.AddCommandToList("getAutoControlStatus",lambda dataDict: self.getAutoControlStatus(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("setAutoControlStatus",lambda dataDict: self.setAutoControlStatusCommand(dataDict["state"]))
        return
    
    def addWorker(self,workerID,func):
        ''' Add a worker thread
        @param workerID: A unique string for the worker, usually the server name
        @param func: A function to work on
        @return: the thread, if needed
        '''
        t = FuncThread(func)
        self.workers.append((workerID,t))
        t.start()
        return t
    
    def isWorker(self,workerID):
        for worker in self.workers:
            if worker[ID] == workerID:
                return True
        return False
    
    def waitForWorkers(self):
        ''' Wait for all workers to finish'''
        for worker in self.workers:
            worker[THREAD].join()
        self.workers = []
    
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
        destOpStates = [ServerNodeOpState.permanentlyFailedToStart,ServerNodeOpState.SwitcingOn,ServerNodeOpState.SwitchingOff]
        return self.actionSquence("on",self.mainDaemon.servers.turnOnServer,self.mainDaemon.servers.isReadyToTurnOn,destOpStates,ServerNodeOpState.OK)

    def turnOffSequence(self):
        #TODO: write server network functions, IMPORTANT
        destOpStates = [ServerNodeOpState.failedToStop,ServerNodeOpState.SwitcingOn,ServerNodeOpState.SwitchingOff]
        return self.actionSquence("off",self.mainDaemon.servers.turnOffServer,self.mainDaemon.servers.isReadyToTurnOff,destOpStates,ServerNodeOpState.OFF)
    
    def actionSquence(self,action,actionCallback,isReadyCallback,destOpStates,goalOpState):
        ''' Since turn on and turn of are the same in reverse,
        This function unifies the logic of the two
        @param action: the action name
        @param isReadyCallback: callback to check if we are ready to turn on/off
        @param destOpStates: List of server OpStates that we don't need to run the action on
        @param actionCallback: The action to be performed, takes in the sewer name as a variable
        '''
        first = True
        attemptsToTurnOn=0#counter to count how many iterations went without turning something on
        while (first or self.mainDaemon.servers.turningOn()) and self.isEnabled():#go in the loop and stay until we don't have any servers that are in intermediate states
            attemptsToTurnOn+=1
            first = False
            for server in self.mainDaemon.servers.getSortedNodeList():
                serverName = server.getName()
                
                #Have we reached an end state?
                destOpStates = destOpStates + [goalOpState]
                if server.getOpState() in destOpStates:
                        pass
                elif isReadyCallback(serverName) and (not self.isWorker(serverName)):
                    self.debug("Turning "+ action +" " + serverName)
                    self.addWorker(serverName,lambda: actionCallback(serverName))
                    attemptsToTurnOn = 0
                else: #server is either on already or is dependent on servers that are not on yet
                    pass
            #Turn off loop
            if  attemptsToTurnOn >= int(self.MAX_START_ATTEPMTS) or self.mainDaemon.servers.isAllOpState(goalOpState):
                self.setEnabled(False)
                self.waitForWorkers()
                
            time.sleep(float(self.WAIT_TIME))
            
            self.runningState = "standby"
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
        if state == "True":
            self.setEnabled(True)
                
        else:
            self.setEnabled(False)
        return {"succeeded" : True,"state": self.isEnabled()}

if __name__ == "__main__":
    a = AutoControl(None)
