"""  Ockle PDU and servers manager
Communication client tester

Created on Apr 25, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import socket
from ConfigParser import SafeConfigParser
from lxml import html
from common.CommunicationMessage import MessageClientSend
from common.CommunicationMessage import Message

config = SafeConfigParser()
import os.path, sys
ETC_DIR= os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),'..',"etc")
print os.path.join(ETC_DIR,"config.ini")
config.read(os.path.join(ETC_DIR,"config.ini"))
PORT = config.getint('plugins.SocketListener', 'LISTENER_PORT')

def getServerTree():
    returnValue=""
    try:
        #a = MessageClientSend(MessageAttr.listServers,{"yay":"yay"})
        a = MessageClientSend("dotgraph",{"yay":"yay"})
        #create an INET, STREAMing socket
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        #now connect to the web server on port 80
        # - the normal http port
        print "trying to connect"
        #print a.toxml()
        s.connect(("127.0.0.1", PORT))
        s.send(a.toxml())
        #TODO find a way to determine the size of the transport
        data = s.recv (10000)
        if data:
            messageGen = Message()
            print data
            reply = messageGen.parse(data)
            
            reply.getCommand()
            returnValue= html.fromstring(reply.getDataDict()["Dot"][0]).text
    except:
        returnValue="Error connecting to Ockle server"
        s.close()
    return returnValue