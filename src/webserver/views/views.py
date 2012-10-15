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
from ockle_client.ClientCalls import switchControl
from ockle_client.ClientCalls import runTest
from ockle_client.ClientCalls import getServerView
from ockle_client.ClientCalls import getAutoControlStatus
from ockle_client.ClientCalls import setAutoControlStatus
from ockle_client.ClientCalls import getINIFile
from ockle_client.ClientCalls import setINIFile
from ockle_client.ClientCalls import deleteINIFile
from ockle_client.ClientCalls import deleteINISection
from ockle_client.ClientCalls import restartOckle
from ockle_client.ClientCalls import getAvailablePluginsList
from ockle_client.ClientCalls import getAvailablePDUsList
from ockle_client.ClientCalls import getAvailableTestersList
from ockle_client.ClientCalls import getAvailableControllersList
from ockle_client.ClientCalls import getAvailableServerOutlets
from ockle_client.ClientCalls import getAvailableServerTesters
from ockle_client.ClientCalls import getAvailableServerControls
from ockle_client.ClientCalls import getPDUDict
from ockle_client.ClientCalls import getTesterDict
from ockle_client.ClientCalls import getControllerDict
from ockle_client.ClientCalls import getServerDict
from ockle_client.ClientCalls import loadINIFileTemplate
from ockle_client.ClientCalls import loadINIFileConfig
from ockle_client.ClientCalls import getPDUFolder
from ockle_client.ClientCalls import getTesterFolder
from ockle_client.ClientCalls import getControllerFolder
from ockle_client.ClientCalls import getServerFolder
from ockle_client.ClientCalls import getServerDependencyMap
from ockle_client.ClientCalls import serversDependent
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
def server_info_view(request):
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
    
    #fix strange bug that servers with spaces get " symbols on the canviz tree
    if serverName.startswith('"'):
        serverName = serverName[1:-1]
        
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
    
    def generatePlot(keySlicePrefix,plotTitle,plotYFormat,plotYLabel,plotsData,minTick,maxTick,plotNumber):
        for outletKey in slicedict(dataDictHead,keySlicePrefix).keys():
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
    generatePlot("outlet",plotTitle,plotYFormat,plotYLabel,plotsData,minTick,maxTick,plotNumber)
    generatePlot("control",plotTitle,plotYFormat,plotYLabel,plotsData,minTick,maxTick,plotNumber)
    
    def buildServerObjDict(objs):            
        #Build outlet switches dict
        outlets={}
        outletsServerDict = json.loads(serverDict[objs])
        for outlet in outletsServerDict:
            outlets[outlet] ={}
            outlets[outlet]["name"] = dataDictHead[outlet]["name"]
            outlets[outlet]["OpState"] = outletsServerDict[outlet]["OpState"]
            
            onOpStates = [OpState.OK,OpState.SwitchingOff,OpState.forcedOn]
            if outletsServerDict[outlet]["OpState"] in onOpStates:
                outlets[outlet]["Switch"] = "on"
            else:
                outlets[outlet]["Switch"]="off"
        return outlets
    
    outlets = buildServerObjDict("outlets")
    controls = buildServerObjDict("controls")
    tests = json.loads(serverDict["tests"])
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
            "outlets" : outlets,
            
            #controls data
            "controls": controls,
            "controlsDict": json.dumps(controls),
            
            #tests Data
            "tests": tests,
            "testsDict": json.dumps(tests),
            }

@view_config(renderer="templates/server_edit.pt",route_name='serverEdit')
def server_edit_view(request):
    serverName = request.matchdict['serverName']
    
    configPath= _getServerConfigPath(serverName)
    INIFileDict = _loadServerConfig(serverName)
    
    #testerType = INIFileDict["tester"]["type"]
    INIFileTemplate = _loadServerINITemplate()
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,INIFileDict)
    
    multiListChoices = _makeMultichoice("server","tests",lambda: getAvailableServerTesters(serverName),INIFileDict)
    multiListChoices = _makeMultichoice("server","outlets",lambda: getAvailableServerOutlets(serverName),INIFileDict,multiListChoices)
    multiListChoices = _makeMultichoice("server","controls",lambda: getAvailableServerControls(serverName),INIFileDict,multiListChoices)
    
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
            "deleteCallback" : "server",
            "objectName" : str(serverName),
            "redirectURL" : "/",
            
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
    gv.node_attr.update(title="\\\N")
    gv.node_attr.update(tooltip="\\\N")
    gv.node_attr.update(shape="ellipse")
    gv.node_attr.update(style="filled")
    gv.node_attr.update(fillcolor="#CBE6FF")
    gv.node_attr.update(fontname="Arial")
    gv.graph_attr.update(bgcolor="#F4F4F4")

    
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
            "ObjectClassName" : "pdu",
            "AddURL" : "/pdus_add_list",
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
            "AddURL" : "/testers_add_list",
            "ObjectURLCallback" : _objectEditUrl,
            "page_title": "Testers"}
    
