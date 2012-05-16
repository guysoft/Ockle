#!/usr/bin/env python
""" Ockle PDU and servers manager
Template for an outlet object that all other outlets extend
Created on Mar 7, 2012

@author: Guy Sheffer <guysoft at mail.huji.ac.il>
"""
class OutletTemplate(object):
    '''
    
    @param outletConfigDict: a dictionary with the params specified in the ini config file, sections. Its a dict of sections with a dict of variables
    @param outletParams: A dictionary of the server-specific params specified in the outlet section on the server config file
    '''
    def __init__(self,outletConfigDict={},outletParams={}):
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
        