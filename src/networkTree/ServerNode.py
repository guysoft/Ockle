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
    INIT=-1# Did not start yet

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
        ''' Get an outlet from a server, None if does not exist
        '''
        for outlet in self.getOutlets():
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
    
    def getNotOutletsOpState(self,opState):
        ''' Returns outlets that don't have a given opState
        @param opState:  
        @return: outlets that don't have a given state
        '''
        notOutletState = []
        for outlet in self.outlets:
            if outlet.getOpState() != opState:
                notOutletState.append(outlet)
        return notOutletState
    
    def getFailedTests(self):
        ''' return a list of failed tests
        '''
        failedTests = []
        return failedTests
    
    def getTesters(self):
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
    
    def getOutletsDataDict(self):
        ''' Returns a dict that holds all the outlets and their data dict.
        This gets sent to the logger
        @return: A dict with each outlet name, and a dict of its data
        '''
        returnValue = {}
        for outlet in self.getOutlets():
            returnValue["outlet" + outlet.getName()] = outlet.getData()
            returnValue["outlet" + outlet.getName()]["name"] = outlet.getName()
        return returnValue
    
    def turnOn(self):
        ''' Turn on the server outlets, and check if all services are in order
        '''
        self.setOpState(ServerNodeOpState.SwitcingOn)
        self.setOutletsOpState(ServerNodeOpState.SwitcingOn)
        self.incrementStartAttempt()
        
        nonWorkingOutlets = self.getNotOutletsOpState(OpState.OK)
        outletsFailList=[]
       
        while self.outletsStillStarting():
            for outlet in nonWorkingOutlets:
                if not outlet.setState(True): #TODO this should fork 
                    #Failed, set outlet and server state
                    outletsFailList.append(outlet)
                    outlet.setOpState(OutletOpState.failedToStart)
                    self.setOpState(ServerNodeOpState.failedToStart)
                else:
                    #Failed, set outlet state to ok
                    outlet.setOpState(OutletOpState.OK)
                    #self.setOpState(ServerNodeOpState.OK)
                    
            time.sleep(float(MAX_STARTUP_TIME))
        
        testersFailedList = []
        for tester in self.getTesters():
            tester.test()
            if tester.getOpState() == TesterOpState.FAILED:
                testersFailedList.append(tester)
        if outletsFailList or testersFailedList:
            #if we failed to start
            if MAX_ATTEMPTS != 0 and self.getStartAttempts() >= MAX_ATTEMPTS :
                self.setOpState(ServerNodeOpState.permanentlyFailedToStart)
            else:
                self.setOpState(ServerNodeOpState.failedToStart)
        else:
            self.setOpState(ServerNodeOpState.OK)
            
        return
        