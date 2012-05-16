#!/usr/bin/env python
"""  Ockle PDU and servers manager
Ping Tester
Test if we can ping a hostname

Created on Apr 25, 2012

@author: Guy Sheffer <guysoft at mail.huji.ac.il>
"""
import subprocess
import os
from TemplateTester import TemplateTester

def ping(ip):
    '''
    subprocess ping
    '''
    ping = subprocess.Popen(["ping", "-c", "2", "-w", "1", ip], shell=None,stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    ping.wait()
    if ping.returncode != 1:
        #print ping.returncode, "ERROR: failed to ping host. Please check."
        return False
    else:
        return True

class PingTester(TemplateTester):
    def __init__(self,daemon,hostname):
        self.daemon = daemon
        self.hostname = hostname
        return
    
    def test(self):
        '''
        Runs the test
        '''
        return ping(self.hostname)
