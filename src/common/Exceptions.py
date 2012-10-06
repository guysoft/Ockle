#!/usr/bin/env python
"""  Ockle PDU and servers manager
Common exceptions in the project

Created on Mar 14, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
class Error(Exception):
    '''Base class for exceptions in this module.'''
    def debug(self,message):
        print "Error: " + self.__class__.__name__ + ": " + str(message)
        return
class _ObjGeneratorTypeNotFound(Error):
    '''Exception raised when an obj Generator type was not found

    Attributes:
        @param iniFile : Path to ini file contains the declaration
        @param type: the type of outlet declared
        @param objGenerator: the object Generator
    '''
    def __init__(self, objGenerator, iniFile, objType):
        self.debug(objGenerator + " type '" + objType + "' specified in " + iniFile + " does not exist")
        
class OutletTypeNotFound(_ObjGeneratorTypeNotFound):
    def __init__(self, iniFile, objType):
        _ObjGeneratorTypeNotFound.__init__(self,"PDU", iniFile, objType)
    
class TesterTypeNotFound(Error):
    def __init__(self, iniFile, objType):
        _ObjGeneratorTypeNotFound.__init__(self,"Tester", iniFile, objType)    

class ControllerTypeNotFound(Error):
    def __init__(self, iniFile, objType):
        _ObjGeneratorTypeNotFound.__init__(self,"Controller", iniFile, objType)
                    
class MultipleDeclerationInConfig(Error):
    '''Exception raised for multiple declaration in same config file,

    Attributes:
        @param iniFile : Path to ini file contains the declaration
        @param section: section in the ini file
        @param key: the key that is declated twice or more
    '''
    def __init__(self, iniFile,section,key):
        self.debug("The property " + key + " was declared multiple times in config file " + iniFile + " in section:" + section)

class MultipleDeclerationList(Error):
    ''''Exception raised for multiple declaration in same section list of tuples

    Attributes:
        @param key the key that caused the clash
    '''
    def __init__(self, key):
        self.key = key
        
        
class ParsingTemplateException(Error):
    ''' Exception raised if we got an invalid template ini file to parse'''
    