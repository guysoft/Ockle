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
from networkTree.ServerNetworkFactory import ServerNetworkFactory
from networkTree.Exceptions import DependencyException
from pygraph.classes.exceptions import AdditionError

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
    
    def getServerDict(self):
        return self._getObjectDict("servers",self.mainDaemon.SERVERS_DIR)
    
    def getServerInfo(self,dataDict):
        ''' Get the data dict of a server
        @param dataDict: The data dict from the communication call, should contain the key "server"
        @return: the server information, empty dict if invalid request
        '''
        try:
            server = self.mainDaemon.servers.getServernode(dataDict["server"])
        except:
            return {} #no server found
        server.getName()
        outlets={}
        for outlet in server.getOutlets():
            outletIndex="outlet"+outlet.getName()
            outlets[outletIndex] ={} 
            outlets[outletIndex]["type"] = outlet.getOutletType()
            outlets[outletIndex]["OpState"] = outlet.getOpState()
            outlets[outletIndex]["state"] = outlet.getState()
            outlets[outletIndex]["data"] = outlet.getData()
            outlets[outletIndex]["name"] = outlet.getName()
            
        return {"Name" :  server.getName(),
                "OpState" : server.getOpState(),
                "outlets" : json.dumps(outlets),
                "StartAttempts" : server.getStartAttempts()
                }
    
    def switchOutlet(self,dataDict):
        ''' Swtich an outlet on or off
        @param dataDict: A dict with an entry for server, outlet and state
        @return: Empty dict for now
        '''
        #TODO: return a success of failed state, so we can move the switch back up in the GUI if failed
        serverName = dataDict["server"]
        outletName = dataDict["outlet"]
        
        outletState = dataDict["state"] == "on" 
        
        outlet = self.mainDaemon.servers.getServer(serverName).getOutletByName(outletName)
        outlet.setState(outletState)
        if outletState:
            outlet.setOpState(OutletOpState.forcedOn)
        else:
            outlet.setOpState(OutletOpState.forcedOff)
        return {}
    
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
        for outlet in returnValue.keys():
            returnValue[outlet]["doc"] = ""
        return {"serverOutlets" : json.dumps(returnValue)}
    
    def getAvailableServerTesters(self,server):
        returnValue = self._getAvailableServerObjs(server,"tester")
        for outlet in returnValue.keys():
            returnValue[outlet]["doc"] = ""
        return {"serverTesters" : json.dumps(returnValue)}
    
    def _getServerDependencyMap(self,serverName):
        ''' Returns a dict of available servers to be added as dependencies
        @param server: The current server we are looking at
        @return: A dict with the keys available, disabled and existing according to what is possible. The disabled value is the cycle caused by the dependency
        '''
        
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
                except DependencyException as e:
                    returnValue['available'].pop(possibleServer)
                    returnValue['disabled'][possibleServer] = e.list
                except AdditionError:
                    #Happens if dependency already exists
                    returnValue['existing'][possibleServer] = returnValue['available'].pop(possibleServer)
        return {"dependencyMap": json.dumps(returnValue)}
    
    def run(self):
        self.debug("\n")
        self.mainDaemon.communicationHandler.AddCommandToList("dotgraph",lambda dataDict: self.getDotGraph(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("ServerView",lambda dataDict: self.getServerInfo(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("getPDUDict",lambda dataDict: self.getPDUDict())
        self.mainDaemon.communicationHandler.AddCommandToList("getTesterDict",lambda dataDict: self.getTesterDict())
        self.mainDaemon.communicationHandler.AddCommandToList("getServerDict",lambda dataDict: self.getServerDict())
        self.mainDaemon.communicationHandler.AddCommandToList("switchOutlet",lambda dataDict: self.switchOutlet(dataDict))
        self.mainDaemon.communicationHandler.AddCommandToList("getAvailableServerOutlets",lambda dataDict: self.getAvailableServerOutlets(dataDict["server"]))
        self.mainDaemon.communicationHandler.AddCommandToList("getAvailableServerTesters",lambda dataDict: self.getAvailableServerTesters(dataDict["server"]))
        self.mainDaemon.communicationHandler.AddCommandToList("getServerDependencyMap",lambda dataDict: self._getServerDependencyMap(dataDict["server"]))
        return 

if __name__ == "__main__":
    a = CoreCommunicationCommands(None)