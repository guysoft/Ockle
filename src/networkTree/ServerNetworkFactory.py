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
from controllers.ControllerTemplate import ControllerTemplate

from common.Exceptions import OutletTypeNotFound
from common.Exceptions import TesterTypeNotFound
from common.Exceptions import ControllerTypeNotFound
from networkTree.Exceptions import DependencyException
from ConfigParser import NoOptionError

config,ETC_DIR = loadConfig()

TESTERS_PACKAGE="testers"
OUTLETS_PACKAGE="outlets"
CONTROLLERS_PACKAGE="controllers"

class ServerNetworkFactory(object):
    '''
    A class to take the config file folder and turn it in to a server network
    @param MainDaemon: the singletron, only used for debug output
    '''
    def __init__(self,MainDaemon,reportDependencyexceptions=True):
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
            
            def buildServerObj(objNames,builderCallback):
                ''' Parse the serverObj field
                @param objNames: the name of the field we are parsing
                @param builderCallback: The function that takes the server config and name, building the object
                @return: A list of the server objects 
                '''
                #Handle a list or single string outlet
                try:
                    outlets = serverConfig.get('server', objNames)
                except NoOptionError:
                    outlets = "[]" 
                    
                if outlets.startswith("["):
                    outlets = json.loads(outlets)
                else:
                    outlets=[outlets]
                outletList=[]
                for outlet in outlets:
                    outletList.append(builderCallback(serverConfig,outlet,serverConfigPath))
                return outletList
            
            outletList = buildServerObj('outlets',self.__makeOutlet)
            testerList = buildServerObj('tests',self.__makeTester)
            controlList = buildServerObj('controls',self.__makeControl)
            
                        
            #Make the server with the outlets and testers
            self.servers.addServer(ServerNode(server,outletList,testerList,controlList))
        
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
                try:
                    self.servers.addDependency(server, dependency)
                except DependencyException as e:
                    if DependencyException:
                        self.mainDaemon.debug(e.msg +":" + str(e.list))
                    raise e
        return self.servers
    
    def __makeServerObj(self,objGeneratorName,objGeneratorFolder,objGeneratorPackageName,objGeneratorSubclass,objGeneratorNotFoundException,serverConfig,objSection,serverConfigPath):
        ''' Make an objSection from the config file path of an objSection, and the required socket
        @param serverConfig config ini path to the socket
        @param objSection a string to get the objSection objSection
        @param serverConfigPath:
        @returns an objSection type socket
        '''
        
        #get server specific config for objSection (socket number etc)
        outletParams = turpleList2Dict(serverConfig.items(objSection))
        
        #get objSection type so we can pull its config data
        outletConfig=serverConfig.get(objSection, objGeneratorName)
        outletConfigPath = os.path.join(objGeneratorFolder,outletConfig + ".ini")
        outletConfig = SafeConfigParser()
        
        #Create the objSection with server params and objSection config 
        outletConfig.read(outletConfigPath)
        outletConfigDict={}
        self.mainDaemon.debug("Loading:"+str(outletConfigPath))
        for objSection in outletConfig.sections(): 
            outletConfigDict[objSection] = turpleList2Dict(outletConfig.items(objGeneratorName))
        
        #Find from type the kind of objSection
        outlets = load(objGeneratorPackageName,subclasses=objGeneratorSubclass)
        outletType = outletConfigDict[objGeneratorName]['type']
        for outletClass in outlets:
            if outletClass.__name__ == outletType:
                return outletClass(objSection,outletConfigDict,outletParams)
        raise objGeneratorNotFoundException(outletConfigPath,outletType)
    
    def _getClassDictIndex(self,package,subclass):
        ''' Get a list of modules
        @param package: The package path to search
        @param subclass: The subclass to search for 
        @return: A list of the names of the classes ''' 
        classTypeDict = {}
        outlets = load(package,subclasses=subclass)
        for outletClass in outlets:
            if not outletClass.__name__ in classTypeDict:
                classTypeDict[outletClass.__name__] = outletClass.__doc__
        return classTypeDict
    
    def getOutletsDictIndex(self):
        return self._getClassDictIndex(OUTLETS_PACKAGE,OutletTemplate)

    def getTestersDictIndex(self):
        return self._getClassDictIndex(TESTERS_PACKAGE,TemplateTester)
    
    def getControllersDictIndex(self):
        return self._getClassDictIndex(CONTROLLERS_PACKAGE,ControllerTemplate)
    
    def __makeOutlet(self,serverConfig,outlet,serverConfigPath):
        return self.__makeServerObj("pdu",self.mainDaemon.OUTLETS_DIR,OUTLETS_PACKAGE,OutletTemplate,OutletTypeNotFound,serverConfig,outlet,serverConfigPath)
    
    def __makeTester(self,serverConfig,tester,serverConfigPath):
        return self.__makeServerObj("tester",self.mainDaemon.TESTERS_DIR,TESTERS_PACKAGE,TemplateTester,TesterTypeNotFound,serverConfig,tester,serverConfigPath)
    
    def __makeControl(self,serverConfig,control,serverConfigPath):
        return self.__makeServerObj("controller",self.mainDaemon.CONTROLLERS_DIR,CONTROLLERS_PACKAGE,ControllerTemplate,ControllerTypeNotFound,serverConfig,control,serverConfigPath)
    
    