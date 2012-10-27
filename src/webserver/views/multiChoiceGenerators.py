"""  Ockle PDU and servers manager
Helper functions for creating multi-choice fields that can then be displayed by the GUI

Created on Oct 27, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

from collections import OrderedDict
import json

def _makeSelectMulitChoice(existingType,objectType,item,getObjectDict,multiListChoices=None):
    ''' Make a multi select option for the select type
    
    :param existingType: The selected option
    :param objectType: The section to build
    :param item: The item to build
    :param getObjectCallback: the Dict holding the select list 
    :param multiListChoices: an existing multiListChoices dict (optional)
    :return: The updated multiListChoices dict
    '''
    #Create a multi-choice box for the outlets
    if multiListChoices == None:
        multiListChoices={}
    if not objectType in multiListChoices:
        multiListChoices[objectType]=OrderedDict()
    multiListChoices[objectType][item]=OrderedDict()
    #getAvailableOutletsList
    for slectionName in getObjectDict().keys():
        multiListChoices[objectType][item][slectionName]={}
    
    for slectionName in multiListChoices[objectType][item].keys():
        multiListChoices[objectType][item][slectionName]["selected"] = (slectionName == existingType)
        
    return multiListChoices


def _makeMultichoice(section,option,multiListChoicesCallback,INIFileDict,multiListChoices=None):
    ''' Generate a multilist format for a template. So it can be rendered on a template
    
    :param section: The option section in the ini file
    :param option: The name of the option in the ini file
    :param multiListChoicesCallback: a callback function the returns a dict of the available options
    :param INIFileDict: An INI file dict that holds the list of selected choices
    :param multiListChoices: If there is a multiListChoices dict you want to append the existing configuration to
    :return: a multiListChoices dict ready to be rendred in a template
    '''
    if multiListChoices == None:
        multiListChoices = OrderedDict()
    
    if not section in multiListChoices.keys():
        multiListChoices[section]=OrderedDict()
    
    #build list of checked plugins multilist
    selectedPlugins = []
    try:
        selectedPlugins = json.loads(INIFileDict[section][option])
    except:
        selectedPlugins = [INIFileDict[section][option]]

    
    multiListChoices[section][option]=multiListChoicesCallback()
    for key in multiListChoices[section][option].keys():
        multiListChoices[section][option][key] = { "doc" : multiListChoices[section][option][key] }
    
    for pluginName in multiListChoices[section][option].keys():
        if pluginName in selectedPlugins:
            multiListChoices[section][option][pluginName]["checked"]=True
        else:
            multiListChoices[section][option][pluginName]["checked"]=False
    return multiListChoices