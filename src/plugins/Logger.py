#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to log server and outlet information to a database

Created on Jul 5, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
import time

p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)

from plugins.ModuleTemplate import ModuleTemplate
from outlets.OutletTemplate import OutletOpState
from networkTree.ServerNode import ServerNodeOpState

class Logger(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.LOG_RESOLUTION = int(self.getConfigVar("LOG_RESOLUTION"))
        return
    
    def run(self):
        while True:
            self.appendToLog()
            time.sleep(self.LOG_RESOLUTION)
        return
    
    def appendToLog(self):
        return

if __name__ == "__main__":
    a = Logger(None)
