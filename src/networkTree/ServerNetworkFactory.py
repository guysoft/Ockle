#!/usr/bin/env python
""" Ockle PDU and servers manager
The server network factory
Goes over the ini files in etc and builds the server network

Created on May 10, 2012

@author: Guy Sheffer <guysoft at mail.huji.ac.il>
"""
from ConfigParser import SafeConfigParser
import os
import json

from networkTree.ServerNetwork import ServerNetwork
from networkTree.ServerNode import ServerNode
from common.common import loadConfig
from common.common import turpleList2Dict
from straight.plugin import load
from outlets.OutletTemplate import OutletTemplate

from common.Exceptions import OutletTypeNotFound

config,ETC_DIR = loadConfig()
class ServerNetworkFactory(object):
    '''
    A class to take the config file folder and turn it in to a server network
    '''
    def __init__(self):
        '''
        Constructor
        '''
        return
    def buildNetwork(self,config_path):
        config,ETC_DIR = loadConfig()
        
        self.servers=ServerNetwork()
        
        #build servers
        SERVER_DIR = config.get('main', 'SERVER_DIR')
        serverConfigPath = os.path.join(ETC_DIR,SERVER_DIR)
        serverConfigFileList = os.listdir(serverConfigPath)
        for serverConfigFile in serverConfigFileList:
            serverConfigFile = os.path.join(serverConfigPath,serverConfigFile)
            serverConfig = SafeConfigParser()
            serverConfig.read(serverConfigFile)
            server = serverConfig.get('server', 'name')
            
            #Handle a list or single string outlet
            outlets = serverConfig.get('server', 'outlets')
            if outlets.startswith("["):
                outlets = json.loads(serverConfig.get("server","outlets"))
            else:
                outlets=[outlets]
            outletList=[]
            for outlet in outlets:
                outletList.append(self.__makeOutlet(serverConfig,outlet,serverConfigPath))
               
            self.servers.addServer(ServerNode(server,outletList))
        
        #add dependencies to our server forest
        for serverConfigFile in serverConfigFileList:
            serverConfigFile = os.path.join(serverConfigPath,serverConfigFile)
            serverConfig = SafeConfigParser()
            serverConfig.read(serverConfigFile)
            
            server = serverConfig.get('server', 'name')
            
            #sanitize input
            if serverConfig.get("server","dependencies") != "":    
                dependencies = json.loads(serverConfig.get("server","dependencies"))
            else:
                dependencies=[]
            
            for dependency in dependencies:
                self.servers.addDependency(server, dependency)
        return self.servers
    
    def __makeOutlet(self,serverConfig,outlet,serverConfigPath):
        ''' Make an outlet from the config file path of an outlet, and the required socket
        @param outletConfigPath config ini path to the socket
        @param outlet a string to get the outlet section
        @returns an outlet type socket
        '''
        
        #get server specific config for outlet (socket number etc)
        outletParams = turpleList2Dict(serverConfig.items(outlet))
        
        #get outlet type so we can pull its config data
        outletConfig=serverConfig.get(outlet, "outlet")
        OUTLET_DIR = config.get('main', 'OUTLET_DIR')
        outletConfigPath = os.path.join(ETC_DIR,OUTLET_DIR,outletConfig + ".ini")
        outletConfig = SafeConfigParser()
        
        #Crate the outlet with server params and outlet config 
        outletConfig.read(outletConfigPath)
        outletConfigDict={}
        for section in outletConfig.sections(): 
            outletConfigDict[section] = turpleList2Dict(outletConfig.items('outlet'))
        
        #todo, find from type the kind of outlet
        outlets = load(OUTLET_DIR,subclasses=OutletTemplate)
        outletType = outletConfigDict['outlet']['type']
        for outlet in outlets:
            if outlet.__name__ == outletType:
                return outlet(outletConfigDict,outletParams)
        raise OutletTypeNotFound(outletConfigPath,outletType)
    