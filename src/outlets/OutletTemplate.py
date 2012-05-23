#!/usr/bin/env python
""" Ockle PDU and servers manager
Template for an outlet object that all other outlets extend
Created on Mar 7, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from common.common import OpState
class OutletOpState(OpState):
    init=-1# Did not start yet

    
class OutletTemplate(object):
    '''
    @param outletConfigDict: a dictionary with the params specified in the ini config file, sections. Its a dict of sections with a dict of variables
    @param outletParams: A dictionary of the server-specific params specified in the outlet section on the server config file
    '''
    def __init__(self,outletConfigDict={},outletParams={}):
        self.OutletOpState = OutletOpState.OK #outlets are innocent until proven guilty
        return
    
    def _setOutletState(self,state):
        return
    
    def setState(self,state):
        return
    
    def getState(self):
        return self.state
    
    def updateState(self):
        return
        
    def _getOuteletState(self):
        return
    
    def setOpState(self,state):
        self.OutletOpState=state
    def getOpState(self):
        return self.OutletOpState
    
        