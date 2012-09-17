import os.path,sys
p = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
print p
sys.path.insert(0, p)

from collections import OrderedDict

#pyramid stuff
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import Response

#ockle stuff
from ockle_client import ClientCalls
from ockle_client.ClientCalls import getServerTree
from ockle_client.ClientCalls import switchOutlet
from ockle_client.ClientCalls import getServerView
from ockle_client.ClientCalls import getAutoControlStatus
from ockle_client.ClientCalls import getINIFile
from ockle_client.ClientCalls import setINIFile
from ockle_client.ClientCalls import restartOckle
from ockle_client.ClientCalls import getAvailablePluginsList
from ockle_client.ClientCalls import getAvailableOutletsList
from ockle_client.ClientCalls import getAvailableTestersList
from ockle_client.ClientCalls import getAvailableServerOutlets
from ockle_client.ClientCalls import getAvailableServerTesters
from ockle_client.ClientCalls import getPDUDict
from ockle_client.ClientCalls import getTesterDict
from ockle_client.ClientCalls import getServerDict
from ockle_client.ClientCalls import loadINIFileTemplate
from ockle_client.ClientCalls import loadINIFileConfig
from ockle_client.ClientCalls import getOutletFolder
from ockle_client.ClientCalls import getTesterFolder
from ockle_client.ClientCalls import getServerFolder
from ockle_client.ClientCalls import getServerDependencyMap
from ockle_client.DBCalls import getServerStatistics
from common.common import OpState
from common.common import sortDict
from common.common import slicedict
from common.common import getINIFolderTemplate
from plugins.Log import DATA_NAME_TO_UNITS
from plugins.Log import DATA_NAME_TO_UNITS_NAME

#macros
from macros import site_layout,config_sidebar_head,config_sidebar_body,INI_InputArea_head,INI_InputArea_body

#config stuff
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from common.common import getINIstringtoDict

#graphviz
import pygraphviz as pgv

import time
from datetime import datetime
import json

#plot settings
PLOT_STEP=3600 #What is the step length of the graph
STATISTICS_WINDOW=60*60*3#How far back should the log show

