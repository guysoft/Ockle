#!/usr/bin/env python
""" Ockle PDU and servers manager
A server node is a server with outlets,
or a service with the list of outlets to its servers that run it

Created on Mar 14, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import time
from common.common import OpState
from common.common import loadConfig
from outlets.OutletTemplate import OutletOpState
from testers.TemplateTester import TesterOpState
from controllers.ControllerTemplate import ControllerOpState

config,ETC_DIR = loadConfig()
MAX_STARTUP_TIME = config.get('servers', 'MAX_STARTUP_TIME')
MAX_ATTEMPTS = int(config.get('servers', 'MAX_ATTEMPTS'))

class ServerNodeOpState(OpState):
    INIT="Did not initiate yet"# Did not start yet

class ServerNode():
    '''
    This class represents a PC in the network
    '''
    def setName(self,name):
        self.name = name
        
    def getName(self):
        return self.name
    
    def __init__(self,name,outlets=[],tests=[],controls=[]):
        '''Constructor
        
        @param name: node name (string)
        @param outlets: a list of Outlet classes
        @param tests: a list of test classes
        '''
        self.setName(name)
        self.outlets = outlets #list of outlets types for the server
        self.tests = tests #list of tests to make sure server is performing right
        self.controls = controls #list of controllers to control the server dirctly
        #self.setOutletsOpState(OutletOpState.INIT) #server state
        self.setOpState(ServerNodeOpState.INIT)
        self.startAttempts = 0 #reset startup attempts
        #TODO add shutdown attempts when implementing shutdown
        
        return
    
    def setState(self,state):
        '''
        Set server state
        @param state: server state type
        '''
        self.state = state
        return
        
    def getOutlet(self,number):
        ''' Get an outlet from the outlet list
        @param number outlet number in the list
        @return: an outlet type that is in the given place
        '''
        return self.outlets[number]
    
    def getOutlets(self):
        ''' Get a list of outlet numbers
        @return: a list of outlets
        '''
        return self.outlets
    
    def getOutletByName(self,outletSearchName):
        return self.__getServerObjByName(outletSearchName,self.getOutlets())

    def getControlByName(self,controlSearchName):
        return self.__getServerObjByName(controlSearchName,self.getControls())
    
    def __getServerObjByName(self,outletSearchName,objs):
        ''' Get an outlet from a server, None if does not exist
        '''
        for outlet in objs:
            if outlet.getName() == outletSearchName:
                return outlet
        return None
    
    def setOutletsState(self,state):
        ''' Sets the outlets all to a given state by force
        @param state: set the outlets to state (boolean)
        @return: A list of outlets the failed (note: you can check with "if not" to see if there was no failure
        '''
        outletFailList=[]
        for outlet in self.outlets:
            outlet.setState(state)
            if outlet.getState() != state:
                outletFailList.append(outlet)
        return outletFailList
    
    def setOutletsOpState(self,opState):
        ''' Set all the outlets to a given opState
        @param opState: The opState to set the outlets to
        '''
        for outlet in self.outlets:
            outlet.setOpState(opState)
        return
    
    def setControlOpState(self,opState):
        ''' Set all the controls to a given opState
        @param opState: The opState to set the control to
        '''
        for control in self.controls:
            control.setOpState(opState)
        return
    
    def getNotOutletsOpState(self,opState):
        ''' Returns outlets that don't have a given opState
        @param opState:  
        @return: outlets that don't have a given state
        '''
        notOutletState = []
        for outlet in self.getOutlets():
            if outlet.getOpState() != opState:
                notOutletState.append(outlet)
        return notOutletState

    def getNotControlsOpState(self,opState):
        ''' Returns controls that don't have a given opState
        @param opState:  
        @return: controls that don't have a given state
        '''
        notControlState = []
        for control in self.getControls():
            if control.getOpState() != opState:
                notControlState.append(control)
        return notControlState
 
    def getFailedTests(self):
        ''' return a list of failed tests
        '''
        failedTests = []
        return failedTests
    
    def getTests(self):
        return self.tests
    
    def getControls(self):
        return self.controls
    
    def setOpState(self,state):
        ''' Set the operating state of the server
        '''
        self.state = state
        return
    def getOpState(self):
        return self.state
    
    def outletsStillStarting(self):
        '''
        Return true if any outlet is still on SwitcingOn OpState
        '''
        for outlet in self.getOutlets():
            if outlet.getOpState() == OutletOpState.SwitcingOn:
                return True
        return False
    
    def controlsStillStarting(self):
        '''
        Return true if any control is still on SwitcingOn OpState
        '''
        for control in self.getControls():
            if control.getOpState() == ControllerOpState.SwitcingOn:
                return True
        return False
    
    def incrementStartAttempt(self):
        ''' Increment the startup attempt counter
        @return: Number of startup attempts
        '''
        self.startAttempts = self.startAttempts + 1
        return self.startAttempts
    
    def getStartAttempts(self):
        ''' Get number of startup attempts
        @return: Number of startup attempts
        '''
        return self.startAttempts
    
    def _getServerObjDataLog(self,objCallback,objName):
        ''' get server object data that we can store in the db log
        @param objCallback: A callback that gets the server object data
        @return: a dict for the logger
        '''
        returnValue = {}
        for serverObj in objCallback():
            returnValue[objName + serverObj.getName()] = serverObj.getData()
            returnValue[objName + serverObj.getName()]["name"] = serverObj.getName()
        return returnValue
    
    def getControlsDataDict(self):
        return self._getServerObjDataLog(self.getControls,"control") 
    
    def getOutletsDataDict(self):
        ''' Returns a dict that holds all the outlets and their data dict.
        This gets sent to the logger
        @return: A dict with each outlet name, and a dict of its data
        '''
        return self._getServerObjDataLog(self.getOutlets,"outlet")
    
    def turnOn(self):
        ''' Turn on the server outlets, and check if all services are in order
        '''
        self.incrementStartAttempt()
        
        #TODO: Add controls here
        self.setOpState(ServerNodeOpState.SwitcingOn)
        self.setOutletsOpState(OutletOpState.SwitcingOn)
        self.setControlOpState(ControllerOpState.SwitcingOn)
       
        def serverObjSwitchOn(sillRunningCallback,objOpState,getNonWorkingObj):
            nonWorkingObjs = getNonWorkingObj(OpState.OK)
            failList=[]
            while sillRunningCallback():
                for obj in nonWorkingObjs:
                    if not obj.setState(True): 
                        #Failed, set outlet and server state
                        failList.append(obj)
                        obj.setOpState(objOpState.failedToStart)
                        self.setOpState(ServerNodeOpState.failedToStart)
                    else:
                        #Failed, set obj state to ok
                        obj.setOpState(objOpState.OK)
                        #self.setOpState(ServerNodeOpState.OK
            time.sleep(float(MAX_STARTUP_TIME))
                
        outletsFailList  = serverObjSwitchOn(self.outletsStillStarting,OutletOpState,self.getNotOutletsOpState)
        controlsFailList = serverObjSwitchOn(self.controlsStillStarting,ControllerOpState,self.getNotControlsOpState)          
            
        
        testersFailedList = []
        for tester in self.getTests():
            tester.test()
            if tester.getOpState() == TesterOpState.FAILED:
                testersFailedList.append(tester)
        if outletsFailList or testersFailedList or controlsFailList:
            #if we failed to start
            if MAX_ATTEMPTS != 0 and self.getStartAttempts() >= MAX_ATTEMPTS :
                self.setOpState(ServerNodeOpState.permanentlyFailedToStart)
            else:
                self.setOpState(ServerNodeOpState.failedToStart)
        else:
            self.setOpState(ServerNodeOpState.OK)
            
        return
    
    def action(self,actionString):
        if actionString == "on":
            self.turnOn()
        else:
            self.turnOff()
            
    def turnOff(self):
        pass
        
