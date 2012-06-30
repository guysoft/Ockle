#pyramid stuff
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import Response

#ockle stuff
from ockle_client.ClientCalls import getServerTree
from ockle_client.ClientCalls import getServerView

#graphviz
import pygraphviz as pgv

@view_config(route_name='tree')
def myview(request):
    return Response(str(getServerView(request.matchdict['serverName'])))

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
    gv.layout(prog='dot')
    
    return {"layout": site_layout(),
            "page_title": "Home",
            "xdottree" : gv.draw(format="xdot").replace('\n','\\n\\\n')}


@view_config(renderer="templates/about.pt", name="about.html")
def about_view(request):
    return {"layout": site_layout(),
            "page_title": "About"}


@view_config(renderer="templates/company.pt", name="acme")
def company_view(request):
    return {"layout": site_layout(),
            "page_title": COMPANY + " Projects",
            "company": COMPANY,
            "projects": PROJECTS}


@view_config(renderer="templates/people.pt", name="people")
def people_view(request):
    return {"layout": site_layout(),
            "page_title": "People", "company": COMPANY, "people": PEOPLE}

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
