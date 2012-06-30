#!/usr/bin/env python
"""  Ockle PDU and servers manager
The main daemon that runs it all

Created on Apr 25, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import json
import codecs

from common.common import loadConfig
from common.common import appendProjectPath
from daemon import Daemon

from networkTree.ServerNetwork import *

from straight.plugin import load
from plugins.ModuleTemplate import ModuleTemplate
from networkTree.ServerNetworkFactory import ServerNetworkFactory

from common.CommunicationHandler import CommunicationHandler

config,ETC_DIR = loadConfig()

PLUGIN_DIR =config.get('main', 'PLUGIN_DIR')
LOG_FILE_PATH = appendProjectPath(config.get('main', 'LOG_FILE_PATH'))
#pluginList=["webserver"]
pluginList= json.loads(config.get("plugins","pluginList"))


class MainDaemon():
    def debug(self,message):
        self.f = codecs.open(LOG_FILE_PATH,'a')
        print "DEBUG: " + str(message)
        self.f.write((time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) + str(message.encode("utf-8")) + "\n"));
        self.f.close()
        return
        
    def __init__(self):
        
        #config framework
        self.config = config #get it from the global
        
        #Handle the serverTree
        #Daemon.__init__(self, pidfile, stdin, stdout, stderr)
        
        factory = ServerNetworkFactory()
        self.servers=factory.buildNetwork(ETC_DIR)
        self.servers.allOff()
        #servers.initiateStartup()
        
        #Communication handling system
        self.communicationHandler =CommunicationHandler(self)
        
        self.running= True
        
        #plugin init
        self.plugins = []
        plugins = load(PLUGIN_DIR,subclasses=ModuleTemplate)
        for plugin in plugins:
            if plugin.__name__ in pluginList:
                #self.debug("Loaded: " + plugin.__name__)
                self.plugins.append(plugin(self))
        
        #plugin run
        for plugin in self.plugins:
            plugin.start()
        
        #main loop
        while self.running:
            self.debug("In main loop")
            time.sleep(10)
        return





pluginLoadList=["PingTester"]
    
if __name__ == "__main__":
    servers = MainDaemon()