@view_config(renderer="templates/pdus_testers.pt", name="controllers")
def controllers_view(request):
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "ObjectList" : getControllerDict(),
            "ObjectName" : "controller",
            "ObjectClassName" : "controller",
            "AddURL" : "/controllers_add_list",
            "ObjectURLCallback" : _objectEditUrl,
            "page_title": "Controllers"}
    
@view_config(renderer="templates/pdus_testers.pt", name="servers")
def servers_view(request):
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "ObjectList" : getServerDict(),
            "ObjectName" : "server",
            "ObjectClassName" : "server",
            "AddURL" : "/server_add",
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
    return _servers_obj_add_list_view(request,"outlet",getPDUDict(),"pdu")

@view_config(renderer="templates/add_pdu_or_tester_list.pt", route_name="servers_test_add_list_view")
def servers_test_add_list_view(request):
    return _servers_obj_add_list_view(request,"test",getTesterDict(),"tester")

@view_config(renderer="templates/add_pdu_or_tester_list.pt", route_name="servers_control_add_list_view")
def servers_control_add_list_view(request):
    return _servers_obj_add_list_view(request,"control",getControllerDict(),"controller")

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
    return _obj_add_list_view(request,"PDU",sortDict(getAvailablePDUsList()))
    
@view_config(renderer="templates/add_pdu_or_tester_list.pt", name="testers_add_list")
def testers_add_list_view(request):
    return _obj_add_list_view(request,"tester",sortDict(getAvailableTestersList()))

@view_config(renderer="templates/add_pdu_or_tester_list.pt", name="controllers_add_list")
def controllers_add_list_view(request):
    return _obj_add_list_view(request,"controller",sortDict(getAvailableControllersList()))

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
 
def _objGenerator_create(request,objName,objGenerator,loadObjGeneratorTemplate,getAvailableObjGeneratorsList,getObjGeneretorFolder):
    ''' Create a dict for an object Generator page
    @param objName: The name of the Server Object
    @param objGenerator: The name of the Server Object Generator
    @param loadObjGeneratorTemplate:  a callback to get the template of the object Generator
    @param getAvailableObjGeneratorsList: Get a list of the object generators
    @param getObjGeneretorFolder: Get the folder of the object generator
    @return: a dict ready to be rendered
    '''
    PDUType = request.matchdict[objGenerator.lower() + 'Type']
    INIFileTemplate = loadObjGeneratorTemplate(PDUType)

    #Remove the outlet params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop(objName +"Params")
    except:
        pass

    INIFileTemplate[objGenerator.lower()]["name"] =["name",""]
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,{})    
    
    INIFileDict[objGenerator.lower()]["type"] = PDUType
    multiListChoices = _makeSelectMulitChoice(PDUType,objGenerator.lower(),"type",getAvailableObjGeneratorsList)
    
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),

            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),            
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "multiListChoices" : multiListChoices,
            "OBJnameSection" : objGenerator.lower(),
            
            "configPathPrefix": getObjGeneretorFolder() + "/",
            "existingOBJCallback" : "checkExisting"+ objGenerator +"s" ,
            
            "page_title": "Add new "+ objGenerator + ": " + PDUType
            }    

@view_config(renderer="templates/pdu_tester_create.pt", route_name="pduCreate")
def pdu_create(request):
    return _objGenerator_create(request,"outlet","PDU",_loadPDUINITemplate,getAvailablePDUsList,getPDUFolder)

