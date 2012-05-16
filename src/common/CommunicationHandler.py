#!/usr/bin/env python
""" Ockle PDU and servers manager
Handle communication massages from a listner plugin

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from CommunicationMessage import MessageServerSend
from CommunicationMessage import MessageAttr

class CommunicationHandler(object):
    def __init__(self):
        self.commandList=[]
        return
    
    def handleMessage(self,mainDaemon,message):
        print message.__class__.__name__
        returnValue = MessageServerSend(MessageAttr.editServer,{"yay":"yay"})
        print returnValue.toxml()
        return returnValue
    
    def registerCommandList(self,message):
        '''Used by plugins to add an ability to handle a message to the server
        @todo: actually write this
        '''
        self.commandList.append(message)
        return