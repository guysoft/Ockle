#!/usr/bin/env python
""" Ockle PDU and servers manager
A dummy controller, useful for testing

Created on Oct 05, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from controllers.ControllerTemplate import ControllerTemplate

from paramiko import SSHClient
import json

class SSHController(ControllerTemplate):
    def __init__(self,name,controllerConfigDict={},controllerParams={}):
        ControllerTemplate.__init__(self,name,controllerConfigDict={},controllerParams={})
        
        self.sshArgs = {"host": controllerParams["host"],
                        "password" : controllerParams["password"],
                        "username" : controllerParams["username"],
                        "key_filename" : controllerParams["key_filename"],
                        "allow_agent" : json.loads(controllerParams["allow_agent"]),
                        "look_for_keys" : json.loads(controllerParams["look_for_keys"]),
                        "compress" : json.loads(controllerParams["compress"])
                        }
        try:
            self.sshArgs["timeout"] = float(controllerParams["timeout"])
        except ValueError:
            pass  
        
        for arg in self.sshArgs.keys():
            if self.sshArgs[arg] == "" and arg != "host":
                self.sshArgs.pop(arg)
        
        self.state=False
        return
    
    def updateData(self):
        pass
    
    def _setControlState(self,state):
        if state == False:
            client = SSHClient()
            client.load_system_host_keys()
            client.connect(** self.sshArgs)
            #stdin, stdout, stderr = client.exec_command('ls -l')
            client.exec_command('shutdown now')
            client.close()
        return