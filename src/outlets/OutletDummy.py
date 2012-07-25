#!/usr/bin/env python
""" Ockle PDU and servers manager
A dummy outlet, useful for testing

Created on Mar 7, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from OutletTemplate import OutletTemplate
import time

class Dummy(OutletTemplate):
    '''
    This class is an instance of an outlet within the pdu, you must specify a number
    '''
    def __init__(self,name,outletConfigDict={},outletParams={}):
        OutletTemplate.__init__(self,name,outletConfigDict,outletParams)
        self.setState(False)
        return
    
    def _setOutletState(self,state):
        self.state = state
        return
    
    def setState(self,state):
        self._setOutletState(state)
        #time.sleep(0.3)
        self.updateState()
        return True
    
    def getState(self):
        return self.state
    
    def updateState(self):
        self.state=self._getOuteletState()
        
    def _getOuteletState(self):
        try:
            self.state
        except AttributeError:
            self.state = False 
        return self.state
        
        