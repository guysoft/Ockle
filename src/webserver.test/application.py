#!/usr/bin/env python
"""  Ockle PDU and servers manager
Basic webserver testing area

Created on Jun 27, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

#pyramid
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config

#Ockle
import sys, os, os.path
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'common')
print p
sys.path.insert(0, p)
import socket
from ConfigParser import SafeConfigParser
from lxml import html
from common.CommunicationMessage import MessageClientSend
from common.CommunicationMessage import Message

config = SafeConfigParser()
ETC_DIR= os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),'..',"etc")
print os.path.join(ETC_DIR,"config.ini")
config.read(os.path.join(ETC_DIR,"config.ini"))
PORT = config.getint('plugins.SocketListener', 'LISTENER_PORT')

@view_config(renderer="hello.pt")
def showTree(request):
    return {"tutorial": "Little Dummy"}
    returnValue=""
    
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
    data = s.recv (1024)
    if data:
        messageGen = Message()
        reply = messageGen.parse(data)
        
        reply.getCommand()
        returnValue=html.fromstring(reply.getDataDict()["Dot"][0]).text
        
    s.close()
    return Response(returnValue)

if __name__ == '__main__':
   config = Configurator()
   #config.scan("views")
   config.add_route('tree', '/tree/{name}')
   config.add_view(showTree, route_name='tree')
   app = config.make_wsgi_app()
   server = make_server('0.0.0.0', 8000, app)
   server.serve_forever()
   