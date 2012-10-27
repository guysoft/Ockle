#!/usr/bin/env python
"""  Ockle PDU and servers manager
Simple example plugin to demonstrate the plugin framework

Created on Oct 27, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import time

from plugins.ModuleTemplate import ModuleTemplate
class TimerPluginExample(ModuleTemplate):
    ''' Example plugin that just sends to debug a message every X seconds, as defined in its config var
    '''
    
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.wait_time = self.getConfigInt("WAIT_TIME")
        
    def run(self):
        while self.mainDaemon.running:
            self.debug("I am a test plugin")
            time.sleep(self.wait_time)