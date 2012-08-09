#pyramid stuff
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import Response

#ockle stuff
from ockle_client.ClientCalls import getServerTree
from ockle_client.ClientCalls import getServerView
from ockle_client.ClientCalls import getAutoControlStatus
from ockle_client.ClientCalls import getINIFile
from ockle_client.ClientCalls import getAvailablePluginsList
from ockle_client.DBCalls import getServerStatistics
from common.common import OpState
from common.common import slicedict
from common.common import configToDict
from plugins.Log import DATA_NAME_TO_UNITS
from plugins.Log import DATA_NAME_TO_UNITS_NAME

#config stuff
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from common.common import getINITemplate

#graphviz
import pygraphviz as pgv

import time
from datetime import datetime
import json

#plot settings
PLOT_STEP=3600 #What is the step length of the graph
STATISTICS_WINDOW=60*60*3#How far back should the log show

@view_config(route_name='serverView',renderer="templates/server_info.pt")
def serverPage(request):
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
                    dataPoint=dataDict[outletKey][dataKey]
                    
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
    print serverDict
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

def site_layout():
    renderer = get_renderer("templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout

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

@view_config(renderer="templates/config.pt", name="config")
def config_view(request):
    configPath = "config.ini"
    multiListChoices={}
    iniTemplate = getINITemplate(configPath)
    
    iniString = getINIFile(configPath)
    iniFile = StringIO(iniString)
    iniConfig = SafeConfigParser()
    iniConfig.readfp(iniFile)
    INIFileDict = configToDict(iniConfig)
    
    for section in iniTemplate.keys():
        for item in iniTemplate[section].keys():
            iniTemplate[section][item] = json.loads(iniTemplate[section][item])
    
    #build list of checked plugins multilist
    selectedPlugins = json.loads(INIFileDict["plugins"]["pluginlist"])
    multiListChoices["plugins"]={}
    
    #TODO: perhaps we could un-hardcode this somehow
    multiListChoices["plugins"]["pluginlist"]=getAvailablePluginsList()
    for key in multiListChoices["plugins"]["pluginlist"].keys():
        multiListChoices["plugins"]["pluginlist"][key] = { "doc" : multiListChoices["plugins"]["pluginlist"][key] }
    
    for pluginName in multiListChoices["plugins"]["pluginlist"].keys():
        if pluginName in selectedPlugins:
            multiListChoices["plugins"]["pluginlist"][pluginName]["checked"]=True
        else:
            multiListChoices["plugins"]["pluginlist"][pluginName]["checked"]=False
            
    
    return {"layout": site_layout(),
            "page_title": "Configuration",
            "INIFileDict" : INIFileDict,
            "INIFileTemplate" : iniTemplate,
            "multiListChoices" : multiListChoices}
