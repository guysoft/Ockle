"""  Ockle PDU and servers manager
Helper functions for parsing and arranging INI files for display in the GUI

Created on Oct 27, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""

import os.path
from ockle_client.ClientCalls import loadINIFileTemplate
from ockle_client.ClientCalls import loadINIFileConfig
from ockle_client.ClientCalls import getPDUFolder
from ockle_client.ClientCalls import getTesterFolder
from ockle_client.ClientCalls import getControllerFolder
from ockle_client.ClientCalls import getServerFolder

def __fillINIwithTemplate(INIFileTemplate,INIFileDict={}):
    ''' Fill missing values in an INI config file with ones that exist in the template
    
    :param INIFileTemplate: The config template as a dict
    :param INIFileDict: The config file dict
    :return: The new INIFileDict with the missing fields
    '''
    for section in INIFileTemplate.keys():
        if section not in INIFileDict.keys():
            INIFileDict[section] = {}
        for item in INIFileTemplate[section].keys():
            if item not in INIFileDict[section]:
                INIFileDict[section][item] =  INIFileTemplate[section][item][1]
    return INIFileDict

def _loadPDUINITemplate(outletType):
    ''' Get the outlet type template
    
    :param outletType: The type of the outlet 
    :reurn: Outlet ini template dict'''
    return loadINIFileTemplate(['conf_outlets/' + outletType + '.ini'] + ["outlets.ini"])

def _loadTesterINITemplate(testerType):
    ''' Get the outlet type template
    
    :param outletType: The type of the tester
    :reurn: Tester ini template dict'''
    return loadINIFileTemplate(['conf_testers/' + testerType + '.ini'] + ["testers.ini"])

def _loadControllerINITemplate(controllerType):
    ''' Get the outlet type template
    
    :param outletType: The type of the tester
    :reurn: Tester ini template dict'''
    return loadINIFileTemplate(['conf_controllers/' + controllerType + '.ini'] + ["controllers.ini"])

def _loadServerINITemplate():
    ''' Get the serverNode template
    
    :reurn: Server ini template dict'''
    return loadINIFileTemplate("serverNodes.ini")

def _loadPDUConfig(PDUName):
    ''' Get the config Dict of a PDU
    
    :param PDUName: The name of the PDU
    :return: a config dict of the PDU'''
    configPath= os.path.join(getPDUFolder() , PDUName + '.ini')
    return loadINIFileConfig(configPath)

def _loadTesterConfig(testerName):
    ''' Get the config Dict of a Tester
    
    :param testerName: The name of the tester
    :return: a config dict of the tester'''
    configPath= os.path.join(getTesterFolder() , testerName + '.ini')
    return loadINIFileConfig(configPath)

def _loadControllerConfig(controllerName):
    ''' Get the config Dict of a controller
    
    :param controllerName: The name of the controller
    :return: a config dict of the controller'''
    configPath= os.path.join(getControllerFolder() , controllerName + '.ini')
    return loadINIFileConfig(configPath)

def _loadServerConfig(serverName):
    ''' Get the config Dict of a server
    
    :param serverName: The name of the server
    :return: a config dict of the server'''
    configPath= _getServerConfigPath(serverName)
    return loadINIFileConfig(configPath)

def _getServerConfigPath(serverName):
    ''' Get the config file path of a server
    
    :param serverName: The name of the server
    :return: The path of the server'''  
    return os.path.join(getServerFolder() , serverName + '.ini')

