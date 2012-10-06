#!/usr/bin/env python
""" Ockle PDU and servers manager
A dummy controller, useful for testing

Created on Oct 05, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from controllers.ControllerTemplate import ControllerTemplate
   
class Dummy(ControllerTemplate):
    def __init__(self,name,controllerConfigDict={},controllerParams={}):
        ControllerTemplate(name,controllerConfigDict={},controllerParams={})
        
        self.state=False
        return
    
    def updateData(self):
        pass
    
    def setSate(self,state):
        self.state=True
        return