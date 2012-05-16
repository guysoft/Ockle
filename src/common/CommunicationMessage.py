#!/usr/bin/env python
"""  Ockle PDU and servers manager
Types of messages that can be sent to a client and to the Ockle server

Created on May 9, 2012

@author: Guy Sheffer <guysoft at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
sys.path.insert(0, p)

from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
from xml.dom.minidom import Document
import XMLDictionarySerialize

#list of message commands to send
class MessageAttr:
    init=-1
    listServers=1 #Get a list of the servers
    addServer=2 #add a server
    removeServer=3
    editServer=4
    

#how to use: x = Animal.DOG

class Message(object):
    '''Base message class all message classes inherit'''
    def __init__(self,messageAttr=MessageAttr.init,data={}):
        '''
        Constructor
        '''
        self.messageAttr = messageAttr
        self.data = data
        return

    
    def toxmlElement(self):
        '''Generated the elements for the xml creationl. Should be used in all child toxml implementations'''
        impl = getDOMImplementation()
        
        # Create the minidom document
        doc = Document()
        
        # Create the <MessageType> base element
        MessageType = doc.createElement("MessageType")
        MessageType.setAttribute("name", self.__class__.__name__)
        doc.appendChild(MessageType)
        return doc,MessageType
    
    def toxml(self):
        '''Returns the xml element, needs to be implemented in the child'''
        return
    
    def parse(self,xml):
        '''
        Parse a message that was serialized, and return a Message class
        '''
        dom = parseString(xml)
        MessageType = dom.getElementsByTagName('MessageType')[0].getAttribute("name")
        
        for messageCandidate in Message.__subclasses__():
            if MessageType ==  messageCandidate.__name__:
                returnValue = messageCandidate()
                returnValue.parseType(xml)
                return returnValue
        return MessageServerError()

    def parseType(self,xml):
        '''Returns the message Class, needs to be implemented in the child'''
        return
         
class MessageServerSend(Message):
    '''
    A message to be sent using a communication plugin
    '''
    def __init__(self,messageAttr=MessageAttr.init,data={}):
        Message.__init__(self)
        self.messageAttr=MessageAttr
        print MessageAttr
        
    def toxml(self):
        ''' Returns the element as serialized xml'''
        doc,MessageType = Message.toxmlElement(self)
        
        # Create the main <MessageAttr> element
        maincard = doc.createElement("MessageAttr")
        maincard.setAttribute("Reply", str(self.messageAttr))
        MessageType.appendChild(maincard)
        
        # Make the <data> element which is a serialized dict
        dataDict =XMLDictionarySerialize.dict2xml(self.data,"data")
        
        maincard.appendChild(dataDict)
        return doc.toxml("UTF-8")

class MessageServerError(Message):
    '''
    Server returns an error message
    '''
    
    
class MessageClientSend(Message):
    '''
    A message to be received using a communication plugin
    '''
    def __init__(self,messageAttr=MessageAttr.init,data={}):
        Message.__init__(self)
        self.messageAttr = messageAttr
        self.data = data
        return
    
    def toxml(self):
        ''' Returns the element as serialized xml'''
        doc,MessageType = Message.toxmlElement(self)
        
        # Create the main <MessageAttr> element
        maincard = doc.createElement("MessageAttr")
        maincard.setAttribute("Command", str(self.messageAttr))
        MessageType.appendChild(maincard)
        
        # Make the <data> element which is a serialized dict
        dataDict =XMLDictionarySerialize.dict2xml(self.data,"data")
        
        maincard.appendChild(dataDict)
        return doc.toxml("UTF-8")
    
    def parseType(self,xml):
        dom = parseString(xml)
        messageCommand = dom.getElementsByTagName('MessageAttr')[0]
        messageData = messageCommand.getElementsByTagName('data')[0]

        self.messageAttr = messageCommand.getAttribute("Command")
        self.data=XMLDictionarySerialize.element2dict(messageData)
        return
        
    
if __name__ == "__main__": 
    a= MessageClientSend(MessageAttr.listServers,{"testd1":"testd2"})

    print a.toxml()
    b= Message()
    print b.parse(a.toxml()).toxml()
    
