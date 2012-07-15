#pyramid stuff
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import Response

#ockle stuff
from ockle_client.ClientCalls import getServerTree
from ockle_client.ClientCalls import getServerView
from common.common import OpState

#graphviz
import pygraphviz as pgv

@view_config(route_name='serverView',renderer="templates/server_info.pt")
def serverPage(request):
    serverName = request.matchdict['serverName'];
    
    serverDict = getServerView(serverName)
    if type(serverDict) == dict:
        '''
        for key in serverDict.iterkeys():
            serverDict[key] = serverDict[key][0]
        '''
        
        serverDict["Switch"]=""
        if serverDict["OpState"] ==  OpState.OK or serverDict["OpState"] == OpState.SwitchingOff:
            serverDict["Switch"]="On"
        else:
            serverDict["Switch"]="Off"
    else:
        serverDict={}
     
    return {"layout": site_layout(),
            "xdottree" : "",
            "server_dict" : serverDict,
            "page_title" : "Server View: " + str(serverName)}
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
