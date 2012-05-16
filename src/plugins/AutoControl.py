#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to automatically start up and manage the servers

Created on May 16, 2012

@author: Guy Sheffer <guysoft at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)

from plugins.ModuleTemplate import ModuleTemplate

class AutoControl(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        ''' states'''
    
        return
    
    def run(self):
        #TODO: add if states normal
        self.debug("\n")
        
        for server in self.mainDaemon.servers.getSortedNodeList():
            self.startup(server)
            
        return
    
    def startup(self,server):
        return

if __name__ == "__main__":
    a = AutoControl(None)