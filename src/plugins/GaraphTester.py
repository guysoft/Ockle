#!/usr/bin/env python
"""  Ockle PDU and servers manager
Simple tester for graph functions

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
from plugins.ModuleTemplate import ModuleTemplate
import pygraph.readwrite.dot

class GraphTester(ModuleTemplate):
    ''' Simple tester for graph functions'''
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def getDotGraph(self,dataDict):
        dot = pygraph.readwrite.dot.write(self.mainDaemon.servers.graph,False) 
        return {"Dot" :  dot}
    
    def run(self):
        self.debug("\n")
        self.mainDaemon.communicationHandler.AddCommandToList("dotgraph",lambda dataDict: self.getDotGraph(dataDict))
        '''
        while True:
            #print self.mainDaemon.servers.graph
            dot=pygraph.readwrite.dot.write(self.mainDaemon.servers.graph,False)
            
            gv = pgv.AGraph(string=dot,weights=False)
            gv.layout(prog='dot')
            gv.draw('/tmp/file.png')
            gv.draw('forfmat.xdot')
            print gv.draw(format="xdot")
            time.sleep(5)
        '''
        return

if __name__ == "__main__":
    a = GraphTester(None)