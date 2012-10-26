#!/usr/bin/env python
"""  Ockle PDU and servers manager
The basic plugin that that all other plugins extend

Created on Apr 26, 2012
@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from threading import Thread

from networkTree.ServerNetworkFactory import ServerNetworkFactory
from networkTree.Exceptions import DependencyException
from pygraph.classes.exceptions import AdditionError
from common.common import iniToDict
import os.path

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
    
    def stop(self):
        ''' Called to request the thread to terminate
        '''
        self._Thread__stop()

        return 
    
    ### Common Functions ###
    #Add here things that we want all plugins to have access to
    
    
    def _getServerDependencyMap(self,serverName):   
        factory = ServerNetworkFactory(self.mainDaemon)
        serversNetwork=factory.buildNetwork(self.mainDaemon.ETC_DIR)
        
        returnValue = {}
        returnValue['available'] = {}
        returnValue['disabled'] = {}
        returnValue['existing'] = {}
        
        for possibleServer in serversNetwork.getSortedNodeListIndex():
            if possibleServer != serverName:
                returnValue['available'][possibleServer] = iniToDict(os.path.join(self.mainDaemon.SERVERS_DIR,possibleServer + ".ini"))["server"]["comment"]
                try:
                    serversNetwork.addDependency(serverName, possibleServer)
                    
                    #if all went well, remove dependency
                    try:
                        serversNetwork.removeDependency( possibleServer,serverName )
                    except ValueError:
                        pass
                except DependencyException as e:
                    returnValue['available'].pop(possibleServer)
                    returnValue['disabled'][possibleServer] = e.list
                except AdditionError:
                    #Happens if dependency already exists
                    returnValue['existing'][possibleServer] = returnValue['available'].pop(possibleServer)

        
        return returnValue