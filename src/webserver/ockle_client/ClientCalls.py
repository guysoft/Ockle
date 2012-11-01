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

PORT = 8088
try:
    PORT = config.getint('plugins.SocketListener', 'LISTENER_PORT')
except:
    pass

SOCKET_TIMEOUT = 5
try:
    SOCKET_TIMEOUT = config.getint('plugins.SocketListener', 'SOCKET_TIMEOUT')
except:
    pass
OCKLE_SERVER_HOSTNAME="127.0.0.1"

def getDataFromServer(command,paramsDict={},noReturn=False):
    ''' Send a command to the Ockle server, and return the responce dict
     
    :param command: The command to send
    :param paramsDict: the dictionary that is sent with command arguments
    :param noReturn: Should we not expect a reply. Used in cases were we want to restart the Ockle server
    :return: A dict with the response data, None if we failed to connect
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
    
    :param dataDict: the dictionary that is sent with command arguments
    :param errorClass: An instance of the object to return on fail
    
    :return: If the call succeeds then return the response, else return errorClass'''
    response = getDataFromServer(command,dataDict)
    if response == None:
        return errorClass
    else:
        return response

def getServerTree():
    ''' Get a server tree status from the Ockle server, and return a dict ready
    to be parsed by a pyramid view
     
    :return: a string with the dot graph'''
    response = getDataFromServer("dotgraph",{"yay":"yay"})
    if response == None:
        return "Error connecting to Ockle server"
    else:
        return html.fromstring(response["Dot"]).text 

def getServerView(serverName):
    ''' Get information of the server
    
    :param serverName: the server's name
    :return: a dict of string of the server's info'''
    return _getDataFromServerWithFail("ServerView",{"server":serverName},"Error connecting to Ockle server - Can't get server Info")

def getAutoControlStatus():
    ''' Get the status of the Auto Control plugin
    
    :return: A dict with a key 'status' holding the status of Auto Control'''
    return _getDataFromServerWithFail("getAutoControlStatus",{},{"status":"N/A"})

def setAutoControlStatus(dataDict):
    ''' Set the status of Auto Control 
    
    :param: dataDict: A dictionary with the field status which is either 'on' or 'off'
    :return: A dict similar to ::func: getAutoControlStatus'''
    return _getDataFromServerWithFail("setAutoControlStatus",dataDict,{"status":"N/A"}) 

def getINIFile(iniPath):
    ''' Get an INI file from Ockle's configuration
    
    :param iniPath: the path of the ini file starting from the 'etc' folder
    :return: A string with the ini file contents'''
    return getDataFromServer("getINIFile",{"Path":iniPath})["File"]

def getAvailablePluginsList():
    ''' Get the list of available plugins 
    
    :return: a dict with the plugin names as keys and the description as the value'''
    return _getDataFromServerWithFail("getAvailablePluginsList",{},{})

def setINIFile(iniPath,iniDict):
    ''' Set an INI file from Ockle's configuration
    
    :param iniPath: the path of the ini file starting from the 'etc' folder
    :param iniDict: a dict holding the structure of the ini file
    :return: A response from Ockle'''
    return getDataFromServer("setINIFile",{"Path":iniPath, "iniDict" : json.dumps(iniDict)})

def deleteINIFile(iniPath):
    ''' Delete an INI file from Ockle's configuration
    
    :param iniPath: the path of the ini file starting from the 'etc' folder
    :return: A response from Ockle'''
    return getDataFromServer("deleteINIFile",{"Path":iniPath})

def deleteINISection(section,iniPath):
    ''' Delete a section from an INI file in Ockle's configuration
    
    :param iniPath: the path of the ini file starting from the 'etc' folder
    :param section: the section to be deleted
    :return: A response from Ockle'''
    return getDataFromServer("deleteINISection",{"Path":iniPath, "Section": section})

def restartOckle():
    ''' Restart Ockle
    '''
    return getDataFromServer("restart",{},True)

def getPDUDict():
    ''' Get a dict of the current PDUs that are configured 
    
    :return: A dict of PDUs with the key as their name and the value as their description
    '''
    reply = json.loads(getDataFromServer("getPDUDict")["pdus"])
    return reply

def getTesterDict():
    ''' Get a dict of the current testers that are configured 
    
    :return: A dict of testers with the key as their name and the value as their description
    '''
    reply = json.loads(getDataFromServer("getTesterDict")["testers"])
    return reply

def getControllerDict():
    ''' Get a dict of the current controllers that are configured 
    
    :return: A dict of controllers with the key as their name and the value as their description
    '''
    reply = json.loads(getDataFromServer("getControllerDict")["controllers"])
    return reply

def getServerDict():
    ''' Get a dict of the current servers that are configured 
    
    :return: A dict of servers with the key as their name and the value as their description
    '''
    reply = json.loads(getDataFromServer("getServerDict")["servers"])
    return reply

def loadINIFileTemplate(templatePaths):
    ''' Load an INI file and template data so it would display correctly.
    Is called with loadINIFileConfig(configPath)
    
    :param templatesPaths: A path, or list of paths relative to 'src/config'
    :return: A dicts of the template
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
    ''' Get the currently available PDU types list
    
    :return: a sorted dict of PDUs, the key is the name of the PDU, and extra information is within the dict's value'''
    response = getDataFromServer("getAvailablePDUsList")
    if response == None:
        return {}
    else:
        return json.loads(response["PDUs"])
    return

