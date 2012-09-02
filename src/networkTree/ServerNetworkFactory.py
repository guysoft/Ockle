#!/usr/bin/env python
""" Ockle PDU and servers manager
The server network factory
Goes over the ini files in etc and builds the server network

Created on May 10, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
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
from testers.TemplateTester import TemplateTester

from common.Exceptions import OutletTypeNotFound
from common.Exceptions import TesterTypeNotFound

config,ETC_DIR = loadConfig()

TESTERS_PACKAGE="testers"
OUTLETS_PACKAGE="outlets"
class ServerNetworkFactory(object):
    '''
    A class to take the config file folder and turn it in to a server network
    @param MainDaemon: the singletron, only used for debug output
    '''
    def __init__(self,MainDaemon):
        '''
        Constructor
        '''
        self.mainDaemon = MainDaemon
        return
    
    def _getNameFromFilePath(self,path):
        return os.path.splitext(os.path.basename(path))[0]
    
    def buildNetwork(self,config_path):
        config,ETC_DIR = loadConfig()
        
        self.servers=ServerNetwork()
        
        #build servers
        SERVER_DIR = config.get('main', 'SERVER_DIR')
        serverConfigPath = os.path.join(ETC_DIR,SERVER_DIR)
        self.mainDaemon.debug("Loading:"+str(serverConfigPath))
        serverConfigFileList = os.listdir(serverConfigPath)
        for serverConfigFile in serverConfigFileList:
            serverConfigFile = os.path.join(serverConfigPath,serverConfigFile)
            serverConfig = SafeConfigParser()
            serverConfig.read(serverConfigFile)
            #server = serverConfig.get('server', 'name')
            server = self._getNameFromFilePath(serverConfigFile)
            
            #Handle a list or single string outlet
            outlets = serverConfig.get('server', 'outlets')
            if outlets.startswith("["):
                outlets = json.loads(serverConfig.get("server","outlets"))
            else:
                outlets=[outlets]
            outletList=[]
            for outlet in outlets:
                outletList.append(self.__makeOutlet(serverConfig,outlet,serverConfigPath))
                
            #Handle a list or single string testser
            testerList=[]
            if serverConfig.has_option('server', 'testers'):
                testers = serverConfig.get('server', 'testers')
                if testers.startswith("["):
                    testers = json.loads(serverConfig.get("server","testers"))
                else:
                    testers=[testers]
                for tester in testers:
                    testerList.append(self.__makeTester(serverConfig,tester,serverConfigPath))
            
            #Make the server with the outlets and testers
            self.servers.addServer(ServerNode(server,outletList,testerList))
        
        #add dependencies to our server forest
        for serverConfigFile in serverConfigFileList:
            serverConfigFile = os.path.join(serverConfigPath,serverConfigFile)
            serverConfig = SafeConfigParser()
            serverConfig.read(serverConfigFile)
            
            #server = serverConfig.get('server', 'name')
            server = self._getNameFromFilePath(serverConfigFile)
            
            #sanitize input
            if serverConfig.get("server","dependencies") != "":    
                dependencies = json.loads(serverConfig.get("server","dependencies"))
            else:
                dependencies=[]
            
            for dependency in dependencies:
                self.servers.addDependency(server, dependency)
        return self.servers
    
    #TODO fix nasty code repetition here with Test and make
    def __makeOutlet(self,serverConfig,outlet,serverConfigPath):
        ''' Make an outlet from the config file path of an outlet, and the required socket
        @param serverConfig config ini path to the socket
        @param outlet a string to get the outlet section
        @param serverConfigPath:
        @returns an outlet type socket
        '''
        
        #get server specific config for outlet (socket number etc)
        outletParams = turpleList2Dict(serverConfig.items(outlet))
        
        #get outlet type so we can pull its config data
        outletConfig=serverConfig.get(outlet, "outlet")
        outletConfigPath = os.path.join(self.mainDaemon.OUTLETS_DIR,outletConfig + ".ini")
        outletConfig = SafeConfigParser()
        
        #Create the outlet with server params and outlet config 
        outletConfig.read(outletConfigPath)
        outletConfigDict={}
        self.mainDaemon.debug("Loading:"+str(outletConfigPath))
        for section in outletConfig.sections(): 
            outletConfigDict[section] = turpleList2Dict(outletConfig.items('outlet'))
        
        #Find from type the kind of outlet
        outlets = load(OUTLETS_PACKAGE,subclasses=OutletTemplate)
        outletType = outletConfigDict['outlet']['type']
        for outletClass in outlets:
            if outletClass.__name__ == outletType:
                return outletClass(outlet,outletConfigDict,outletParams)
        raise OutletTypeNotFound(outletConfigPath,outletType)
    
    def _getClassDictIndex(self,package,subclass):
        ''' Get a list of modules
        @param package: The package path to search
        @param subclass: The subclass to search for 
        @return: A list of the names of the classes ''' 
        classTypeDict = {}
        outlets = load(OUTLETS_PACKAGE,subclasses=OutletTemplate)
        for outletClass in outlets:
            if not outletClass.__name__ in classTypeDict:
                classTypeDict[outletClass.__name__] = outletClass.__doc__
        return classTypeDict
    
    def getOutletsDictIndex(self):
        return self._getClassDictIndex(OUTLETS_PACKAGE,OutletTemplate)

    def getTestersDictIndex(self):
        return self._getClassDictIndex(TESTERS_PACKAGE,TemplateTester)
    
    def __makeTester(self,serverConfig,tester,serverConfigPath):
        ''' Make a tester from the config file path of a tester, and the required tester-server info
        @param testerConfigPath config ini path to the tester
        @param tester a string to get the tester section
        @param serverConfigPath: 
        @returns a tester type class
        '''
        
        #get server specific config for outlet (socket number etc)
        testerParams = turpleList2Dict(serverConfig.items(tester))
        
        #get tester type so we can pull its config data
        testerConfig=serverConfig.get(tester, "type")
        TESTER_DIR = config.get('main', 'TESTER_DIR') 
        testerConfigPath = os.path.join(ETC_DIR,TESTER_DIR,testerConfig + ".ini")
        testerConfig = SafeConfigParser()
        
        #Create the tester with server params and tester config 
        testerConfig.read(testerConfigPath)
        testerConfigDict={}
        for section in testerConfig.sections(): 
            testerConfigDict[section] = turpleList2Dict(testerConfig.items('tester'))
                        
        #Find from type the kind of tester
        testers = load(TESTERS_PACKAGE,subclasses=TemplateTester)
        testerType = testerConfigDict['tester']['type']
        for tester in testers:
            if tester.__name__ == testerType:
                return tester(testerConfigDict,testerParams)
        raise TesterTypeNotFound(testerConfigPath,testerType)
    