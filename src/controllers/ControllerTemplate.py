#!/usr/bin/env python
""" Ockle PDU and servers manager
Template for a controller object that all other controllers extend
Controllers are used to send signals to the server node (mainly the shut down signal)

Created on Jul 26, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

from common.common import OpState
class ControllerOpState(OpState):
    INIT=-1 #: Did not start yet

class ControllerTemplate(object):
    ''' Template for a control object that all other controls extend
    
    :ivar data: Holds a dict of the data from the control'''
    
    ''' Constructor
    
    :param controllerConfigDict: a dictionary with the params specified in the ini config file, sections. Its a dict of sections with a dict of variables
    :param controllerParams: A dictionary of the server-specific params specified in the controller section on the server config file
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
        try:
            return self.data
        except AttributeError:
            pass
    
    def updateData(self):
        '''To  be Implemented in the child, updates the ``self.data`` variable
        '''
        pass
    
    def _getControlState(self):
        ''' To be implemented by the child, sets the control's state
        
        :return: The current control state ''' 
        pass
    
    def _setControlState(self,state):
        ''' To be implemented by the child, sets the control's state 
        
        :param bool state: The state to set '''
        pass

    def getState(self):
        return self.state
    
    def updateState(self):
        self.state=self._getControlState()

    def updateOpState(self):
        ''' Update the op state to on or off according to the on/off state of the outlet
        
        :return: the new opState
        '''
        if self.getState():
            self.setOpState(ControllerOpState.OK)
        else:
            self.setOpState(ControllerOpState.OFF)
        return

    def setState(self,state):
        '''set the current OpState
        
        :param state: The state of the control to set
        :return: True if the setting was successful 
        '''
        self._setControlState(state)
        self.updateState()
        #TODO: make this more robust?
        if self.getState() == state:
            return True
        else:
            return False
    
    def setOpState(self,state):
        self.opState=state
        
    def getOpState(self):
        return self.opState