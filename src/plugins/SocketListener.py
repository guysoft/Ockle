#!/usr/bin/env python
"""  Ockle PDU and servers manager
Socket Listener plugin
Lets Ockle talk to a webserver or client using a network socket

Created on May 02, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)

from common.CommunicationMessage import *

import socket

from plugins.ModuleTemplate import ModuleTemplate

from common.CommunicationMessage import MessageServerError

class SocketListener(ModuleTemplate):
    ''' Lets Ockle talk to a webserver or client using a network socket '''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        self.LISTENER_PORT = self.getConfigInt('LISTENER_PORT')
        self.MAX_CONNECTIONS = self.getConfigInt('MAX_CONNECTIONS')
        self.MAX_RCV_SIZE = self.getConfigInt('MAX_RCV_SIZE')
        
        return
    
    def run(self):
        self.debug("\n")
        
        
        #create an INET, STREAMing socket
        serverSocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        #bind the socket to a public host,
        # and a well-known port
        serverSocket.bind(('', self.LISTENER_PORT))
        #become a server socket
        serverSocket.listen(self.MAX_CONNECTIONS)
        
        self.debug("Started Listening on port:" + str(self.LISTENER_PORT))
        while 1:
            client, address = serverSocket.accept()
            print 'We have opened a connection with', address
            data = client.recv(self.MAX_RCV_SIZE)
            
            self.debug(data)
            if data:
                
                message= Message(data,self)
                #TODO add here for debug what message we got
                message = message.parse(data,self)
                #try:
                xml = self.mainDaemon.communicationHandler.handleMessage(message).toxml()
                self.debug("Sending XML:" + str(xml))
                #client.send(xml)
                client.sendall(str(len(xml)) +":" +  xml)
                #except:
                #    self.debug("Got a bad message class, returning error")
                #    client.send(MessageServerError().toxml())
                client.close()
            '''
            client.close() 
            #accept connections from outside
            (clientsocket, address) = serverSocket.accept()
            #now do something with the clientsocket
            #in this case, we'll pretend this is a threaded server
            ct = client_thread(clientsocket)
            ct.run()
            '''
            
        return

if __name__ == "__main__":
    a = SocketListener(None)