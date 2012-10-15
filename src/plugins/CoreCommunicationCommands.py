#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to add a bunch of basic communication commands

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
from plugins.ModuleTemplate import ModuleTemplate
import pygraph.readwrite.dot
from common.common import iniToDict

from collections import OrderedDict

from outlets.OutletTemplate import OutletOpState
from controllers.ControllerTemplate import ControllerOpState

import json

class CoreCommunicationCommands(ModuleTemplate):
    ''' Add of basic communication commands'''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def getDotGraph(self,dataDict):
        dot = pygraph.readwrite.dot.write(self.mainDaemon.servers.graph,False) 
        return {"Dot" :  dot}
    
    def _getObjectDict(self,returnVariable,objectFolder):
        #Sanitize if the folder does not exist
        if not os.path.isdir(objectFolder):
            return {returnVariable : "{}"}
        
        returnValue = {}
        for obj in os.listdir(objectFolder):
            obj = os.path.join(objectFolder,obj)
            objectDict = iniToDict(obj)
            objName = os.path.splitext(os.path.basename(obj))[0]
            returnValue[objName] = objectDict
        return {returnVariable : json.dumps(returnValue)}
    
    def getPDUDict(self):
        return self._getObjectDict("pdus",self.mainDaemon.OUTLETS_DIR)
    
    def getTesterDict(self):
        return self._getObjectDict("testers",self.mainDaemon.TESTERS_DIR)
    
    def getControllerDict(self):
        return self._getObjectDict("controllers",self.mainDaemon.CONTROLLERS_DIR)
        
    def getServerDict(self):
        return self._getObjectDict("servers",self.mainDaemon.SERVERS_DIR)
    
    def ServerView(self,dataDict):
        ''' Get the data dict of a server
        @param dataDict: The data dict from the communication call, should contain the key "server"
        @return: the server information, empty dict if invalid request
        '''
        try:
            server = self.mainDaemon.servers.getServernode(dataDict["server"])
        except:
            return {} #no server found
        server.getName()
        
        def getServerObjInfo(obj,objList,test=False):
            objs={}
            for outlet in objList:
                outletIndex=obj +outlet.getName()
                objs[outletIndex] ={} 
                #outlets[outletIndex]["type"] = outlet.getOutletType()
                objs[outletIndex]["OpState"] = outlet.getOpState()
                if not test:
                    objs[outletIndex]["state"] = outlet.getState()
                    objs[outletIndex]["data"] = outlet.getData()
                objs[outletIndex]["name"] = outlet.getName()
            return objs
        outlets = getServerObjInfo("outlet",server.getOutlets())
        controls = getServerObjInfo("control",server.getControls())
        tests = getServerObjInfo("test",server.getTests(),True)
         
        return {"Name" :  server.getName(),
                "OpState" : server.getOpState(),
                "outlets" : json.dumps(outlets),
                "controls" : json.dumps(controls),
                "tests" : json.dumps(tests),
                "StartAttempts" : server.getStartAttempts()
                }
    
    def switchOutlet(self,dataDict):
        ''' Swtich an outlet on or off
        @param dataDict: A dict with an entry for server, outlet and state
        @return: The opStatus of the outlet
        '''
        serverName = dataDict["server"]
        outletName = dataDict["obj"]
        
        outletState = dataDict["state"] == "on" 
        
        outlet = self.mainDaemon.servers.getServer(serverName).getOutletByName(outletName)
        outlet.setState(outletState)
        if outletState:
            outlet.setOpState(OutletOpState.forcedOn)
        else:
            outlet.setOpState(OutletOpState.forcedOff)
        return {"status" : outlet.getOpState()}
    
    #TODO: remove repition: same as switchOutlet, but we need to change getOutletByName to something we can pass
    def switchControl(self,dataDict):
        ''' Swtich an outlet on or off
        @param dataDict: A dict with an entry for server, outlet and state
        @return: The opStatus of the control
        '''
        serverName = dataDict["server"]
        outletName = dataDict["obj"]
        
        outletState = dataDict["state"] == "on" 
        
        outlet = self.mainDaemon.servers.getServer(serverName).getControlByName(outletName)
        outlet.setState(outletState)
        if outletState:
            outlet.setOpState(ControllerOpState.forcedOn)
        else:
            outlet.setOpState(ControllerOpState.forcedOff)
        return {"status" : outlet.getOpState()}
    
    def runTest(self,dataDict):
        ''' Run a test
        @param dataDict: A dict with an entry for server, outlet and state
        @return: Empty dict for now
        '''
        serverName = dataDict["server"]
        testName = dataDict["obj"]
        
        test = self.mainDaemon.servers.getServer(serverName).getTestByName(testName)
        test.test()
        return {"status" : test.getOpState()}
    
    def _getAvailableServerObjs(self,server,obj):
        returnValue = OrderedDict()
        serverPath = os.path.join(self.mainDaemon.SERVERS_DIR,server + ".ini")
        serverDict = iniToDict(serverPath)
        
        #Get checked items in order
        try:
            for objItem in json.loads(serverDict["server"][obj + "s"]):
                returnValue[objItem] = serverDict[objItem]
        except:
            pass
            
        
        serverDict.pop("server")
        
        for section in serverDict.keys():
            if obj in serverDict[section] and not section in returnValue:  #we have an outlet/tester
                returnValue[section] = serverDict[section]
        return returnValue
    
    def getAvailableServerOutlets(self,server):
        returnValue = self._getAvailableServerObjs(server,"pdu")
        return {"serverOutlets" : json.dumps(returnValue)}
    
    def getAvailableServerTesters(self,server):
        returnValue = self._getAvailableServerObjs(server,"tester")
        return {"serverTesters" : json.dumps(returnValue)}
    
    def getAvailableServerControls(self,server):
        returnValue = self._getAvailableServerObjs(server,"controller")
        return {"serverControls" : json.dumps(returnValue)}
    
    def getServerDependencyMap(self,serverName):
        ''' Returns a dict of available servers to be added as dependencies
        @param server: The current server we are looking at
        @return: A dict with the keys available, disabled and existing according to what is possible. The disabled value is the cycle caused by the dependency
        '''
        return {"dependencyMap": json.dumps(self._getServerDependencyMap(serverName))}
         
    
    def run(self):
        self.debug("\n")
        self.mainDaemon.communicationHandler.AddCommandToList("dotgraph",lambda dataDict: self.getDotGraph(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("ServerView",lambda dataDict: self.ServerView(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("getPDUDict",lambda dataDict: self.getPDUDict())
        self.mainDaemon.communicationHandler.AddCommandToList("getTesterDict",lambda dataDict: self.getTesterDict())
        self.mainDaemon.communicationHandler.AddCommandToList("getControllerDict",lambda dataDict: self.getControllerDict())
        self.mainDaemon.communicationHandler.AddCommandToList("getServerDict",lambda dataDict: self.getServerDict())
        self.mainDaemon.communicationHandler.AddCommandToList("switchOutlet",lambda dataDict: self.switchOutlet(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("switchControl",lambda dataDict: self.switchControl(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("runTest",lambda dataDict: self.runTest(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("getAvailableServerOutlets",lambda dataDict: self.getAvailableServerOutlets(dataDict["server"]))
        self.mainDaemon.communicationHandler.AddCommandToList("getAvailableServerTesters",lambda dataDict: self.getAvailableServerTesters(dataDict["server"]))
        self.mainDaemon.communicationHandler.AddCommandToList("getAvailableServerControls",lambda dataDict: self.getAvailableServerControls(dataDict["server"]))
        self.mainDaemon.communicationHandler.AddCommandToList("getServerDependencyMap",lambda dataDict: self.getServerDependencyMap(dataDict["server"]))
        return 

if __name__ == "__main__":
    a = CoreCommunicationCommands(None)