#!/usr/bin/env python
""" Ockle PDU and servers manager
A dummy outlet, useful for testing

Created on Mar 7, 2012

@author: Guy Sheffer <guysoft at mail.huji.ac.il>
"""
from OutletTemplate import OutletTemplate
class Dummy(OutletTemplate):
    '''
    This class is an instance of an outlet within the pdu, you must spesify a number
    '''
    def __init__(self,outletConfigDict={},outletParams={}):
        #TODO: fix declaration
        #super(Dummy).__init__(outletConfigDict,outletParams)
        self.state = False
        return
    
    def _setOutletState(self,state):
        self.state = state
        return
    
    def setState(self,state):
        self._setOutletState(state)
        self.updateState()
        return
    
    def getState(self):
        return self.state
    
    def updateState(self):
        self.state=self._getOuteletState()
        
    def _getOuteletState(self):
        return self.state
        