@view_config(route_name='serverView',renderer="templates/server_info.pt")
def serverPage_view(request):
    ''' Server View page 
    '''
    def unix2javascript(time):
        ''' Convert a unix timestamp to a javascript timestamp
        @param time: Unix timestamp
        @return: Javascript timestamp
        '''
        return time*1000.0
    
    def javascript2unix(time):
        ''' Convert a javascript timestamp to a unix timestamp
        @param time: Javascript timestamp
        @return: Unix timestamp
        '''
        return time/1000
    
    def getMinMaxListofLists(l,key):
        ''' Get the min and max of a list of lists, takes a list and the key value
        @param l: a list of lists, or list of dicts
        @param key: the key number of the list
        @return: tuple of the min and max values
        '''
        try:
            Min = l[0][key]
            Max = l[0][key]
        except KeyError:
            return 0 
        for element in l:
            if Max < element[key]:
                Max = element[key]
            if Min > element[key]:
                Min =  element[key]
        return Min,Max
    
    serverName = request.matchdict['serverName']
    serverDict = getServerView(serverName)
    
    if type(serverDict) == dict:
        
        #Set the on/of switch
        serverDict["Switch"]=""
        if serverDict["OpState"] ==  str(OpState.OK) or serverDict["OpState"] == str(OpState.SwitchingOff):
            serverDict["Switch"]="on"
        else:
            serverDict["Switch"]="off"
    else:
        #return an empty dict if we encountered some error
        serverDict={}
        serverDict["Switch"]="off"
    
    ## Build data for the statistics display ##
    dataLog=[]
    serverLog = getServerStatistics(serverName,time.time() - STATISTICS_WINDOW,time.time()+1)
    #get the last data entry
    dataDictHead = {}
    if not serverLog.keys() == []:
        dataEntry = serverLog[serverLog.keys()[len(serverLog)-1]]
        dataDictHead=json.loads(dataEntry["dataDict"])#parse the dict from the db string
    
    #list of variables we are going to fill, generating the plots
    #plotsTicks=[]
    plotTitle=[]
    plotXLabel="Time [Hr:Min]"
    plotYFormat=[]
    plotYLabel=[]
    plotsData=[]
    minTick=[]
    maxTick=[]
    plotNumber=0
    for outletKey in slicedict(dataDictHead,"outlet").keys():
        for dataKey in dataDictHead[outletKey].keys():
            if dataKey != "name":
                #Init all the plot labels and lists
                #TODO time pulling can be done at O(n) not O(n^2)
                plotTitle.insert(plotNumber, dataKey + " graph for " + dataDictHead[outletKey]["name"])
                plotYLabel.insert(plotNumber, dataKey + " " + DATA_NAME_TO_UNITS_NAME[dataKey])
                plotYFormat.insert(plotNumber, DATA_NAME_TO_UNITS[dataKey])
                plotsData.insert(plotNumber, [])
                #plotsTicks.insert(plotNumber, [])
                
                #Retrieve data for this plot
                for key in serverLog.keys(): #now we scan all keys
                    #parse the database entry
                    dataDict = json.loads(serverLog[key]["dataDict"])
                    
                    #save data point
                    dataPointTime=serverLog[key]["time"]
                    try:
                        dataPoint=dataDict[outletKey][dataKey]
                    except KeyError:
                        dataPoint=0
                    
                    plotsData[plotNumber].append([unix2javascript(float(dataPointTime)),float(dataPoint)])
                
                #Build ticks
                minTime,maxTime = getMinMaxListofLists(plotsData[plotNumber],0)
                
                minTime=  javascript2unix(minTime)
                maxTime = javascript2unix(maxTime)
                
                minTick.insert(plotNumber,datetime.fromtimestamp(minTime).strftime("%Y-%m-%d %H:%M"))
                maxTick.insert(plotNumber,datetime.fromtimestamp(maxTime).strftime("%Y-%m-%d %H:%M"))
                #for timestamp in range(int(minTime),int(maxTime),PLOT_STEP):
                #    plotsTicks[plotNumber].append(datetime.fromtimestamp(timestamp).strftime("%d %H:%M"))
                
                plotNumber=plotNumber+1
                
    #Build outlet switches dict
    outlets={}
    outletsServerDict = json.loads(serverDict["outlets"])
    for outlet in outletsServerDict:
        outlets[outlet] ={}
        outlets[outlet]["name"] = dataDictHead[outlet]["name"]
        outlets[outlet]["OpState"] = outletsServerDict[outlet]["OpState"]
        
        if outletsServerDict[outlet]["OpState"] ==  OpState.OK or outletsServerDict[outlet]["OpState"] == OpState.SwitchingOff:
            outlets[outlet]["Switch"] = "on"
        else:
            outlets[outlet]["Switch"]="off"
    
    return {"layout": site_layout(),
            "xdottree" : "",
            "server_dict" : serverDict,
            "page_title" : "Server View: " + str(serverName),
            "ServerLog" : str(serverLog),
            
            #Plot data
            "plotTitle"   : plotTitle,
            "plotYLabel" : plotYLabel,
            "plotYFormat" : plotYFormat,
            "plotsData"   : plotsData,
            #"plotsTicks"  : plotsTicks,
            "plotXLabel"  : plotXLabel,
            "minTick" : minTick,
            "maxTick" : maxTick,
            
            #outlets data
            "outletsDict" : json.dumps(outlets),
            "outlets" : outlets}
