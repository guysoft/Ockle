#!/usr/bin/env python
""" Ockle PDU and servers manager
Common functions for the whole project
Moved here to avoid code repetition

Created on May 10, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
from ConfigParser import SafeConfigParser
import os.path, sys
import json

class OpState:
    '''
    Operation state enum, that all other operation states enums extend
    '''
    OK=0
    OFF=1
    failedToStart=2
    failedToStop=3
    SwitcingOn = 4
    SwitchingOff = 5
    permanentlyFailedToStart=6
    forcedOn=7
    forcedOff=8
    
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
    return os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])),path)

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
    
