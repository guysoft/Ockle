#!/usr/bin/env python
""" Ockle PDU and servers manager
A Raritan Dominion PX DPXR8A-16 PDU Outlet implementation

Created on Mar 7, 2012

@author: Guy Sheffer <guy.sheffer at mail.huji.ac.il>
"""
# GETNEXT Command Generator
from pysnmp.entity import engine, config
from pysnmp.carrier.asynsock.dgram import udp

from pysnmp.proto import rfc1902

# GET Command Generator
from pysnmp.entity.rfc3413.oneliner import cmdgen

##builder from http://pysnmp.sourceforge.net/faq.html#4
#from pysnmp.smi import builder

cmdGen = cmdgen.CommandGenerator()
mibBuilder = cmdGen.snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

def bool2int(bool):
    if bool:
        return 1
    return 0

def int2bool(int):
    if int == 1:
        return True
    return False

from OutletTemplate import OutletTemplate
class Raritan(OutletTemplate):
    ''' A Raritan Dominion PX DPXR8A-16 PDU
    '''
    def __init__(self,name,outletConfigDict,outletParams):
        print outletConfigDict,outletParams
        #mibSources = mibBuilder.getMibSources() + (
        #    builder.DirMibSource(os.path.dirname(sys.argv[0])),
        #    )
        
        #Store config data
        self.hostname = outletConfigDict['pdu']["pdu_ip"]
        self.hostnameport = int(outletConfigDict['pdu']["pdu_port"])
        self.outletNumber= int(outletParams["socket"])
        self.agentName= outletConfigDict['pdu']["agent_name"]
        self.ReadCommunity = outletConfigDict['pdu']["read_community"]
        self.WriteCommunity = outletConfigDict['pdu']["write_community"]
        
        OutletTemplate.__init__(self,name,outletConfigDict,outletParams)
        self.updateState()
        
        #init data Parameters
        self.updateData()
        return
    
    def _snmpGet(self,value):
        '''
        SNMP get call
        '''
        #print mibBuilder.getMibSources()
        
        errorIndication, errorStatus, \
                         errorIndex, varBinds = cmdGen.getCmd(
            # SNMP v1
        #    cmdgen.CommunityData('test-agent', 'public', 0),
            # SNMP v2
            cmdgen.CommunityData(self.agentName, self.ReadCommunity),
            # SNMP v3
        #    cmdgen.UsmUserData('test-user', 'authkey1', 'privkey1'),
            cmdgen.UdpTransportTarget((self.hostname, self.hostnameport)),
            # Plain OID
            #(1,3,6,1,2,1,1,1,0),
            value,
            #(1,3,6,1,2,1,2,2,1,2,2),
            #((mib-name, mib-symbol), instance-id)
            #(('PDU-MIB', 'sysObjectID'), 0)
            )
                    
        if errorIndication:
            print errorIndication
        else:
            if errorStatus:
                print '%s at %s\n' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
            else:
                for name, val in varBinds:
                    #print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
                    return name, val
        return None
    def _setOutletState(self,state):
        '''
        Set a given outlet to on or off
        '''
        value = bool2int(state)
        self._snmpSet((1,3,6,1,4,1,13742,4,1,2,2,1,3,self.outletNumber), rfc1902.Integer(value))
        return
    
    def setState(self,state):
        self._setOutletState(state)
        self.updateState()
        #TODO: make this more robust?
        if self.getState() == state:
            return True
        else:
            return False
    
    def _snmpSet(self,OID,Value):
        '''
        SNMP set call
        '''
        errorIndication, errorStatus, \
                 errorIndex, varBinds = cmdgen.CommandGenerator().setCmd(
        # SNMP v1
        #    cmdgen.CommunityData('test-agent', 'public', 0),
        # SNMP v2
        cmdgen.CommunityData(self.agentName, self.WriteCommunity),
        # SNMP v3
        #cmdgen.UsmUserData('test-user', 'authkey1', 'privkey1'),
    
        cmdgen.UdpTransportTarget((self.hostname, self.hostnameport)),
        # MIB symbol name, plain string value
        #((('SNMPv2-MIB', 'sysName'), 0), 'new name'),
        # Plain OID name, rfc1902 class instance value
        (OID, Value)
        )
        if errorIndication:
            print errorIndication
        else:
            if errorStatus:
                print '%s at %s\n' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
            '''
            else:
                for name, val in varBinds:
                    print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
            '''
        return
    def getState(self):
        return self.state
    
    def updateState(self):
        self.state=self._getOuteletState()
        
    def _getOuteletState(self):
        '''
        Get the state of an outlet in the PDU
        returns 0 for off, 1 for on
        '''
        try:
            oid,val= self._snmpGet((1,3,6,1,4,1,13742,4,1,2,2,1,3,self.outletNumber))
        except:
            val = 0
        return int2bool(val)
    
    def updateData(self):
        self.data["current"] = int(self._snmpGet((1,3,6,1,4,1,13742,4,1,2,2,1,4,int(self.outletNumber)))[1])
        return self.data