@view_config(renderer="templates/pdu_tester_create.pt", route_name="testerCreate")
def tester_create(request):
    return _objGenerator_create(request,"test","Tester",_loadTesterINITemplate,getAvailableTestersList,getTesterFolder)

@view_config(renderer="templates/pdu_tester_create.pt", route_name="controllerCreate")
def controller_create(request):
    return _objGenerator_create(request,"control","Controller",_loadControllerINITemplate,getAvailableControllersList,getControllerFolder)

@view_config(renderer="templates/pdu_tester_create.pt", name="server_add")
def server_create_view(request):
    INIFileTemplate = _loadServerINITemplate()
    
    INIFileTemplate['server']["name"] =["name",""]
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,{})    
    
    
    
    INIFileDict['server']["tests"] =[]
    INIFileDict['server']["outlets"] =[]
    INIFileDict['server']["controls"] =[]
    INIFileDict['server']["dependencies"] =[]
    
    multiListChoices = _makeMultichoice("server","tests",lambda: {},INIFileDict)
    multiListChoices = _makeMultichoice("server","outlets",lambda: {},INIFileDict,multiListChoices)
    multiListChoices = _makeMultichoice("server","controls",lambda: {},INIFileDict,multiListChoices)
    multiListChoices = _makeMultichoice("server","dependencies",lambda: {},INIFileDict,multiListChoices)
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),

            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),            
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "multiListChoices" : multiListChoices,
            "OBJnameSection" : "server",
            
            "configPathPrefix": getServerFolder() + "/",
            "existingOBJCallback" : "checkExistingServers" ,
            
            "page_title": "Add new Server"
            }

def _server_obj_create(request,obj,objGenerator,objGeneratorConfigCallback,objGeneratorTemplateCallback,getObjGeneratorsCallback,objNameExistJavascriptCallback):
    serverName = request.matchdict['serverName']
    PDU = request.matchdict[objGenerator]
    
    tmpName =  obj +"Params"
    #serverName
    pduType = objGeneratorConfigCallback(PDU)[objGenerator.lower()]["type"]
    tmpINIFileTemplate = objGeneratorTemplateCallback(pduType)
    
    #Here we move the template dict to the right name
    
    INIFileTemplate = {}
    INIFileTemplate[tmpName] = {}
    try:
        INIFileTemplate[tmpName] = tmpINIFileTemplate[obj +"Params"]
    except KeyError:
        pass    
    
    INIFileTemplate[tmpName]["name"] =["name",""]
    INIFileTemplate[tmpName][objGenerator.lower()] =["select",True]
    
    
    #Remove the pdu params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop(objGenerator.lower())
    except KeyError:
        pass
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate)
    try:
        INIFileDict[tmpName][objGenerator.lower()] = PDU
    except KeyError:
        INIFileDict[tmpName] = {}
        INIFileDict[tmpName][objGenerator.lower()] = PDU
        
    multiListChoices= _makeSelectMulitChoice(PDU,tmpName,objGenerator.lower(),getObjGeneratorsCallback)
    
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
            "changeSavePathToName" : 'false',
            
            "configPath": configPath,
            "existingOBJCallback" : objNameExistJavascriptCallback,
            
            "page_title": serverName + ": Add new " + obj +" using " + PDU
            }

