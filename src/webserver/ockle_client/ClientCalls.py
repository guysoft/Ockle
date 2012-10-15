"""  Ockle PDU and servers manager
Client calls to the Ockle server

Created on Apr 25, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..')
print p
sys.path.insert(0, p)

import socket
from ConfigParser import SafeConfigParser
from lxml import html
from common.CommunicationMessage import MessageClientSend
from common.CommunicationMessage import Message
from common.common import trimOneObjectListsFromDict
from common.common import getINIstringtoDict
from common.common import getINITemplate
from common.common import mergeDicts
from common.Exceptions import ParsingTemplateException

import json
from collections import OrderedDict

config = SafeConfigParser()
ETC_DIR= os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','..',"etc")
#print os.path.join(ETC_DIR,"config.ini")
config.read(os.path.join(ETC_DIR,"config.ini"))
PORT = config.getint('plugins.SocketListener', 'LISTENER_PORT')
SOCKET_TIMEOUT = config.getint('plugins.SocketListener', 'SOCKET_TIMEOUT')
OCKLE_SERVER_HOSTNAME="127.0.0.1"

def getDataFromServer(command,paramsDict={},noReturn=False):
    ''' Send a command to the Ockle server, and return the responce dict 
    @param command: The command to send
    @param paramsDict: the dictionary that is sent with command arguments
    @param noReturn: Should we not expect a reply. Used in cases were we want to restart the Ockle server
    @return: A dict with the response data, None if we failed to connect
    '''
    returnValue=""
    def recv(sendMessage,noReturn):
        ''' Loop to receive a message'''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(SOCKET_TIMEOUT)
        n = ''
        data = ''
        try:
            s.connect((OCKLE_SERVER_HOSTNAME, PORT))
            s.sendall(str(len(sendMessage)) +":" +sendMessage)
            
            if noReturn:
                s.close()
                return None,None
            else:
                while 1:
                    c = s.recv(1)
                    if c == ':':
                        break
                    n += c
    
                n = int(n)
                while n > 0:
                    data += s.recv(n)
                    n -= len(data)
                s.close()
                print data
                return None, data
        except socket.error as e:
            s.close()
            return e, None
        
    a = MessageClientSend(command,paramsDict)
    m, data = recv(a.toxml(),noReturn)
    #print 'recv: ', 'error=', m, 'data=', data
    if data:
        messageGen = Message()
        print "got the following data:"
        print data
        reply = messageGen.parse(data)
        returnValue= reply.getDataDict()
        if type(returnValue) == dict:
            returnValue = trimOneObjectListsFromDict(returnValue)

    return returnValue

def _getDataFromServerWithFail(command,dataDict,errorClass):
    ''' Gets data from server, if fails returns an empty dict
    '''
    response = getDataFromServer(command,dataDict)
    if response == None:
        return errorClass
    else:
        return response

def getServerTree():
    ''' Get a server tree status from the Ockle server, and return a dict ready
    to be parsed by a pyramid view '''
    response = getDataFromServer("dotgraph",{"yay":"yay"})
    if response == None:
        return "Error connecting to Ockle server"
    else:
        return html.fromstring(response["Dot"]).text 

def getServerView(serverName):
    return _getDataFromServerWithFail("ServerView",{"server":serverName},"Error connecting to Ockle server - Can't get server Info")

def getAutoControlStatus():
    return _getDataFromServerWithFail("getAutoControlStatus",{},{"status":"N/A"})

def setAutoControlStatus(dataDict):
    return _getDataFromServerWithFail("setAutoControlStatus",dataDict,{"status":"N/A"}) 

def getINIFile(iniPath):
    return getDataFromServer("getINIFile",{"Path":iniPath})["File"]

def getAvailablePluginsList():
    return _getDataFromServerWithFail("getAvailablePluginsList",{},{})

def setINIFile(iniPath,iniDict):
    return getDataFromServer("setINIFile",{"Path":iniPath, "iniDict" : json.dumps(iniDict)})

def deleteINIFile(iniPath):
    return getDataFromServer("deleteINIFile",{"Path":iniPath})

def deleteINISection(section,iniPath):
    return getDataFromServer("deleteINISection",{"Path":iniPath, "Section": section})

def restartOckle():
    return getDataFromServer("restart",{},True)

def getPDUDict():
    reply = json.loads(getDataFromServer("getPDUDict")["pdus"])
    return reply

def getTesterDict():
    reply = json.loads(getDataFromServer("getTesterDict")["testers"])
    return reply

def getControllerDict():
    reply = json.loads(getDataFromServer("getControllerDict")["controllers"])
    return reply

def getServerDict():
    reply = json.loads(getDataFromServer("getServerDict")["servers"])
    return reply

def loadINIFileTemplate(templatePaths):
    ''' Load an INI file and template data so it would display correctly.
    Is called with loadINIFileConfig(configPath)
    @param templatesPaths: A path, or list of paths relative to 'src/config'
    @return: A dicts of the template
    '''
    if type(templatePaths) == str or type(templatePaths) == unicode:
        templatePaths= [templatePaths]

    iniTemplate = getINITemplate(templatePaths)
    
    try:
        for section in iniTemplate.keys():
            for item in iniTemplate[section].keys():
                print iniTemplate[section][item]
                iniTemplate[section][item] = json.loads(iniTemplate[section][item])
    except ValueError:
        raise ParsingTemplateException()
        
    return iniTemplate

def loadINIFileConfig(configPath):
    ''' Get the config on an ini file
    @param configPath: the path to the config relative to etc
    @return: a dict of the config
    '''
    iniString = getINIFile(configPath)
    INIFileDict = getINIstringtoDict(iniString)
    return INIFileDict

def getAvailablePDUsList():
    response = getDataFromServer("getAvailablePDUsList")
    if response == None:
        return {}
    else:
        return json.loads(response["PDUs"])
    return

def getAvailableTestersList():
    response = getDataFromServer("getAvailableTestersList")
    if response == None:
        return {}
    else:
        return json.loads(response["Testers"])
    return

def getAvailableControllersList():
    response = getDataFromServer("getAvailableControllersList")
    if response == None:
        return {}
    else:
        return json.loads(response["Controllers"])
    return

def getAvailableServerOutlets(server):
    response = getDataFromServer("getAvailableServerOutlets",{"server": server})
    if response == None:
        return {}
    else:
        outletDict =  json.loads(response["serverOutlets"],object_pairs_hook=OrderedDict)
        for key in outletDict.keys():
            outletDict[key] = ""
    return outletDict

def getAvailableServerTesters(server):
    response = getDataFromServer("getAvailableServerTesters",{"server": server})
    if response == None:
        return {}
    else:
        testerDict =  json.loads(response["serverTesters"],object_pairs_hook=OrderedDict)
        for key in testerDict.keys():
            testerDict[key] = ""
    return testerDict

def getAvailableServerControls(server):
    response = getDataFromServer("getAvailableServerControls",{"server": server})
    if response == None:
        return {}
    else:
        controlDict =  json.loads(response["serverControls"],object_pairs_hook=OrderedDict)
        for key in controlDict.keys():
            controlDict[key] = ""
    return controlDict

def getServerDependencyMap(server):
    response = getDataFromServer("getServerDependencyMap",{"server": server})
    if response == None:
        return {}
    else:
        depMap = json.loads(response["dependencyMap"])
        return mergeDicts(depMap["available"], depMap["existing"])

def serversDependent(server):
    response = getDataFromServer("getServerDependencyMap",{"server": server})
    if response == None:
        return {}
    else:
        depMap = json.loads(response["dependencyMap"])
        return depMap["disabled"].keys()

def getPDUFolder():
    return loadINIFileConfig("config.ini")['main']['outlet_dir']

def getTesterFolder():
    return loadINIFileConfig("config.ini")['main']['tester_dir']

def getControllerFolder():
    return loadINIFileConfig("config.ini")['main']['controller_dir']

def getServerFolder():
    return loadINIFileConfig("config.ini")['main']['server_dir']

def switchOutlet(dataDict):
    return getDataFromServer("switchOutlet",dataDict)

def switchControl(dataDict):
    return getDataFromServer("switchControl",dataDict)

def runTest(dataDict):
    return getDataFromServer("runTest",dataDict)