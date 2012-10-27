#!/usr/bin/env python
"""  Ockle PDU and servers manager
Dummy Tester
This tester can be set to always pass or fail

Created on Oct 27, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from TemplateTester import TemplateTester
import json

class Dummy(TemplateTester):
    ''' A simple ping test
    '''
    def __init__(self,name,testerConfigDict={},testerParams={}):
        TemplateTester.__init__(self,name, testerConfigDict, testerParams)
        self.state = json.loads(testerParams["succeed"])
        return
    
    def _test(self):
        '''Runs the test
        
        :return: Return True if succeeded
        '''
        return self.state
