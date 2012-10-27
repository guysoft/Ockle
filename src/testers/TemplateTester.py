#!/usr/bin/env python
"""  Ockle PDU and servers manager
This is a template module that all other test modules extend

Created on Apr 25, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

class TesterOpState():
    INIT=-1# Did not start yet
    SUCCEEDED="SUCCEEDED" #: Test has succeeded
    FAILED="FAILED"       #: Test has failed
    

class TemplateTester(object):
    def __init__(self,name,testerConfigDict,testerParams):
        self.opState = TesterOpState.INIT
        self.setName(name)
        return
    
    def getName(self):
        return self.name
    
    def setName(self,name):
        self.name = name
    
    def _test(self):
        '''To be implemented by the child, runs the test
        
        :return: Return True if succeeded
        '''
        pass
    
    def runTest(self):
        ''' Use this method to run a test, updates the OpState
        ''' 
        if self._test():
            self.setOpState(TesterOpState.SUCCEEDED)
        else:
            self.setOpState(TesterOpState.FAILED)
    
    def setOpState(self,state):
        self.opState=state
    def getOpState(self):
        return self.opState