#!/usr/bin/env python
""" Ockle PDU and servers manager
Exceptions from the network tree data structure

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from common.Exceptions import Error

class ServerTreeError(Error):
    '''Base class for exceptions in this module.'''
    pass

class DependencyException(ServerTreeError):
    '''Exception raised for dependency cycles

    Attributes:
        @param list : List of nodes causing the cycle
        @param msg  : explanation of the error
    '''
    def __init__(self, nodesList, msg):
        self.list = nodesList
        self.msg = msg
        #self.debug(msg +":" + str(list))

class ServerNodeUnmetDependencies(ServerTreeError):
    '''Exception raised when a server dependencies failed to start
    @param server: server name
    @param requires: list of unmet dependencies
    '''
    def __init__(self, server,requires):
        self.debug("Can't start server node " + server+ ". unmet dependencies:" + str(requires))