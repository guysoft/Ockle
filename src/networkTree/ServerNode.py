#!/usr/bin/env python
""" Ockle PDU and servers manager
A server node is a server with outlets,
or a service with the list of outlets to its servers that run it

Created on Mar 14, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
class ServerNode():
    '''
    This class represents a PC in the network
    '''
    def setName(self,name):
        self.name = name
        
    def getName(self):
        return self.name
    
    def __init__(self,name,outlets):
        '''Constructor
        
        @param name: node name (string)
        @param outlets: a list of Outlet classes  
        '''
        self.setName(name)
        self.outlets = outlets
        
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
        '''
        for outlet in self.outlets:
            outlet.setState(state)
        