"""  Ockle PDU and servers manager
Page macros for the Ockle GUI

Created on Aug 24, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

#pyramid stuff
from pyramid.renderers import get_renderer

def site_layout():
    renderer = get_renderer("templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout


def config_sidebar_body():
    renderer = get_renderer("templates/config_sidebar.pt")
    return renderer.implementation().macros['config_sidebar_body']

def config_sidebar_head():
    renderer = get_renderer("templates/config_sidebar.pt")
    return renderer.implementation().macros['config_sidebar_head']

def INI_InputArea_body():
    renderer = get_renderer("templates/INI_InputArea.pt")
    return renderer.implementation().macros['INI_InputArea_body']

def INI_InputArea_head():
    renderer = get_renderer("templates/INI_InputArea.pt")
    return renderer.implementation().macros['INI_InputArea_head']