'''
@view_config(route_name='serverEdit',renderer="templates/server_edit.pt")
def server_edit_view(request):
    serverName = request.matchdict['serverName']
    
    SERVER_DIR = ClientCalls.config.get('main', 'SERVER_DIR')
    
    configPath =  os.path.join(SERVER_DIR,serverName) + ".ini"
    iniString = getINIFile(configPath)
    print iniString
    INIFileDict = getINIstringtoDict(iniString)
    
    serverDict = getServerView(serverName)
    
    return {"layout": site_layout(),
            "page_title" : "Server Edit: " + str(serverName),
            "server_dict" : serverDict,
            "INIFileDict" : INIFileDict}
'''
@view_config(renderer="templates/server_edit.pt",route_name='serverEdit')
def server_edit_view(request):
    serverName = request.matchdict['serverName']
    
    configPath= os.path.join(getServerFolder() , serverName + '.ini')
    INIFileDict = loadINIFileConfig(configPath)
    
    #testerType = INIFileDict["tester"]["type"]
    INIFileTemplate = _loadServerINITemplate()
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,INIFileDict)
    
    
    multiListChoices = _makeMultichoice("server","testers",lambda: getAvailableServerTesters(serverName),INIFileDict)
    multiListChoices = _makeMultichoice("server","outlets",lambda: getAvailableServerOutlets(serverName),INIFileDict,multiListChoices)
    
    multiListChoices = _makeMultichoice("server","dependencies",lambda: getServerDependencyMap(serverName),INIFileDict,multiListChoices)
    
    #multiListChoices = _makeSelectMulitChoice(testerType,"tester",getAvailableTestersList)

    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "configPath" : configPath,
            "serverName" : serverName,
            "multiListChoices" : multiListChoices,
            "page_title": "Server Edit: " + str(serverName)}

@view_config(renderer="templates/index.pt")
def index_view(request):
    '''
    View of the server network
    '''
    #get Dot data
    dot= getServerTree()
    
    #Add generate an xdot file from the dot we got from the server
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
    
    #get autocontrol stuff
    autoControlStatus = getAutoControlStatus()["status"]
    return {"layout": site_layout(),
            "page_title": "Server Network View",
            "autoControlStatus" : autoControlStatus,
            "xdottree" : gv.draw(format="xdot").replace('\n','\\n\\\n')}


@view_config(renderer="templates/about.pt", name="about.html")
def about_view(request):
    return {"layout": site_layout(),
            "page_title": "About"}

def _objectEditUrl(ObjectName,ObjectVar):
    ''' A callback that is used when return the object edit url path
    Here to remove code repetition 
    '''
    return "/" + ObjectName.lower() + "/" + ObjectVar + "/edit"

@view_config(renderer="templates/pdus_testers.pt", name="pdus")
def pdus_view(request):
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "ObjectList" : getPDUDict(),
            "ObjectName" : "PDU",
            "ObjectClassName" : "outlet",
            "ObjectURLCallback" : _objectEditUrl,
            "page_title": "PDUs"}

@view_config(renderer="templates/pdus_testers.pt", name="testers")
def testers_view(request):
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "ObjectList" : getTesterDict(),
            "ObjectName" : "tester",
            "ObjectClassName" : "tester",
            "ObjectURLCallback" : _objectEditUrl,
            "page_title": "Testers"}
    
@view_config(renderer="templates/pdus_testers.pt", name="servers")
def servers_view(request):
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "ObjectList" : getServerDict(),
            "ObjectName" : "server",
            "ObjectClassName" : "server",
            "ObjectURLCallback" : _objectEditUrl,
            "page_title": "Servers"}
    

def _servers_obj_add_list_view(request,obj,objDict,objGenerator):
    serverName = request.matchdict['serverName']
    
    for key in objDict.keys():
        objDict[key] = str(objDict[key][objGenerator]["comment"])

    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "TypeList" : objDict,
            "typeCreatePath" : "server/" + serverName + "/" + obj + "Create",
            "TypeCreateName" : "from which " + obj + " the outlet is located",
            "page_title": serverName + ": Add new Server "+ obj +" - Select " + objGenerator +" from list"
            }