def _server_obj_edit_view(request,obj,objGenerator,objGeneratorConfigCallback,getObjGeneratorsCallback,objGeneratorTemplateCallback):
    ''' Get the edit dict of a server object (like outlet, tester, etc)
    @param obj: the name of the object in the server (eg. outlet)
    @param objName: The name of the object
    @param objGenerator: the name of the object generator (eg. pdu)
    @param objGeneratorConfigCallback: a callback the returns the object's config dict 
    @param getObjGeneratorsCallback: A callback that gets the available object generators
    @param objGeneratorTemplateCallback: A callback that gets the template dict of the object generator
    @param existingOBJJavascriptCallback: The ockle javascript command to check if 
    @return: dict for the edit view
    '''
    serverName = request.matchdict['serverName']
    objName = request.matchdict[obj]
    objParam = obj +  "Params"
    
    configPath= _getServerConfigPath(serverName)
    tmpINIFileDict = _loadServerConfig(serverName)
    INIFileDict = OrderedDict() 
    INIFileDict[objName] = tmpINIFileDict[objName]
    objGeneratorName =  INIFileDict[objName][objGenerator.lower()]
    
    objType = objGeneratorConfigCallback(objGeneratorName)[objGenerator.lower()]["type"]
    INIFileTemplate = objGeneratorTemplateCallback(objType)
    
    #pop the main dict
    INIFileTemplate.pop(objGenerator.lower())
    
    if not objParam in INIFileTemplate:
        INIFileTemplate[objParam] = {}
    
    #add the type name
    INIFileTemplate[objParam][objGenerator.lower()] =["select",True]
    
    #Move outlet Params to the right name
    INIFileTemplate[objName] = INIFileTemplate[objParam]
    INIFileTemplate.pop(objParam)
    
    multiListChoices= _makeSelectMulitChoice(objGeneratorName,objName,objGenerator.lower(),getObjGeneratorsCallback)
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,INIFileDict)
    
    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),

            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),            
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "multiListChoices" : multiListChoices,
            "OBJnameSection" : objName,
            "matchdict" : json.dumps(request.matchdict),
            "changeSavePathToName" : 'false',
            
            #Name field variables
            "configPath": configPath,
            #"existingOBJCallback" : existingOBJJavascriptCallback,
            
            #delete variables
            "deleteCallback" : obj,
            "objectName" : objName,
            "redirectURL" : "/server/" + serverName + "/edit" ,
            #section delete stuff
            "sectionDelete" : json.dumps({"sectionDelete" : objName}), #we are deleting a section only
            
            "page_title": serverName + ": Edit " + obj +" " + objName
            }

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="servers_outletEdit_view")
def server_outlet_edit_view(request):
    return _server_obj_edit_view(request,"outlet","PDU",_loadPDUConfig,getPDUDict,_loadPDUINITemplate)

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="servers_testEdit_view")
def server_test_edit_view(request):
    return _server_obj_edit_view(request,"test","tester",_loadTesterConfig,getTesterDict,_loadTesterINITemplate)

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="servers_controlEdit_view")
def server_control_edit_view(request):
    return _server_obj_edit_view(request,"control","controller",_loadControllerConfig,getControllerDict,_loadControllerINITemplate)

@view_config(renderer="templates/pdu_tester_create.pt", route_name="servers_outletCreate_view")
def server_outlet_create_view(request):
    return _server_obj_create(request,"outlet","PDU",_loadPDUConfig,_loadPDUINITemplate,getPDUDict,"checkExistingServerOutlets")

@view_config(renderer="templates/pdu_tester_create.pt", route_name="servers_testCreate_view")
def server_test_create_view(request):
    return _server_obj_create(request,"test","tester",_loadTesterConfig,_loadTesterINITemplate,getTesterDict,"checkExistingServerTests")

@view_config(renderer="templates/pdu_tester_create.pt", route_name="servers_controlCreate_view")
def server_control_create_view(request):
    return _server_obj_create(request,"control","controller",_loadControllerConfig,_loadControllerINITemplate,getControllerDict,"checkExistingServerControls")

def _loadPDUINITemplate(outletType):
    ''' Get the outlet type template
    @param outletType: The type of the outlet 
    @return: Outlet ini template dict'''
    return loadINIFileTemplate(['conf_outlets/' + outletType + '.ini'] + ["outlets.ini"])

def _loadTesterINITemplate(testerType):
    ''' Get the outlet type template
    @param outletType: The type of the tester
    @return: Tester ini template dict'''
    return loadINIFileTemplate(['conf_testers/' + testerType + '.ini'] + ["testers.ini"])

def _loadControllerINITemplate(controllerType):
    ''' Get the outlet type template
    @param outletType: The type of the tester
    @return: Tester ini template dict'''
    return loadINIFileTemplate(['conf_controllers/' + controllerType + '.ini'] + ["controllers.ini"])

def _loadServerINITemplate():
    ''' Get the serverNode template
    @return: Server ini template dict'''
    return loadINIFileTemplate("serverNodes.ini")

def _loadPDUConfig(PDUName):
    configPath= os.path.join(getPDUFolder() , PDUName + '.ini')
    return loadINIFileConfig(configPath)

def _loadTesterConfig(testerName):
    configPath= os.path.join(getTesterFolder() , testerName + '.ini')
    return loadINIFileConfig(configPath)

