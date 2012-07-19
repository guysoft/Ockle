#pyramid stuff
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import Response

#ockle stuff
from ockle_client.ClientCalls import getServerTree
from ockle_client.ClientCalls import getServerView
from ockle_client.DBCalls import getServerStatistics
from common.common import OpState

#graphviz
import pygraphviz as pgv

import time
from datetime import datetime
import json

@view_config(route_name='serverView',renderer="templates/server_info.pt")
def serverPage(request):
    serverName = request.matchdict['serverName'];
    
    serverDict = getServerView(serverName)
    if type(serverDict) == dict:
        

        for key in serverDict.iterkeys():
            try:
                serverDict[key] = serverDict[key][0]
            except:
                pass
        
        serverDict["Switch"]=""
        if serverDict["OpState"] ==  str(OpState.OK) or serverDict["OpState"] == str(OpState.SwitchingOff):
            serverDict["Switch"]="on"
        else:
            print serverDict["OpState"]
            serverDict["Switch"]="off"
    else:
        serverDict={}
        serverDict["Switch"]="off"
    '''
    dataLog=[['23-May-08', 578.55], ['20-Jun-08', 566.5], ['25-Jul-08', 480.88], ['22-Aug-08', 509.84],
                  ['26-Sep-08', 454.13], ['24-Oct-08', 379.75], ['21-Nov-08', 303], ['26-Dec-08', 308.56],
                  ['23-Jan-09', 299.14], ['20-Feb-09', 346.51], ['20-Mar-09', 325.99], ['24-Apr-09', 386.15]]
    '''
    dataLog=[]
    serverLog = getServerStatistics(serverName,time.time() - 5,time.time()+1)
    for key in serverLog.keys():
        dataPointTime=serverLog[key]["time"]
        dataPoint=serverLog[key]["time"]
        print "yay"
        dataLog.append([datetime.fromtimestamp(float(dataPointTime)).strftime('%H:%M:%S'),float(dataPoint)])
    return {"layout": site_layout(),
            "xdottree" : "",
            "server_dict" : serverDict,
            "page_title" : "Server View: " + str(serverName),
            "ServerLog" : str(serverLog),
            "dataLog" : str(dataLog)}
    #return Response(str(getServerView(request.matchdict['serverName'])))

def site_layout():
    renderer = get_renderer("templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout

@view_config(renderer="templates/index.pt")
def index_view(request):
    '''
    View of the server network
    '''
    dot= getServerTree()
    
    gv = pgv.AGraph(string=dot,weights=False)
    #TODO: fix this ugly escape character, ie add a javascript variable wrapper
    #gv.node_attr.update(href="javascript:void(click_node(\\'\\\N\\'))")
    gv.node_attr.update(href="server/\\\N")
    gv.node_attr.update(title="server/\\\N")
    gv.node_attr.update(style="filled")
    gv.node_attr.update(fillcolor="#dbdbdb")
    gv.node_attr.update(name="bla")
    
    for node in gv.nodes():
        print node.get_name()
    
    gv.layout(prog='dot')
    
    return {"layout": site_layout(),
            "page_title": "Server Network View",
            "xdottree" : gv.draw(format="xdot").replace('\n','\\n\\\n')}


@view_config(renderer="templates/about.pt", name="about.html")
def about_view(request):
    return {"layout": site_layout(),
            "page_title": "About"}

# Dummy data
COMPANY = "ACME, Inc."

PEOPLE = [
        {'name': 'sstanton', 'title': 'Susan Stanton'},
        {'name': 'bbarker', 'title': 'Bob Barker'},
]

PROJECTS = [
        {'name': 'sillyslogans', 'title': 'Silly Slogans'},
        {'name': 'meaninglessmissions', 'title': 'Meaningless Missions'},
]