def getAvailableTestersList():
    ''' Get the currently available testers type list
    
    :return: a sorted dict of testers, the key is the name of the tester, and extra information is within the dict's value'''
    response = getDataFromServer("getAvailableTestersList")
    if response == None:
        return {}
    else:
        return json.loads(response["Testers"])
    return

def getAvailableControllersList():
    ''' Get the currently available controller types list
    
    :return: a sorted dict of controllers, the key is the name of the controller, and extra information is within the dict's value'''
    response = getDataFromServer("getAvailableControllersList")
    if response == None:
        return {}
    else:
        return json.loads(response["Controllers"])
    return

def getAvailableServerOutlets(server):
    ''' Get the currently configured servers list
    
    :return: a sorted dict of servers, the key is the name of the server, and extra information is within the dict's value'''
    response = getDataFromServer("getAvailableServerOutlets",{"server": server})
    if response == None:
        return {}
    else:
        outletDict =  json.loads(response["serverOutlets"],object_pairs_hook=OrderedDict)
        for key in outletDict.keys():
            outletDict[key] = ""
    return outletDict

def getAvailableServerTesters(server):
    ''' Get the currently configured tests of a given server
    
    :return: a sorted dict of tests, the key is the name of the test, and extra information is within the dict's value'''
    response = getDataFromServer("getAvailableServerTesters",{"server": server})
    if response == None:
        return {}
    else:
        testerDict =  json.loads(response["serverTesters"],object_pairs_hook=OrderedDict)
        for key in testerDict.keys():
            testerDict[key] = ""
    return testerDict

def getAvailableServerControls(server):
    ''' Get the currently configured controls of a given server
    
    :return: a sorted dict of controls, the key is the name of the test, and extra information is within the dict's value'''
    response = getDataFromServer("getAvailableServerControls",{"server": server})
    if response == None:
        return {}
    else:
        controlDict =  json.loads(response["serverControls"],object_pairs_hook=OrderedDict)
        for key in controlDict.keys():
            controlDict[key] = ""
    return controlDict

def getServerAvilableDependencies(server):
    ''' Get a dict of the available dependencies that can be created for a server
     
     :param server: the server that is going to have the new dependency
     :return: A dict of servers and their description '''
    response = getDataFromServer("getServerDependencyMap",{"server": server})
    if response == None:
        return {}
    else:
        depMap = json.loads(response["dependencyMap"])
        return mergeDicts(depMap["available"], depMap["existing"])

def serversDependent(server):
    ''' Get a dict of servers that this server is dependent on
    
    :param server: The server to check for
    :return: a dict of servers that this server is dependent on'''
    response = getDataFromServer("getServerDependencyMap",{"server": server})
    if response == None:
        return {}
    else:
        depMap = json.loads(response["dependencyMap"])
        return depMap["disabled"].keys()

def getPDUFolder():
    ''' Get the configuration folder of all PDUs
    
    :return: A string of the folder name'''
    return loadINIFileConfig("config.ini")['main']['outlet_dir']

def getTesterFolder():
    ''' Get the configuration folder of all testers 
    
    :return: A string of the folder name'''
    return loadINIFileConfig("config.ini")['main']['tester_dir']

def getControllerFolder():
    ''' Get the configuration folder of all controllers 
    
    :return: A string of the folder name'''
    return loadINIFileConfig("config.ini")['main']['controller_dir']

def getServerFolder():
    ''' Get the configuration folder of all servers 
    
    :return: A string of the folder name'''
    return loadINIFileConfig("config.ini")['main']['server_dir']

def setServer(dataDict):
    ''' Set a server on or off 
    
    :param dataDict: A dict with two keys, one with the key 'server' which holds the server name in its value, and another with the key 'state' where its value is wither 'on' or 'off' 
    :return: A dict with the key 'status' containing a string reply from Ockle'''
    return getDataFromServer("setServer",dataDict)

def switchNetwork(dataDict):
    ''' A master command to turn all the servers on the network on or off
    
    :param dataDict: a dict with the key 'state' that has a string 'true' or 'false'
    :return: a dict with the key 'status' with a string reply from Ockle
    '''
    return _getDataFromServerWithFail("switchNetwork",dataDict,{"status":"N/A"}) 

def switchOutlet(dataDict):
    ''' Switch a server outlet on or off 
    
    :param dataDict: a dict holding three keys: 'server' key for the server's name, an 'obj' key for the outlet's name and the 'state' key with a string 'on' or 'off'
    :returns: the OpState of the outlet
    '''
    return getDataFromServer("switchOutlet",dataDict)

def switchControl(dataDict):
    ''' Switch a server control on or off 
    
    :param dataDict: a dict holding three keys: 'server' key for the server's name, an 'obj' key for the control's name and the 'state' key with a string 'on' or 'off'
    :returns: the OpState of the control
    '''
    return getDataFromServer("switchControl",dataDict)

def runTest(dataDict):
    ''' Switch a server outlet on or off 
    
    :param dataDict: a dict holding two keys: 'server' key for the server's name and an 'obj' key for the outlet's name
    :returns: the OpState of the test
    '''
    return getDataFromServer("runTest",dataDict)

def listCommands():
    ''' A command to list all available commands on the communication server
    
    :return: A dict with the command names as the key and a description if available as their value
    '''
    return getDataFromServer("listCommands",{})