def _loadControllerConfig(controllerName):
    configPath= os.path.join(getControllerFolder() , controllerName + '.ini')
    return loadINIFileConfig(configPath)

def _getServerConfigPath(serverName):
    return os.path.join(getServerFolder() , serverName + '.ini')

def _loadServerConfig(serverName):
    configPath= _getServerConfigPath(serverName)
    return loadINIFileConfig(configPath)

def _objGenerator_edit_view(request,objName,objGenerator,objURLName,getObjGenertorFolderCallback,objGeneratorConfigCallback,objGeneratorTemplateCallback,getAvilableObjGenetorsList):   
    ''' Make an edit view for an object generator (like a PDU or tester)
    @param request: The request from pyramid
    @param objName: the object name
    @param objGenerator: The name of the object generator
    @param objURLName: The url name that holds the name of the current object we are editing
    @param getObjGenertorFolderCallback: A function that returns the path of the object generator folder
    @param objGeneratorConfigCallback: A function the returns the object generator config
    @param objGeneratorTemplateCallback: A function that returns the template of the current object generator
    @param getAvilableObjGenetorsList: A callback that returns the current available object generators
    @return: A ready to render dict for the edit page
    '''
    PDUName = request.matchdict[objURLName]
    
    configPath= os.path.join(getObjGenertorFolderCallback() , PDUName + '.ini')
    INIFileDict = objGeneratorConfigCallback(PDUName)
    
    outletType = INIFileDict[objGenerator.lower()]["type"]
    INIFileTemplate = objGeneratorTemplateCallback(outletType)
    
    INIFileDict = __fillINIwithTemplate(INIFileTemplate,INIFileDict)
    
    #Remove the obj params if exist, we handle them in the server section
    try:
        INIFileTemplate.pop(objName + "Params")
    except:
        pass
    
    multiListChoices = _makeSelectMulitChoice(outletType,objGenerator.lower(),"type",getAvilableObjGenetorsList)

    return {"layout": site_layout(),
            "config_sidebar_head" : config_sidebar_head(),
            "config_sidebar_body" : config_sidebar_body(),
            "INI_InputArea_head" : INI_InputArea_head(),
            "INI_InputArea_body" : INI_InputArea_body(),
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : INIFileTemplate,
            "configPath" : configPath,
            "multiListChoices" : multiListChoices,
            "page_title": objGenerator + " Edit: " + str(PDUName),
            
            #delete-variables
            "deleteCallback" : objGenerator.lower(),
            "objectName" : PDUName,
            "redirectURL" : "/" + objGenerator.lower()  +"s"}

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="pduEdit")
def pdu_edit_view(request):
    return _objGenerator_edit_view(request,"outlet","PDU",'pduName',getPDUFolder,_loadPDUConfig,_loadPDUINITemplate,getAvailablePDUsList) 

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="testerEdit")
def tester_edit_view(request):
    return _objGenerator_edit_view(request,"test","Tester",'testerName',getTesterFolder,_loadTesterConfig,_loadTesterINITemplate,getAvailableTestersList)

@view_config(renderer="templates/pdu_tester_edit.pt", route_name="controllerEdit")
def controller_edit_view(request):
    return _objGenerator_edit_view(request,"control","Controller",'controllerName',getControllerFolder,_loadControllerConfig,_loadControllerINITemplate,getAvailableControllersList)

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
    #TODO find a way to make this not hard-coded
    PARAMS_LIST=["outletParams","testParams","controlParams"]
    for param in PARAMS_LIST:
        if param in iniDict.keys():
            iniDict[iniDict[param]["name"]] = iniDict[section]
            iniDict[iniDict[param]["name"]].pop("name")
            iniDict.pop(param)
    
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

def serverDelete(name,objectName,path):
    dependent = serversDependent(name)
    if len(dependent) == 0:
        return True
    return "The following servers are dependent on it: " +", ".join(serversDependent(name))

def pduDelete(name,objectName,path):
    return _objectGenertorDelete("PDU",name,objectName,path)

def testerDelete(name,objectName,path):
    return _objectGenertorDelete("tester",name,objectName,path)

def controllerDelete(name,objectName,path):
    return _objectGenertorDelete("controller",name,objectName,path)

