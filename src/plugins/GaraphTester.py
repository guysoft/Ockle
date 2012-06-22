#!/usr/bin/env python
"""  Ockle PDU and servers manager
Test plugin to check graph capabilities

Created on May 16, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','common')
sys.path.insert(0, p)
import time
from plugins.ModuleTemplate import ModuleTemplate
import pygraph.readwrite.dot
import pygraphviz as pgv
import time

class GraphTester(ModuleTemplate):
    def __init__(self,MainDaemon):
        ModuleTemplate.__init__(self,MainDaemon)
        return
    
    def run(self):
        self.debug("\n")
        
        while True:
            #print self.mainDaemon.servers.graph
            dot=pygraph.readwrite.dot.write(self.mainDaemon.servers.graph,False)
            f = open("/tmp/graph_viz.dot","w")
            f.write(dot)
            f.close()
            
            gv = pgv.AGraph("/tmp/graph_viz.dot",weights=False)
            print dot
            gv.layout(prog='dot')
            gv.draw('/tmp/file.png')
            time.sleep(5)
        return

if __name__ == "__main__":
    a = GraphTester(None)