@view_config(renderer="templates/add_pdu_or_tester_list.pt", route_name="servers_outlet_add_list_view")
def servers_outlet_add_list_view(request):
    return _servers_obj_add_list_view(request,"outlet",getPDUDict(),"PDU")

@view_config(renderer="templates/add_pdu_or_tester_list.pt", route_name="servers_test_add_list_view")
def servers_tester_add_list_view(request):
    return _servers_obj_add_list_view(request,"test",getTesterDict(),"tester")

def __fillINIwithTemplate(INIFileTemplate,INIFileDict={}):
    ''' Fill missing values in an INI config file with ones that exist in the template
    @param INIFileTemplate: The config template as a dict
    @param INIFileDict: The config file dict
    @return: The new INIFileDict with the missing fields
    '''
    for section in INIFileTemplate.keys():
        if section not in INIFileDict.keys():
            INIFileDict[section] = {}
        for item in INIFileTemplate[section].keys():
            if item not in INIFileDict[section]:
                INIFileDict[section][item] =  INIFileTemplate[section][item][1]
    return INIFileDict

def _obj_add_list_view(request,objGenerator,TypeList):
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "TypeList" : TypeList,
            "typeCreatePath" :  objGenerator.lower() + "Create",
            "TypeCreateName" : "type of " + objGenerator +" to create:",
            "page_title": "Add new " + objGenerator +" - Select type from list"
            }
    
@view_config(renderer="templates/add_pdu_or_tester_list.pt", name="pdus_add_list")
def pdu_add_list_view(request):
    return _obj_add_list_view(request,"PDU",sortDict(getAvailableOutletsList()))
    
@view_config(renderer="templates/add_pdu_or_tester_list.pt", name="testers_add_list")
def testers_add_list_view(request):
    return _obj_add_list_view(request,"tester",sortDict(getAvailableTestersList()))

