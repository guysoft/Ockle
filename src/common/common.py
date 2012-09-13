#!/usr/bin/env python
""" Ockle PDU and servers manager
Common functions for the whole project
Moved here to avoid code repetition

Created on May 10, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from ConfigParser import SafeConfigParser
from StringIO import StringIO
import os.path, sys
import json
from collections import OrderedDict

class OpState:
    '''
    Operation state enum, that all other operation states enums extend
    '''
    OK="OK"
    OFF="OFF"
    failedToStart="Failed to start"
    failedToStop="Failed to stop"
    SwitcingOn = "Switching on"
    SwitchingOff = "Switching off"
    permanentlyFailedToStart="Permanently failed to start"
    forcedOn="Forced on"
    forcedOff="Forced off"
    
COLOR_DICT={
            -1:"black",
            OpState.OK:"green",
           OpState.failedToStart:"orange",
           OpState.failedToStop:"yellow",
           OpState.SwitcingOn:"grey",
           OpState.SwitchingOff:"blue",
           OpState.permanentlyFailedToStart:"red",
           }
    

def loadConfig():
    ''' Get the config file and folder
    @return: a tuple with a config parser to config.ini and the etc folder'''
    config = SafeConfigParser()
    ETC_DIR= appendProjectPath("etc")
    config.read(os.path.join(ETC_DIR,"config.ini"))
    return config,ETC_DIR

def appendProjectPath(path=""):
    ''' Appends the project path to a relative path
    @param path: the internal path
    @return: the relative path 
    '''
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),'..',path)

def turpleList2Dict(tupleList):
    ''' Convert a tuple list to a dict. For easy and saner access
    Used in this project because config parser returns a list of tuples
    @param tupleList the list of tuples
    @return: a dict with lists for each variable
    '''
    returnDict={}
    for turple in tupleList:
        key = turple[0]
        data = turple[1]
        if data.startswith("["):#turn to a list if lists
            data = json.loads(data)
        returnDict[key]=data
    return returnDict

def trimOneObjectListsFromDict(d):
    ''' There is some strange bug in the xml dict recovery,
    Some strings return as lists with a single element,
    This is a workaround
    @param d: A dict containing some single element lists
    @return: The dict with the lists removed and replaced by the element
    '''
    for key in d.iterkeys():
        try:
            d[key] = d[key][0]
        except:
            pass
    return d

def slicedict(d, s):
    ''' Slice a dict according to a prefix in the key 
    @param d: a dict
    @param s: The prefix
    @return: The sliced dict
    '''
    return {k:v for k,v in d.iteritems() if k.startswith(s)}

def configToDict(config):
    ''' Get a configuration dictionary from a config parser
    @param config: A config file handler
    @return: A dict of the sections and the variables in it
    '''
    returnValue={}
    
    for section in config.sections():
        returnValue[section]={}
        sectionTurples = config.items(section)
        for itemTurple in sectionTurples:
            returnValue[section][itemTurple[0]] = itemTurple[1]
    return returnValue

def iniToDict(path):
    ''' Read an ini path in to a dict
    @param path: Path to file
    @return: a dict of that path
    ''' 
    config = SafeConfigParser()
    config.read(path)
    return configToDict(config)

def dictToConfig(d):
    ''' Get a config parser from a config dictionary
    @param d: a dictionary
    @return: a config parser file handler
    '''
    config = SafeConfigParser()
    
    for section in d.keys():
        config.add_section(section)
        for item in d[section]:
            value = d[section][item]
            if type(value) == list:
                value = json.dumps(value)
            config.set(section,item,value)
        
    return config

def _appendTemplateDIR(path):
    CONFIG_TEMPLATE_DIR= appendProjectPath(os.path.join("src","config"))
    print CONFIG_TEMPLATE_DIR
    return os.path.join(CONFIG_TEMPLATE_DIR,path)

def getINITemplate(paths):
    ''' Get an INI template as a dict
    @param path: relative path in the src tree
    @return: a dict of the config template
    '''
    if type(paths) == str:
        paths = [paths]
    appandedPaths=[]
    for path in paths:
        appandedPaths.append(_appendTemplateDIR(path))
    config = SafeConfigParser()
    config.read(appandedPaths)
    return configToDict(config)

def getINIFolderTemplate(path):
    print path
    files = os.listdir(_appendTemplateDIR(path))
    print _appendTemplateDIR(path)
    returnValue=[]
    for fileName in files:
        returnValue.append(_appendTemplateDIR(os.path.join(path,fileName)))
    return returnValue

def getINITemplateFolder(path):
    ''' Get an INI template of a all INI files in a folder
    @param path: relative path in the src tree
    @return: a dict of the config template
    '''
    returnValue={}
    config = SafeConfigParser()
    CONFIG_TEMPLATE_DIR= _appendTemplateDIR()
    for filePath in os.listdir(os.path.join(CONFIG_TEMPLATE_DIR,path)):
        returnValue = mergeDicts(returnValue,configToDict(config.read(os.path.join(CONFIG_TEMPLATE_DIR,path,filePath))))
    return returnValue

def getINIstringtoDict(iniString):
    ''' Take an ini file as as string, and convert it to a dict
    @param iniString: ini file as string
    @return: a dict of that ini file
    ''' 
    print iniString
    iniFile = StringIO(iniString)
    iniConfig = SafeConfigParser()
    iniConfig.readfp(iniFile)
    return configToDict(iniConfig)

def mergeDicts(a,b):
    ''' Merges two dicts, second should overwrite the first
    @param a: a dict
    @param b: a dict, should overwrite a
    @return: a merged dict, second dict overwrites the first
    '''
    return dict(a.items() + b.items())

def sortDict(d):
    ''' Takes a normal unsorted dict, and returns an alphabetically ordered dict
    @param d: An unsorted dict
    @return: An ordered dict, sorted
    '''
    return OrderedDict(sorted(d.items(), key=lambda t: t[0])) 