#!/usr/bin/env python
""" Ockle PDU and servers manager
A server node is a server with outlets,
or a service with the list of outlets to its servers that run it

Created on Mar 14, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from common.common import OpState

class ServerNodeOpState(OpState):
    init=-1# Did not start yet

class ServerNode():
    '''
    This class represents a PC in the network
    '''
    def setName(self,name):
        self.name = name
        
    def getName(self):
        return self.name
    
    def __init__(self,name,outlets=[],tests=[]):
        '''Constructor
        
        @param name: node name (string)
        @param outlets: a list of Outlet classes
        @param tests: a list of test classes
        '''
        self.setName(name)
        self.outlets = outlets
        self.tests = tests
        
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
        
    def turnOnTry(self):
        ''' Try to turn on server, if already on then don't do nothing
        @return: True if succeeded, false if not
        '''
        #TODO check if we want exceptions or other return types on failure
        self.setOutletsState(True)
        return
    
    def turnOn(self):
        ''' Turn on the server outlets, and check if all services are in order
        '''
        