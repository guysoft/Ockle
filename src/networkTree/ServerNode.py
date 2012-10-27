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
    ''' This class represents a PC in the network
    '''
    def setName(self,name):
        ''' Set the name of the Server
        :param name: The name ot be set '''
        self.name = name
        
    def getName(self):
        return self.name
    
    def __init__(self,name,outlets=[],tests=[],controls=[]):
        '''Constructor
        
        :param name: node name (string)
        :param outlets: a list of Outlet classes
        :param tests: a list of test classes
        '''
        self.setName(name)
        self.outlets = outlets #list of outlets types for the server
        self.tests = tests #list of tests to make sure server is performing right
        self.controls = controls #list of controllers to control the server dirctly
        #self.setOutletsOpState(OutletOpState.INIT) #server state
        self.setOpState(ServerNodeOpState.INIT)
        self.resetStartAttempt()
        self.resetShutdownAttempts()
        
        return
    
    def setState(self,state):
        '''
        Set server state
        
        :param state: server state type
        '''
        self.state = state
        return
        
    def getOutlet(self,number):
        ''' Get an outlet from the outlet list
        
        :param number outlet number in the list
        :return: an outlet type that is in the given place
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
    
    def getTestByName(self,TestSearchName):
        return self.__getServerObjByName(TestSearchName,self.getTests())
    
    def __getServerObjByName(self,outletSearchName,objs):
        ''' Get an outlet from a server, None if does not exist
        '''
        for outlet in objs:
            if outlet.getName() == outletSearchName:
                return outlet
        return None
    
    def setOutletsState(self,state):
        ''' Sets the outlets all to a given state by force
        
        :param state: set the outlets to state (boolean)
        :return: A list of outlets the failed (note: you can check with "if not" to see if there was no failure
        '''
        outletFailList=[]
        for outlet in self.outlets:
            outlet.setState(state)
            if outlet.getState() != state:
                outletFailList.append(outlet)
        return outletFailList
    
    def setOutletsOpState(self,opState):
        ''' Set all the outlets to a given opState
        
        :param opState: The opState to set the outlets to
        '''
        for outlet in self.outlets:
            outlet.setOpState(opState)
        return
    
    def setControlOpState(self,opState):
        ''' Set all the controls to a given opState
        
        :param opState: The opState to set the control to
        '''
        for control in self.controls:
            control.setOpState(opState)
        return
    
    def getNotOutletsOpState(self,opState):
        ''' Returns outlets that don't have a given opState
        
        :param opState:  
        :return: outlets that don't have a given state
        '''
        notOutletState = []
        for outlet in self.getOutlets():
            if outlet.getOpState() != opState:
                notOutletState.append(outlet)
        return notOutletState

    def getNotControlsOpState(self,opState):
        ''' Returns controls that don't have a given opState
        
        :param opState:  
        :return: controls that don't have a given state
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
            interDict = [OutletOpState.SwitcingOn,OutletOpState.SwitchingOff]
            if outlet.getOpState() in interDict:
                return True
        return False
    
    def controlsStillStarting(self):
        '''
        Return true if any control is still on SwitcingOn OpState
        '''
        for control in self.getControls():
            interDict = [ControllerOpState.SwitcingOn,ControllerOpState.SwitchingOff]
            if control.getOpState() in  interDict:
                return True
        return False
    
    def resetStartAttempt(self):
        self.startAttempts = 0
        return
    
    def resetShutdownAttempts(self):
        self.shutdownAttempts = 0
        return
    
    def incrementStartAttempt(self):
        ''' Increment the startup attempt counter
        
        :return: Number of startup attempts
        '''
        self.startAttempts += 1
        return self.startAttempts
    
    def incrementShutdownAttempt(self):
        ''' Increment the stop attempt counter
        
        :return: Number of shutdown attempts
        '''
        self.shutdownAttempts += 1
        return self.shutdownAttempts
    
    def getStartAttempts(self):
        ''' Get number of startup attempts
        
        :return: Number of startup attempts
        '''
        return self.startAttempts
    
    def getShutdownAttempts(self):
        ''' Get number of shutdown attempts
        
        :return: Number of shutdown attempts
        '''
        return self.shutdownAttempts
    
    def _getServerObjDataLog(self,objCallback,objName):
        ''' get server object data that we can store in the db log
        
        :param objCallback: A callback that gets the server object data
        :return: a dict for the logger
        '''
        returnValue = {}
        for serverObj in objCallback():
            returnValue[objName + serverObj.getName()] = serverObj.getData()
            returnValue[objName + serverObj.getName()]["name"] = serverObj.getName()
        return returnValue
    
    def getControlsDataDict(self):
        ''' Get the data dict of all the controls
        
        :returns: the controls data dict
        '''
        return self._getServerObjDataLog(self.getControls,"control") 
    
    def getOutletsDataDict(self):
        ''' Returns a dict that holds all the outlets and their data dict.
        This gets sent to the logger
        
        :return: A dict with each outlet name, and a dict of its data
        '''
        return self._getServerObjDataLog(self.getOutlets,"outlet")
    
    def serverObjSwitch(self,state,sillRunningCallback,serverFailState,
                        destState,failState,getNonWorkingObj):
        nonWorkingObjs = getNonWorkingObj(destState)
        failList=[]
        while sillRunningCallback():
            for obj in nonWorkingObjs:
                if not obj.setState(state): 
                    #Failed, set outlet and server state
                    failList.append(obj)
                    obj.setOpState(failState)
                    self.setOpState(serverFailState)
                else:
                    print "obj " +str(obj.getName()) +" to " + str(state)
                    #Failed, set obj state to ok
                    obj.setOpState(destState)
                    #self.setOpState(ServerNodeOpState.O
        time.sleep(float(MAX_STARTUP_TIME))
        return failList
    
    def _turnAction(self,incrementer,getActionAttempts,serverDestState,serverInterState,
                   serverFailState,serverPermanentFailState,destObjState,
                   
                   outletDestState, outletInterState,outletFailState,
                   controllerDestState, controlInterState,controllerFailState,runTesters=True,ignoreDeps=False):
        ''' Run an action to turn on or off the server
        
        :param ignoreDeps: Should we ignore failures
        :param incrementer: Used to increment the attempts at the action
        :param serverDestState: The destination opState of the server
        :param serverInterState: The intermediate state of the server
        :param serverFailState: What server OpState is should be set if we fail on this action
        :param serverPermanentFailState: the permanent OpState of serverFailState
        :param destObjState: The destination state for Server Objects
        :param outletDestState: The state the outlet would be set at the end of this action
        :param outletInterState: The outlet intermediate OpState
        :param outletFailState: The fail OpState of the outlet is this action has failed
        :param controllerDestState: The OpState the control would be set at the end of this action
        :param controlInterState: The control intermediate OpState
        :param controllerFailState: The fail OpState of the control is this action has failed
        '''
        incrementer()
        
        self.setOpState(serverInterState)
        self.setOutletsOpState(outletInterState)
        self.setControlOpState(controlInterState)
               
        outletsFailList  = self.serverObjSwitch(destObjState,self.outletsStillStarting,serverFailState,
                                                outletDestState,outletFailState,self.getNotOutletsOpState)
        controlsFailList = self.serverObjSwitch(destObjState,self.controlsStillStarting,serverFailState,
                                                controllerDestState,controllerFailState,self.getNotControlsOpState)          
        
        testersFailedList = []
        if runTesters and not ignoreDeps:
            for tester in self.getTests():
                tester.runTest()
                if tester.getOpState() == TesterOpState.FAILED:
                    testersFailedList.append(tester)
            
        if not ignoreDeps:
            if outletsFailList or testersFailedList or controlsFailList:
                #if we failed to start
                if MAX_ATTEMPTS != 0 and getActionAttempts() >= MAX_ATTEMPTS :
                    self.setOpState(serverPermanentFailState)
                else:
                    self.setOpState(serverFailState)
            else:
                self.setOpState(serverDestState)
        else:
            self.setOpState(serverDestState)
        return
    
    def action(self,actionString,ignoreDeps=False):
        ''' Execute an on/off action on the server
        
        :param actionString: Either "on" or "off"
        :param ignoreDeps: True if you want to ignore other server dependencies
        '''
        if actionString == "on":
            self.turnOn(ignoreDeps)
        else:
            self.turnOff(ignoreDeps)
    
    def turnOn(self,ignoreDeps=False):
        ''' Turn on the server outlets, and check if all services are in order
        
        :param ignoreDeps: True if you want to ignore other server dependencies
        '''
        self.resetShutdownAttempts()
        return self._turnAction(self.incrementStartAttempt,self.getStartAttempts,ServerNodeOpState.OK,ServerNodeOpState.SwitcingOn,
                               ServerNodeOpState.failedToStart,ServerNodeOpState.permanentlyFailedToStart, True,
                               
                               OutletOpState.OK,OutletOpState.SwitcingOn,OutletOpState.failedToStart,
                               ControllerOpState.OK,ControllerOpState.SwitchingOff,ControllerOpState.failedToStart,True,
                               ignoreDeps)
    
    def turnOff(self,ignoreDeps=False):
        self.resetShutdownAttempts()
        return self._turnAction(self.incrementShutdownAttempt,self.getShutdownAttempts,ServerNodeOpState.OFF,ServerNodeOpState.SwitchingOff,
                               ServerNodeOpState.failedToStop,ServerNodeOpState.permanentlyFailedToStop,False,
                               
                               OutletOpState.OFF,OutletOpState.SwitchingOff,OutletOpState.failedToStop,
                               ControllerOpState.OFF,OutletOpState.SwitchingOff,ControllerOpState.failedToStart,False,
                               ignoreDeps)
        
    def updateOpState(self,runTests=True):
        ''' Update all the OpStates and run all tests of the server
        '''
        generalOpState=True
        serverOpState=ServerNodeOpState.INIT
        
        def calcServerOpState(obj,onServerObjOpState,offServerObjOpState,serverOpState,generalOpState):
            if generalOpState:
                if serverOpState == ServerNodeOpState.INIT:
                    #INIT, set what we have
                    if obj.getOpState() == onServerObjOpState:
                        serverOpState = ServerNodeOpState.OK
                    else:
                        if ServerNodeOpState.OFF:
                            generalOpState = offServerObjOpState
                else:
                    #We have something set
                    if obj.getOpState() == onServerObjOpState or serverOpState != ServerNodeOpState.OK:
                            generalOpState = False
                            
                    elif obj.getOpState() == offServerObjOpState and serverOpState != ServerNodeOpState.OFF:
                            generalOpSate = False
            return generalOpState,serverOpState,serverOpState,generalOpState
        
        #TODO: make this less iffy
        for outlet in self.getOutlets():
            outlet.updateOpState()
            generalOpSate,serverOpState,serverOpState,generalOpState = calcServerOpState(outlet,OutletOpState.OK,OutletOpState.OFF,serverOpState,generalOpState)
                            
            
        for control in self.getControls():
            control.updateOpState()
            generalOpSate,serverOpState,serverOpState,generalOpState = calcServerOpState(outlet,ControllerOpState.OK,ControllerOpState.OFF,serverOpState,generalOpState)
        
        
        if serverOpState == ServerNodeOpState.OK and generalOpSate and runTests:
            for test in self.getTests():
                test.runTest()
                if test.gesetOpStatetOpState() == TesterOpState.FAILED:
                    serverOpState = ServerNodeOpState.failedToStart
                    break
            
        if generalOpState:
            self.setOpState(serverOpState)

        return
        
