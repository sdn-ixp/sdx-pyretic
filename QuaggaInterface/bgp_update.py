#############################################
# SDX-Quagga Integration                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import sys,os
import json

class aspath():
    def __init__(self,refcnt=0,val=''):
        self.refcnt=refcnt
        self.val=val # string with actual ASPATH info, ignored the as_segments here

    def reprJSON(self):
        return dict(refcnt=self.refcnt,val=self.val)

class community():
    def __init__(self,refcnt=0,size=0,val=0,commVal=''):
        self.refcnt=refcnt
        self.size=size
        self.val=val
        self.commVal=commVal

class attr_extra():
    def __init__(self,aggregator_addr='',originator_id='',weight=0,aggregator_as='',
            mp_nexthop_len=''): # ignored ecommunity, cluster_list, transit
        self.aggregator_addr=aggregator_addr
        self.originator_id=originator_id
        self.aggregator_as=aggregator_as
        self.mp_nexthop_len=mp_nexthop_len

class attr():
    def __init__(self,aspath=aspath(),community=community(),attr_extra=attr_extra(),refcnt=0,
            flag='',nexthop='',med=0,local_pref=0,origin=''): # ignored pathlimit
        self.aspath=aspath
        self.community=community
        self.attr_extra=attr_extra
        self.refcnt=refcnt
        self.flag=flag
        self.nexthop=nexthop
        self.med=med
        self.local_pref=local_pref
        self.origin=origin

    def reprJSON(self):
        # limiting the number of JSON variables for now
        return dict(aspath=self.aspath,nexthop=self.nexthop,origin=self.origin,med=self.med)

class info():
    def __init__(self,peer='',attr=attr(),uptime='',infoType='',subType=''):
        self.peer=peer
        self.attr=attr
        self.uptime=uptime
        self.infoType=infoType
        self.subType=subType

    def reprJSON(self):
       return dict(peer=self.peer,attr=self.attr,uptime=self.uptime,infoType=self.infoType,subtype=self.subType)

class prefix:
    def __init__(self,family='',prefixlen=0,address=''):
        self.family=family
        self.prefixlen=prefixlen
        self.address=address



class jmessage():
    def __init__(self,tag='',type='',rib=None,update=info(),prefix=prefix()):
        self.tag=tag
        self.type=type
        self.rib=rib
        self.update=update
        self.prefix=prefix
