#!/usr/bin/env python
"""  Ockle PDU and servers manager
Simple tester plugin that turns all servers on (subject to change)

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
import time
from plugins.ModuleTemplate import ModuleTemplate

class PowerTester(ModuleTemplate):
    ''' Simple tester plugin that turns all servers on (subject to change) '''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def run(self):
        self.debug("\n")
        
        self.mainDaemon.servers.allOff()
        time.sleep(1)
        self.mainDaemon.servers.initiateStartup()
                
    
        return

if __name__ == "__main__":
    a = PowerTester(None)