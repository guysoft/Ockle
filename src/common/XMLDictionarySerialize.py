#!/usr/bin/env python
"""  Ockle PDU and servers manager
Turn dicts to xml and back

Created on May 8, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
Adapted from code by Ben Lackey http://nonplatonic.com/ben.php?title=python_xml_to_dict_bow_to_my_recursive_g
"""
import xml.dom.minidom
from xml.dom.minidom import Document

def xml2dict(xmlstring):
    doc = xml.dom.minidom.parseString(xmlstring)
    removeWhilespace_nodes(doc.documentElement)
    return element2dict(doc.documentElement)

def dict2xml(dictionary, name="dictionary"):
    '''Return an element from a dictionary
    @param dictionary the dictionary
    @return a dom element from the dict'''
    xml = Document()
    items = xml.createElement(name)
    for key, val in dictionary.items():
        node = xml.createElement(str(key))
        node.appendChild(xml.createTextNode(str(val)))
        items.appendChild(node)
    return items

def element2dict(parent):
    '''
    Takes a dom element, and turns it in to a dict
    @param parent the dom parent
    @return: a python dict
    '''
    child = parent.firstChild
    if (not child):
        return None
    elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
        return child.nodeValue
    
    d={}
    while child is not None:
        if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
            try:
                d[child.tagName]
            except KeyError:
                d[child.tagName]=[]
            d[child.tagName].append(element2dict(child))
        child = child.nextSibling
    return d

def removeWhilespace_nodes(node, unlink=True):
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            removeWhilespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()
