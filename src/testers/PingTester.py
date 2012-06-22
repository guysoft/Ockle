#!/usr/bin/env python
"""  Ockle PDU and servers manager
Ping Tester
Test if we can ping a hostname

Created on Apr 25, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import subprocess
import os
from TemplateTester import TemplateTester
from TemplateTester import TesterOpState

def ping(ip):
    '''
    subprocess ping
    '''
    ping = subprocess.Popen(["ping", "-c", "2", "-w", "1", ip], shell=None,stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    ping.wait()
    if ping.returncode != 0:
        #print ping.returncode, "ERROR: failed to ping host. Please check."
        return False
    else:
        return True

class Ping(TemplateTester):
    def __init__(self,testerConfigDict={},testerParams={}):
        TemplateTester.__init__(self, testerConfigDict, testerParams)
        self.hostname = testerParams["hostname"]
        return
    
    def test(self):
        '''
        Runs the test
        '''
        state = ping(self.hostname)
        if state:
            self.setOpState(TesterOpState.SUCCEEDED)
        else:
            self.setOpState(TesterOpState.FAILED)
        return state
