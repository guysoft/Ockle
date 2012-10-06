#!/usr/bin/env python
""" Ockle PDU and servers manager
Template for a controller object that all other controllers extend
Controllers are used to send signals to the server node (mainly the shut down signal)

Created on Jul 26, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

from common.common import OpState
class ControllerOpState(OpState):
    INIT=-1# Did not start yet

class ControllerTemplate(object):
    '''
    @param controllerConfigDict: a dictionary with the params specified in the ini config file, sections. Its a dict of sections with a dict of variables
    @param controllerParams: A dictionary of the server-specific params specified in the controller section on the server config file
    '''
    def __init__(self,name,controllerConfigDict={},controllerParams={}):
        self.data={} #data information from the server
        self.setName(name)
        
        self.updateState()
        self.updateOpState()
        return
    
    def getName(self):
        return self.name
    
    def setName(self,name):
        self.name = name
    
    def getData(self):
        self.updateData()
        return self.data
    
    def updateData(self):
        pass
    
    def setSate(self,state):
        pass
    
    def getState(self):
        pass

    def updateState(self):
        pass

    def updateOpState(self):
        ''' Update the op state to on or off according to the on/off state of the outlet
        @return: the new opState
        '''
        if self.getState():
            self.setOpState(ControllerOpState.OK)
        else:
            self.setOpState(ControllerOpState.OFF)
        return
    
    def setOpState(self,state):
        self.OutletOpState=state
    def getOpState(self):
        return self.OutletOpState