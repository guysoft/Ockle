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
from common.Exceptions import ParsingTemplateException

import json

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

    '''
    returnValue=""
    try:
        #a = MessageClientSend(MessageAttr.listServers,{"yay":"yay"})
        a = MessageClientSend(command,paramsDict)
        #create an INET, STREAMing socket
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        #now connect to the web server on port 80
        # - the normal http port
        print "trying to connect"
        print a.toxml()
        s.connect((OCKLE_SERVER_HOSTNAME, PORT))
        s.send(a.toxml())
        #TODO find a way to determine the size of the transport
        data = s.recv (MAX_RECIVE)
        if data:
            messageGen = Message()
            print "got the following data"
            print data
            reply = messageGen.parse(data)
            
            reply.getCommand()
            returnValue= reply.getDataDict()
    except:
        returnValue=None
        s.close()
    '''
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

def getINIFile(iniPath):
    return getDataFromServer("getINIFile",{"Path":iniPath})["File"]

def getAvailablePluginsList():
    return _getDataFromServerWithFail("getAvailablePluginsList",{},{})

def setINIFile(iniPath,iniDict):
    return getDataFromServer("setINIFile",{"Path":iniPath, "iniDict" : json.dumps(iniDict)})

def restartOckle():
    return getDataFromServer("restart",{},True)

def getPDUDict():
    reply = json.loads(getDataFromServer("getPDUDict")["pdus"])
    return reply

def getTesterDict():
    reply = json.loads(getDataFromServer("getTesterDict")["testers"])
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

def getAvailableOutletsList():
    response = getDataFromServer("getAvailableOutletsList")
    if response == None:
        return {}
    else:
        return json.loads(response["Outlets"])
    return

def getAvailableTestersList():
    response = getDataFromServer("getAvailableTestersList")
    if response == None:
        return {}
    else:
        return json.loads(response["Testers"])
    return

def getOutletFolder():
    return loadINIFileConfig("config.ini")['main']['outlet_dir']

def getTesterFolder():
    return loadINIFileConfig("config.ini")['main']['tester_dir']

def switchOutlet(dataDict):
    return getDataFromServer("switchOutlet",dataDict)