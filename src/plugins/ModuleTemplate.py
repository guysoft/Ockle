#!/usr/bin/env python
"""  Ockle PDU and servers manager
The basic plugin that that all other plugins extend

Created on Apr 26, 2012
@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from threading import Thread

class ModuleTemplate(Thread):
    def __init__(self,MainDaemon):
        Thread.__init__(self)
        self.mainDaemon = MainDaemon
        self.mainDaemon.debug("Loaded: " + self.__class__.__name__)
        
        return
    def run(self):
        return
    
    def getConfigVar(self,value):
        '''Get a value from the config ini for a plugin
        @param value - the value you wnat
        @return: the value from config.ini 
        '''
        return self.mainDaemon.config.get("plugins."+self.__class__.__name__, value)
    
    def getConfigInt(self,value):
        '''Get a value from the config ini for a plugin
        @param value - the value you wnat
        @return: the value from config.ini 
        '''
        return self.mainDaemon.config.getint("plugins."+self.__class__.__name__, value)
    
    def debug(self,message):
        '''Debug message for a module
        @param message: debug message 
        '''
        self.mainDaemon.debug(self.__class__.__name__ +": "+ str(message))
        return