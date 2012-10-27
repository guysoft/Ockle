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

def ping(ip):
    ''' subprocess ping
    '''
    ping = subprocess.Popen(["ping", "-c", "2", "-w", "1", ip], shell=None,stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    ping.wait()
    if ping.returncode != 0:
        #print ping.returncode, "ERROR: failed to ping host. Please check."
        return False
    else:
        return True

class Ping(TemplateTester):
    ''' A simple ping test
    '''
    def __init__(self,name,testerConfigDict={},testerParams={}):
        TemplateTester.__init__(self,name, testerConfigDict, testerParams)
        self.hostname = testerParams["hostname"]
        return
    
    def _test(self):
        '''Runs the test
        
        :return: Return True if succeeded
        '''
        state = ping(self.hostname)
        return state
