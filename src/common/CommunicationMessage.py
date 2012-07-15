#!/usr/bin/env python
"""  Ockle PDU and servers manager
Types of messages that can be sent to a client and to the Ockle server

Created on May 9, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
sys.path.insert(0, p)

from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
from xml.dom.minidom import Document
import XMLDictionarySerialize  

#how to use: x = Animal.DOG

class Message(object):
    '''Base message class all message classes inherit'''
    def __init__(self,messageAttr="null",data={}):
        '''
        Constructor
        '''
        self.messageAttr = messageAttr
        self.data = data
        return

    
    def toxmlElement(self):
        '''Generated the elements for the xml creation. Should be used in all child toxml implementations'''
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
    
    def parse(self,xml,listenerPlugin=None):
        '''
        Parse a message that was serialized, and return a Message class
        @param xml: The message in XML form
        @param listenerPlugin: a class that has a .debug message, so we can print what message type we got, and from where
        '''
        dom = parseString(xml)
        MessageType = dom.getElementsByTagName('MessageType')[0].getAttribute("name")
        if listenerPlugin!=None:
            listenerPlugin.debug("Received " + str(MessageType))
        for messageCandidate in Message.__subclasses__():
            if MessageType ==  messageCandidate.__name__:
                returnValue = messageCandidate()
                returnValue.parseType(xml)
                return returnValue
        return MessageServerError()

    def parseType(self,xml):
        '''Returns the message Class, needs to be implemented in the child'''
        return
    
    def getDataDict(self):
        '''
        Get the extra xml data information in a dict form
        '''
        return self.data
    
    def getCommand(self):
        '''
        @return: the message command type
        '''
        return self.messageAttr
         
class MessageServerSend(Message):
    '''
    A message to be sent using a communication plugin
    '''
    def __init__(self,messageAttr="null",data={}):
        Message.__init__(self,messageAttr,data)
        return
        
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
    
    def parseType(self,xml):
        #TODO code repitition!!
        dom = parseString(xml)
        messageCommand = dom.getElementsByTagName('MessageAttr')[0]
        messageData = messageCommand.getElementsByTagName('data')[0]
        
        self.messageAttr = messageCommand.getAttribute("Reply")
        self.data=XMLDictionarySerialize.element2dict(messageData)
        
        return

class MessageServerError(Message):
    '''
    Server returns an error message
    '''
    def toxml(self):
        ''' Returns the element as serialized xml'''
        doc,MessageType = Message.toxmlElement(self)
        
        # Create the main <MessageAttr> element
        maincard = doc.createElement("MessageAttr")
        maincard.setAttribute("Error", str(self.messageAttr))
        MessageType.appendChild(maincard)
        
        # Make the <data> element which is a serialized dict
        dataDict =XMLDictionarySerialize.dict2xml(self.data,"data")
        
        maincard.appendChild(dataDict)
        return doc.toxml("UTF-8")
    
    
class MessageClientSend(Message):
    '''
    A message to be received using a communication plugin
    '''
    def __init__(self,messageAttr="null",data={}):
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
    a= MessageClientSend("listServers",{"testd1":"testd2"})

    print a.toxml()
    b= Message()
    print b.parse(a.toxml()).toxml()
    
