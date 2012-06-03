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

config,ETC_DIR = loadConfig()
MAX_STARTUP_TIME = config.get('servers', 'MAX_STARTUP_TIME')

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
    
    def __init__(self,name,outlets=[],testers=[]):
        '''Constructor
        
        @param name: node name (string)
        @param outlets: a list of Outlet classes
        @param tests: a list of test classes
        '''
        self.setName(name)
        self.outlets = outlets #list of outlets types for the server
        self.testers = testers #list of testers to make sure server is preforming right
        self.setOutletsState(OutletOpState.INIT) #server state
        self.setOpState(ServerNodeOpState.INIT)
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
    
    def getNotOutletsState(self,state):
        ''' Returns outlets that don't have a given state
        @param state:  
        @return: outlets that don't have a given state
        '''
        notOutletState = []
        for outlet in self.outlets:
            if outlet.getOpState() != state:
                notOutletState.append(outlet)
        return notOutletState
    
    def getFailedTests(self):
        ''' return a list of failed tests
        '''
        failedTests = []
        return failedTests
    
    def getTesters(self):
        return self.testers
    
    def setOpState(self,state):
        ''' Set the oprating state of the server
        '''
        self.state = state
        return
    def getOpState(self):
        return self.state
    
    def turnOn(self):
        ''' Turn on the server outlets, and check if all services are in order
        '''
        self.setOpState(ServerNodeOpState.SwitcingOn)
        
        self.setOutletsState(ServerNodeOpState.SwitcingOn)
        nonWorkingOutlets = self.getNotOutletsState(OpState.OK)
        
        outletsFailList=[]
        #STOPED HERE!
        '''
        while OUTLETS_STILL_STARTING:
            for outlet in nonWorkingOutlets:
                if not outlet.setState(True): #TODO this should fork 
                    outletsFailList.append(outlet)
                    self.setOutletState(OpState.failedToStart)
                else:
                    self.setOutletState(OpState.OK)
                    
            time.sleep(MAX_STARTUP_TIME)
        
        for tester in self.getTesters():
            if tester.run():
                TESTER SET OK AND MARK AS DONE
            else:
                APPEND TO FAIL LIST AND MARK AS FAIL
            
        if outletsFailList or testersFailedList:
            self.setOpState(ServerNodeOpState.failedToStart)
        else:
            self.setOpState(ServerNodeOpState.OK)
        '''  
        return
        