#!/usr/bin/python

from pysnmp.entity import engine, config
from pysnmp.carrier.twisted.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv

from twisted.internet import reactor

import time
import binascii

# 企业微信 api 此处引用server酱代码
import json,requests,base64

WECOM_CID='wwxxxxxxxxxxxxxxxxxx'
WECOM_SECRET='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
WECOM_AID='xxxxxxxx'
WECOM_TOUID='@all'

def send_to_wecom(text,wecom_cid,wecom_aid,wecom_secret,wecom_touid='@all'):
    get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wecom_cid}&corpsecret={wecom_secret}"
    response = requests.get(get_token_url).content
    access_token = json.loads(response).get('access_token')
    if access_token and len(access_token) > 0:
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        data = {
            "touser":wecom_touid,
            "agentid":wecom_aid,
            "msgtype":"text",
            "text":{
                "content":text
            },
            "duplicate_check_interval":600
        }
        response = requests.post(send_msg_url,data=json.dumps(data)).content
        return response
    else:
        return False


# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Transport setup
# UDP over IPv4, first listening interface/port
config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTwistedTransport().openServerMode(('0.0.0.0', 162))
)

# SNMPv1/2c setup
# SecurityName <-> CommunityName mapping
config.addV1System(snmpEngine, 'my-area', 'public')

# Callback function for receiving notifications
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
#Do what you want to do
     snmpSource = ''
     snmpData = ''

     for  name, val in varBinds:
         if name.prettyPrint()=='1.3.6.1.6.3.18.1.3.0':
             snmpSource = val.prettyPrint() 
         if name.prettyPrint()=='1.3.6.1.4.1.6876.4.3.306.0':
             print(name.prettyPrint()+' : '+binascii.a2b_hex( val.prettyPrint()[2:] ).decode('utf-8') + '\n')
             snmpData = binascii.a2b_hex( val.prettyPrint()[2:] ).decode('utf-8')
         else:
             print(name.prettyPrint()+' : '+val.prettyPrint()+ '\n')

     if snmpData!='':
        print( send_to_wecom( 'FROM:' + snmpSource + ' ----\n' + snmpData, WECOM_CID, WECOM_AID, WECOM_SECRET, WECOM_TOUID ) )

# Register SNMP Application at the SNMP engine
ntfrcv.NotificationReceiver(snmpEngine, cbFun)

# Run Twisted main loop
reactor.run()

