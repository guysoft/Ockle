#!/usr/bin/env python
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
ETC_DIR= os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),"etc")
print os.path.join(ETC_DIR,"config.ini")
config.read(os.path.join(ETC_DIR,"config.ini"))
PORT = config.getint('plugins.SocketListener', 'LISTENER_PORT')

from webserver.ockle_client.ClientCalls import getDataFromServer

class ConnectionClient(object):
    '''
    classdocs
    '''
    def getServerTree(self):
        
        def recv(sendMessage):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            n = ''
            data = ''
            try:
                s.connect(('localhost', PORT))
                s.sendall(str(len(sendMessage)) + ":" + sendMessage)
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
            
            
        a = MessageClientSend("listcommands",{"Path":"config.ini"})
        
        
        cnt = 0
        while cnt < 3:
            m, data = recv(a.toxml())
            print 'recv: ', 'error=', m, 'data=', data
            cnt += 1
        returnValue = data
        
        return returnValue
    
    def __init__(self):
        '''
        Constructor
        '''
        #print self.getServerTree()
        print getDataFromServer("restart",{"Path":"config.ini"})
        
        
        
if __name__ == "__main__":
    a = ConnectionClient()