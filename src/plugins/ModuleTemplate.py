#!/usr/bin/env python
"""  Ockle PDU and servers manager
The basic plugin that that all other plugins extend

Created on Apr 26, 2012
@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from threading import Thread
from common.common import getINITemplate
import os.path
import json

class ModuleTemplate(Thread):
    ''' The basic plugin that that all other plugins must extend'''
    
    def __init__(self,MainDaemon):
        ''' constructor, runs at startup
        
        :param MainDaemon: a pointer to the Main Daemon instance'''
        Thread.__init__(self)
        self.mainDaemon = MainDaemon
        self.mainDaemon.debug("Loaded: " + self.__class__.__name__)
        return
    
    def run(self):
        ''' To be implamented by the plugin,
        The main thread of the damon, this function runs in its own thread '''
        return
    
    def getConfigVar(self,value):
        '''Get a value from the config ini for a plugin
        
        :param value - the value you want
        :return: the value from config.ini 
        '''
        try:
            return self.mainDaemon.config.get("plugins."+self.__class__.__name__, value)
        except:
            return self._loadConfigVariableTemplate(value)
        return
    
    def getConfigInt(self,value):
        '''Get a value from the config ini for a plugin
        
        :param value: The value you want to load
        :return: the value from config.ini 
        '''
        try:
            return self.mainDaemon.config.getint("plugins."+self.__class__.__name__, value)
        except:
            return int(self._loadConfigVariableTemplate(value))
        return
    
    def _loadConfigVariableTemplate(self,value):
        pluginName = self.__class__.__name__
        path = os.path.join("plugins",pluginName + ".ini")
        configDict = getINITemplate(path)
        return json.loads(configDict["plugins."+pluginName][value.lower()])[1] 
    
    def debug(self,message):
        '''Debug message for a module
        
        :param message: debug message 
        '''
        self.mainDaemon.debug(self.__class__.__name__ +": "+ str(message))
        return
    
    def stop(self):
        ''' Called to request the thread to terminate
        '''
        self._Thread__stop()
        return