def _makeSelectMulitChoice(existingType,objectType,item,getObjectDict,multiListChoices=None):
    ''' Make a multi select option for the select type
    @param existingType: The selected option
    @param objectType: The section to build
    @param item: The item to build
    @param getObjectCallback: the Dict holding the select list 
    @param multiListChoices: an existing multiListChoices dict (optional)
    @return: The updated multiListChoices dict
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
    
@view_config(renderer="templates/pdu_tester_create.pt", route_name="pduCreate")
def pdu_create(request):
    PDUType = request.matchdict['pduType']
    INIFileTemplate = _loadOutletINITemplate(PDUType)

    #Remove the outlet params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop("outletParams")
    except:
        pass

    INIFileTemplate['outlet']["name"] =["name",""]
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,{})    
    
    INIFileDict['outlet']["type"] = PDUType
    multiListChoices = _makeSelectMulitChoice(PDUType,"outlet","type",getAvailableOutletsList)
    
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),

            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),            
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "multiListChoices" : multiListChoices,
            "OBJnameSection" : "outlet",
            
            "configPathPrefix": getOutletFolder() + "/",
            "existingOBJCallback" : "checkExistingPDU" ,
            
            "page_title": "Add new PDU: " + PDUType
            }

@view_config(renderer="templates/pdu_tester_create.pt", route_name="testerCreate")
def tester_create(request):
    testerType = request.matchdict['testerType']
    INIFileTemplate = _loadTesterINITemplate(testerType)
    
    #Remove the tester params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop("testerParams")
    except:
        pass

    INIFileTemplate['tester']["name"] =["name",""]
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,{})    
    
    INIFileDict['tester']["type"] = testerType
    multiListChoices = _makeSelectMulitChoice(testerType,"tester","type",getAvailableTestersList)
    
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),

            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),            
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "multiListChoices" : multiListChoices,
            "OBJnameSection" : "tester",
            
            "configPathPrefix": getTesterFolder() + "/",
            "existingOBJCallback" : "checkExistingTesters" ,
            
            "page_title": "Add new Tester: " + testerType
            }
    
@view_config(renderer="templates/pdu_tester_create.pt", route_name="servers_outletCreate_view")
def server_outlet_create_view(request):
    serverName = request.matchdict['serverName']
    PDU = request.matchdict['PDU']
    
    tmpName = "outletParams"
    #serverName
    pduType = _loadPDUConfig(PDU)["outlet"]["type"]
    tmpINIFileTemplate = _loadOutletINITemplate(pduType)
    
    #Here we move the template dict to the right name
    
    INIFileTemplate = {}
    INIFileTemplate[tmpName] = tmpINIFileTemplate["outletParams"]
    INIFileTemplate[tmpName]["name"] =["name",""]
    INIFileTemplate[tmpName]["outlet"] =["select",True]
    
    
    #Remove the pdu params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop("outlet")
    except:
        pass
    
    INIFileDict = __fillINIwithTemplate(tmpINIFileTemplate)
    INIFileDict[tmpName]["outlet"] = PDU
    multiListChoices= _makeSelectMulitChoice(PDU,tmpName,"outlet",getPDUDict)
    
    configPath= os.path.join(getServerFolder() , serverName + '.ini')
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),

            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),            
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "multiListChoices" : multiListChoices,
            "OBJnameSection" : tmpName,
            "matchdict" : json.dumps(request.matchdict),
            
            "configPath": configPath,
            "existingOBJCallback" : "checkExistingServerOutlets" ,
            
            "page_title": serverName + ": Add new Outlet using " + PDU
            }

def _loadOutletINITemplate(outletType):
    ''' Get the outlet type template
    @param outletType: The type of the outlet 
    @return: Outlet ini template dict'''
    return loadINIFileTemplate(['conf_outlets/' + outletType + '.ini'] + ["outlets.ini"])

def _loadTesterINITemplate(testerType):
    ''' Get the outlet type template
    @param outletType: The type of the tester
    @return: Tester ini template dict'''
    return loadINIFileTemplate(['conf_testers/' + testerType + '.ini'] + ["testers.ini"])

def _loadServerINITemplate():
    ''' Get the serverNode template
    @return: Server ini template dict'''
    return loadINIFileTemplate("serverNodes.ini")

def _loadPDUConfig(PDUName):
    configPath= os.path.join(getOutletFolder() , PDUName + '.ini')
    return loadINIFileConfig(configPath)

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="pduEdit")
def pdu_edit_view(request):
    PDUName = request.matchdict['pduName']
    
    configPath= os.path.join(getOutletFolder() , PDUName + '.ini')
    INIFileDict = _loadPDUConfig(PDUName)
    
    outletType = INIFileDict["outlet"]["type"]
    INIFileTemplate = _loadOutletINITemplate(outletType)
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,INIFileDict)
    
    #Remove the outlet params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop("outletParams")
    except:
        pass
    
    multiListChoices = _makeSelectMulitChoice(outletType,"outlet","type",getAvailableOutletsList)

    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "configPath" : configPath,
            "multiListChoices" : multiListChoices,
            "page_title": "PDU Edit: " + str(PDUName)}

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="testerEdit")
def tester_edit_view(request):
    TesterName = request.matchdict['testerName']
    
    configPath= os.path.join(getTesterFolder() , TesterName + '.ini')
    INIFileDict = loadINIFileConfig(configPath)
    
    testerType = INIFileDict["tester"]["type"]
    INIFileTemplate = _loadTesterINITemplate(testerType)
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,INIFileDict)
    
    #Remove the outlet params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop("testerParams")
    except:
        pass
    
    multiListChoices = _makeSelectMulitChoice(testerType,"tester","type",getAvailableTestersList)

    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "configPath" : configPath,
            "multiListChoices" : multiListChoices,
            "page_title": "Tester Edit: " + str(TesterName)}


def _makeMultichoice(section,option,multiListChoicesCallback,INIFileDict,multiListChoices=None):
    ''' Generate a multilist format for a template. So it can be rendered on a template
    @param section: The option section in the ini file
    @param option: The name of the option in the ini file
    @param multiListChoicesCallback: a callback function the returns a dict of the available options
    @param INIFileDict: An INI file dict that holds the list of selected choices
    @param multiListChoices: If there is a multiListChoices dict you want to append the existing configuration to
    @return: a multiListChoices dict ready to be rendred in a template
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

