#!/usr/bin/env python
""" Ockle PDU and servers manager
Handle communication massages from a listner plugin

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from CommunicationMessage import MessageServerSend
from CommunicationMessage import MessageServerError
from common import trimOneObjectListsFromDict

class CommunicationHandler(object):
    def __init__(self,mainDaemon):
        '''
        Iinitiate an instance of a communication handler system.
        @param mainDaemon: The main Daemon
        @param listenerPlugin: The plugin that listens for incoming connections (Mostly used to display related debug message)
        '''
        self.mainDaemon = mainDaemon
        #Command dictionary. holds a command name and the function it runs
        self.commandDict={}
        
        self.AddCommandToList("listcommands", lambda dataDict: self.listCommands(dataDict))
        return
    
    def listCommands(self,dataDict):
        '''
        A command to list all available commands on the communication server
        '''
        docCommandsDict = {}
        for command in self.commandDict.keys():
            doc =  self.commandDict[command].__doc__
            if doc == None:
                doc = ""
            docCommandsDict[command] = doc 
        return MessageServerSend("listcommands",docCommandsDict)
    
    def listPlugins(self,dataDict):
        ''' A command to list all the avilable plugins to the Ockle installation
        '''
        plugins = load(PLUGIN_DIR,subclasses=ModuleTemplate)
        return
    
    def handleMessage(self,message):
        '''
        Receives a message class type, and returns the appropriate response
        @param message: The message class we received
        @return: A message class response 
        '''
        #print message.__class__.__name__
        command = message.getCommand()
        if not command in self.commandDict:
            return MessageServerError(command)#TODO: return an unknown command Error message
        handleFunction = self.commandDict[command]
        dataDict = message.getDataDict()
        if dataDict != None:
            dataDict = trimOneObjectListsFromDict(dataDict)
        returnValue = handleFunction(message.getDataDict())
        
        returnMessage = MessageServerSend(command,returnValue)
        print returnMessage.toxml()
        return returnMessage
    
    def AddCommandToList(self,command,function):
        '''Used by plugins to add an ability to handle a message on the server
        @param command: The command to be called
        @param function: a callback to a function that receives a dict of the data to process 
        '''
        self.commandDict[command] = function
        return