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
import json

config = SafeConfigParser()
import os.path, sys
ETC_DIR= os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),'..',"etc")
print os.path.join(ETC_DIR,"config.ini")
config.read(os.path.join(ETC_DIR,"config.ini"))
PORT = config.getint('plugins.SocketListener', 'LISTENER_PORT')
SOCKET_TIMEOUT = config.getint('plugins.SocketListener', 'SOCKET_TIMEOUT')
OCKLE_SERVER_HOSTNAME="127.0.0.1"

def getDataFromServer(command,paramsDict):
    ''' Send a command to the Ockle server, and return the responce dict 
    @param command: The command to send
    @param paramsDict: the dictionary that is sent with command arguments
    @return: A dict with the responce data, None if we failed to connect
    '''
    returnValue=""
    def recv(sendMessage):
        ''' Loop to receive a message'''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(SOCKET_TIMEOUT)
        n = ''
        data = ''
        try:
            s.connect((OCKLE_SERVER_HOSTNAME, PORT))
            s.sendall(str(len(sendMessage)) +":" +sendMessage)
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
            return None, data
        except socket.error as e:
            s.close()
            return e, None
        
    a = MessageClientSend(command,paramsDict)
    m, data = recv(a.toxml())
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

def getServerTree():
    ''' Get a server tree status from the Ockle server, and return a dict ready
    to be parsed by a pyramid view '''
    response = getDataFromServer("dotgraph",{"yay":"yay"})
    if response == None:
        return "Error connecting to Ockle server"
    else:
        return html.fromstring(response["Dot"]).text 

def getServerView(serverName):
    response = getDataFromServer("ServerView",{"server":serverName})
    if response == None:
        return "Error connecting to Ockle server - Can't get server Info"
    else:
        #return html.fromstring(str(response)).text 
        return response
    return

def getAutoControlStatus():
    response = getDataFromServer("getAutoControlStatus",{})
    if response == None:
        return {"status":"N/A"}
    else:
        return response
    return

def getINIFile(iniPath):
    return getDataFromServer("getINIFile",{"Path":iniPath})["File"]

def getAvailablePluginsList():
    response = getDataFromServer("getAvailablePluginsList",{})
    if response == None:
        return {}
    else:
        return response
    return

def setINIFile(iniPath,iniDict):
    return getDataFromServer("setINIFile",{"Path":iniPath, "iniDict" : json.dumps(iniDict)})

    