def _objectGenertorDelete(objectGenerator,name,objectName,path):
    serversUsing = {}
    servers = getServerDict()
    for serverName in servers.keys():
        for section in servers[serverName]:
            
            #Try to see if we have a section at all
            try:
                if servers[serverName][section][objectGenerator.lower()] == name:
                    if not serverName in serversUsing.keys():
                        serversUsing[serverName] = []
                    serversUsing[serverName].append(section)
            except:
                pass
    #formatting
    for serverName in serversUsing.keys():
        serversUsing[serverName] = ",".join(serversUsing[serverName])
        
    if len(serversUsing.keys()) == 0:
        return True
    returnString =""
    for server in serversUsing:
        returnString = returnString +  server + " in: " + serversUsing[serverName] + ". "
    return objectGenerator + " is being used in these servers - " + returnString

def _serverObjectDelete(objectType,name,objectName,path):
    item = objectType+ "s"
    serverDict = loadINIFileConfig(path)
    
    if not serverDict["server"][item].startswith("["):
        serverDict["server"][item] = '["' + serverDict["server"][item] + '"]'
        
    enabledOutlets = json.loads(serverDict["server"][item])
    if name in enabledOutlets:
        return "Please uncheck " + objectType + " in server before deleting."
    return True


def serverOutletDelete(name,objectName,path):
    return _serverObjectDelete("outlet",name,objectName,path)

def serverTestDelete(name,objectName,path):
    return _serverObjectDelete("test",name,objectName,path)

def serverControlDelete(name,objectName,path):
    return _serverObjectDelete("control",name,objectName,path)

def deleteObject(dataDict):
    DELETE_CALLBACK = {"server": serverDelete,
                       "pdu"   : pduDelete,
                       "tester": testerDelete,
                       "controller": controllerDelete,
                       "outlet": serverOutletDelete,
                       "test"  : serverTestDelete,
                       "control"  : serverControlDelete}
    
    returnValue = {}
    outcome = DELETE_CALLBACK[dataDict["object"]](dataDict["name"],dataDict["object"],dataDict["path"])
    if outcome != True:
        returnValue["color"] = "red" 
        returnValue["message"] = "Can't delete " + dataDict["object"] + ".  " + outcome
    else:
        out={}
        if "sectionDelete" in dataDict:
            out = deleteINISection(dataDict["sectionDelete"],dataDict["path"])
        else:
            out = deleteINIFile(dataDict["path"])
            
        if out["succeeded"] == "True":
            returnValue["color"] = "green"
            returnValue["message"] = dataDict["name"] + " deleted successfully"
        else:
            returnValue["color"] = "red"
            try:
                returnValue["message"] = "Can't delete. " + out["error"]
            except:
                returnValue["message"] = "Can't delete, unknown error"
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
    
    if command == "checkExistingPDUs":
        try:
            return {"reply" : dataDict["name"] in getPDUDict()}
        except:
            return {"reply" : "Error"}
    
    if command == "checkExistingTesters":
        try:
            return {"reply" : dataDict["name"] in getTesterDict()}
        except:
            return {"reply" : "Error"}
    
    if command == "checkExistingServerOutlets":
        try:
            return {"reply" : dataDict["name"] in getAvailableServerOutlets(dataDict["matchdict"]["serverName"])}
        except:
            return {"reply" : "Error"}
    
    if command == "checkExistingServerTests":
        try:
            return {"reply" : dataDict["name"] in getAvailableServerTesters(dataDict["matchdict"]["serverName"])}
        except:
            return {"reply" : "Error"}
    
    if command == "checkExistingServerControls":
        try:
            return {"reply" : dataDict["name"] in getAvailableServerControls(dataDict["matchdict"]["serverName"])}
        except:
            return {"reply" : "Error"}
        
    if command == "checkExistingServers":
        try:
            return {"reply" : dataDict["name"] in getServerDict()}            
        except:
            return {"reply" : "Error"}
            
    if command == "deleteObject":
        return deleteObject(dataDict)
    
    if command == "switchOutlet":
        return switchOutlet(dataDict)
        
    if command == "switchControl":
        return switchControl(dataDict)
    
    if command == "runTest":
        return runTest(dataDict)
    
    if command == "setAutoControlStatus":
        return setAutoControlStatus(dataDict)
        
    return dataDict