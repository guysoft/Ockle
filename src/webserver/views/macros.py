'''
Created on Aug 24, 2012

@author: guy
'''

#pyramid stuff
from pyramid.renderers import get_renderer

def site_layout():
    renderer = get_renderer("templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout


def config_ini_layout():
    renderer = get_renderer("templates/test.pt")
    macro = renderer.implementation().macros['name_filler']
    return macro