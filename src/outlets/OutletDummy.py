#!/usr/bin/env python
""" Ockle PDU and servers manager
A dummy outlet, useful for testing

Created on Mar 7, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from OutletTemplate import OutletTemplate

class Dummy(OutletTemplate):
    ''' A dummy outlet, useful for testing
    '''
    def __init__(self,name,outletConfigDict={},outletParams={}):
        OutletTemplate.__init__(self,name,outletConfigDict,outletParams)
        self.setState(False)
        return
    
    def _setOutletState(self,state):
        self.state = state
        return
    
    def updateState(self):
        self.state=self._getOutletState()
        
    def _getOutletState(self):
        try:
            self.state
        except AttributeError:
            self.state = False 
        return self.state
        
        