@view_config(renderer="templates/config.pt", name="config")
def config_view(request):
    
    pluginList = getINIFolderTemplate("plugins")
    
    configPath = "config.ini"
    INIFileDict = loadINIFileConfig(configPath)
    iniTemplate = loadINIFileTemplate([configPath] + pluginList)
    INIFileDict = __fillINIwithTemplate(iniTemplate,INIFileDict)
    
    multiListChoices = _makeMultichoice("plugins","pluginlist",getAvailablePluginsList,INIFileDict)        
    
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),
            "page_title": "General",
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : iniTemplate,
            "configPath" : configPath,
            "multiListChoices" : multiListChoices}


@view_config(renderer="json", name="configSend.json")
def updates_view(request):
    rawiniDict={}
    iniDict={}
    
    jsonData = request.json_body["configINI"]
    iniFilePath = request.json_body["path"]
    
    for i in jsonData:
        rawiniDict[i["name"]] =i["value"]
    
    for key in rawiniDict.keys():
        dataKey = key.split("$")
        section = dataKey[0]
        item = dataKey[1]
        
        if not section in iniDict:
            iniDict[section] = {}
        
        multiListItem = item.split("*")
        if len(multiListItem) > 1: #multilist item detection
            item= multiListItem[0]
            itemOption=multiListItem[1]
            if not item in iniDict[section]:
                iniDict[section][item]=[]
            
            if itemOption != "__null__":
                iniDict[section][item].append(itemOption)
            
        else: #normal non-multilist item
            iniDict[section][item] = rawiniDict[key] 
    
    for section in iniDict.keys():
        for item in iniDict[section]:
            if type(iniDict[section][item]) == list:
                iniDict[section][item]=json.dumps(iniDict[section][item])
    
    
    #convert sections that were nameless on creation
    if "outletParams" in iniDict.keys():
        iniDict[iniDict["outletParams"]["name"]] = iniDict[section]
        iniDict.pop("outletParams")   
    
    #Add sections that were dropped
    oldINIDict = loadINIFileConfig(iniFilePath)
    for section in oldINIDict.keys():
        if not section in iniDict:
            iniDict[section] = oldINIDict[section]
            
    
    result =  setINIFile(iniFilePath,iniDict)
    
    returnValue={}
    
    if result["succeeded"] == "True":
        returnValue["color"] = "green"
        returnValue["message"] ="Configuration saved"
    else:
        returnValue["color"] = "red"
        returnValue["message"] ="Configuration failed"
    return returnValue

@view_config(renderer="json", name="sendOckleCommand.json")
def sendOckleCommand(request):
    command = request.json_body["command"]
    
    dataDict = {}
    try:
        dataDict = request.json_body["dataDict"]
    except:
        pass
    
    print command
    if command == "restart":
        restartOckle()
    
    if command == "checkExistingPDU":
        try:
            return {"reply" : dataDict["name"] in getPDUDict()}
        except:
            return {"reply" : "Error"}
    
    if command == "checkExistingTesters":
        try:
            return {"reply" : dataDict["name"] in getTesterDict()}
        except:
            return {"reply" : "Error"}
        
    #TODO write this!
    if command == "checkExistingServerOutlets":
        try:
            return {"reply" : dataDict["name"] in getAvailableServerOutlets(dataDict["matchdict"]["serverName"])}
        except:
            return {"reply" : "Error"}
    
    if command == "switchOutlet":
        switchOutlet(dataDict)
        
    return dataDict