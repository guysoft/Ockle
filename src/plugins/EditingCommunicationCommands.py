#!/usr/bin/env python
"""  Ockle PDU and servers manager
A plugin to add a commands that let you modify Ockle config files. 

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
from plugins.ModuleTemplate import ModuleTemplate
import pygraph.readwrite.dot
import traceback

import json

class EditingCommunicationCommands(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def getINIFile(self,dataDict):
        fileContent =""
        path = dataDict["Path"]
        print path
        try:
            path = os.path.join("etc",path)
            print path
            with open(path, 'r') as content_file:
                fileContent = content_file.read()
        except:
            traceback.print_exc(file=sys.stdout)
        return {"File" :  fileContent}
    
    def run(self):
        self.debug("\n")
        self.mainDaemon.communicationHandler.AddCommandToList("getINIFile",lambda dataDict: self.getINIFile(dataDict))

        return

if __name__ == "__main__":
    a = CoreCommunicationCommands(None)