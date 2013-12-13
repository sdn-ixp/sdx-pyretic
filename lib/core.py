################################################################################
#
#  <website link>
#
#  File:
#        core.py
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Laurent Vanbever
#        Arpit Gupta
#        Muhammad Shahbaz
#
#  Copyright notice:
#        Copyright (C) 2012, 2013 Georgia Institute of Technology
#              Network Operations and Internet Security Lab
#
#  Licence:
#        This file is part of the SDX development base package.
#
#        This file is free code: you can redistribute it and/or modify it under
#        the terms of the GNU Lesser General Public License version 2.1 as
#        published by the Free Software Foundation.
#
#        This package is distributed in the hope that it will be useful, but
#        WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#        Lesser General Public License for more details.
#
#        You should have received a copy of the GNU Lesser General Public
#        License along with the SDX source package.  If not, see
#        http://www.gnu.org/licenses/.
#

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.setOperation import *
from pyretic.sdx.lib.language import *
#from pyretic.sdx.lib.policy_converter import *
from pyretic.sdx.lib.vnhAssignment import *
## General imports
import json
from importlib import import_module
from ipaddr import IPv4Network
###
### SDX classes
###
# Need to automate generation of these data structures in future

prefix_2_participant={'100.0.0.0/16':{'A':['B'],'B':['C']},
                      '120.0.0.0/16':{'B':['A','C']},
                      '140.0.0.0/16':{'C':['B'],'B':['A']},
                      '150.0.0.0/16':{'C':['B'],'B':['A']},
                      }

participant_2_port={'A':{'A':[1],'B':[2],'C':[3],'D':[4]},
                      'B':{'A':[1],'B':[2,21,22],'C':[3],'D':[4]},
                      'C':{'A':[1],'B':[2],'C':[3],'D':[4]},
                      'D':{'A':[1],'B':[2],'C':[3],'D':[4]}
                      }
prefixes_announced={'pg1':{
                               'A':['p0'],
                               'B':['p1','p2','p3','p4','p6'],
                               'C':['p3','p4','p5','p6'],
                               'D':['p1','p2','p3','p4','p5','p6'],
                               }
                        }
# Set of prefixes for A's best paths
# We will get this data structure from RIB
participant_to_ebgp_nh_received = {
        'A' : {'p1':'D','p2':'D','p3':'D','p4':'C','p5':'C','p6':'C'}
    }

peer_groups={'pg1':[1,2,3,4]}
VNH_2_IP={'VNHB':'172.0.0.201','VNHC':'172.0.0.301','VNHA':'172.0.0.101','VNHD':'172.0.0.401'}
VNH_2_mac={'VNHA':'A1:A1:A1:A1:A1:00','VNHC':'C1:C1:C1:C1:C1:00','VNHB':'B1:B1:B1:B1:B1:00',
               'VNHD':'D1:D1:D1:D1:D1:00'}
    
prefixes={'p1':IPv4Network('11.0.0.0/24'),
          'p2':IPv4Network('12.0.0.0/24'),
          'p3':IPv4Network('13.0.0.0/24'),
          'p4':IPv4Network('14.0.0.0/24'),
          'p5':IPv4Network('15.0.0.0/24'),
          'p6':IPv4Network('16.0.0.0/24')
              }
port_2_participant = {
        1 : 'A',
        2 : 'B',
        21 : 'B',
        22 : 'B',
        3 : 'C',
        4 : 'D'
    }
class SDX(object):
    """Represent a SDX platform configuration"""
    def __init__(self):
        self.participants = []
        self.sdx_ports={}
        self.participant_id_to_in_var = {}
        self.out_var_to_port = {}
        self.port_id_to_out_var = {}
        self.policy_2_prefix={}
        self.prefix_2_policy={}
        #self.prefix_2_participant=prefix_2_participant # This will be later updated from the BGP RIB table
        self.policy_2_VNH={}
        self.participant_2_port=participant_2_port
        self.prefixes_announced=prefixes_announced
        self.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received
        self.peer_groups=peer_groups
        self.VNH_2_IP=VNH_2_IP
        self.VNH_2_mac=VNH_2_mac
        self.prefixes=prefixes
        self.port_2_participant=port_2_participant
        
    def get_participantName(self,ip):
        pname=''
        #print self.sdx_ports
        #print ip
        for participant_name in self.sdx_ports:
            for port in self.sdx_ports[participant_name]:
                #print port.ip
                if IP(ip)==port.ip:
                    #print "IP matched"
                    pname=participant_name
                    break
        return pname
    def get_neighborList(self,sname):
        #print type(sname)
        neighbor_list=[]
        for participant in self.participants:
            #print participant.peers.keys()
            if sname in participant.peers.keys():
                #print "Neighbor found",participant.id_
                neighbor_list.append(participant.id_) 
        return neighbor_list
    
    def add_participant(self, participant):
        self.participants.append(participant)
        self.participant_id_to_in_var[participant.id_] = "in" + participant.id_.upper()
        i = 0
        for port in participant.phys_ports:
            self.port_id_to_out_var[port.id_] = "out" + participant.id_.upper() + "_" + str(i)
            self.out_var_to_port["out" + participant.id_.upper() + "_" + str(i)] = port
            i += 1
    
    #def return_participant(self,ip):
    
    def fwd(self, port):
        if isinstance(port, PhysicalPort):
            return modify(state=self.port_id_to_out_var[port.id_], dstmac=port.mac)
        else:
            return modify(state=self.participant_id_to_in_var[port.participant.id_])
###
### SDX high-level functions
###

def sdx_from(vport):
    '''
        Helper function that given a vport
        return a match function for all the physical macs behind that vport
        this is useful to avoid communication between two participants
    '''
    match_all_physical_port = no_packets
    for phys_port in vport.participant.phys_ports:
        match_all_physical_port = match_all_physical_port | match(srcmac=phys_port.mac)
    return match_all_physical_port

def sdx_restrict_state(sdx_config, participant):
    '''
        Check if the state is not an end state (i.e., output port). 
        If so return a passthrough policy otherwise 
        prefix a match on the participant's state variable
        before any of the participant's policy to ensure that
        it cannot match on other participant's flowspace
    '''
    match_all_output_var = no_packets
    for output_var in sdx_config.out_var_to_port:
        match_all_output_var = match_all_output_var | match(state=output_var)
    return if_(match_all_output_var, 
               passthrough, 
               match(state=sdx_config.participant_id_to_in_var[participant.id_]) >> 
                    #parallel([sdx_from(participant.peers[peer_name]) for peer_name in participant.peers]) & '''Might not happen, as we are providing limited view to the participants''' 
                        participant.policies
              )

def sdx_preprocessing(sdx_config):
    '''
        Map incoming packets on participant's ports to the corresponding
        incoming state
    '''
    preprocessing_policies = []
    for participant in sdx_config.participants:
        for port in participant.phys_ports:
            preprocessing_policies.append((match(inport=port.id_) >> 
                modify(state=sdx_config.participant_id_to_in_var[participant.id_])))
    return parallel(preprocessing_policies)

def sdx_postprocessing(sdx_config):
    '''
        Forward outgoing packets to the appropriate participant's ports
        based on the outgoing state
    '''
    postprocessing_policies = []
    for output_var in sdx_config.out_var_to_port:
        postprocessing_policies.append((match(state=output_var) >> modify(state=None) >> 
            fwd(sdx_config.out_var_to_port[output_var].id_)))
    return parallel(postprocessing_policies)

def sdx_participant_policies(sdx_config):
    '''
        Sequentially compose the || composition of the participants policy k-times where
        k is the number of participants
    '''
    sdx_policy = passthrough
    for k in [0,1]:
    #for k in sdx_config.participants:
        print k
        sdx_policy = sequential([
                sdx_policy,
                parallel(
                    [sdx_restrict_state(sdx_config, participant) for participant in sdx_config.participants]
                )])
    return sdx_policy


    
def sdx_platform(sdx_config):
    '''
        Defines the SDX platform workflow
    '''
    #print sdx_config.out_var_to_port
    #print sdx_config.participant_id_to_in_var
    return (
        sdx_preprocessing(sdx_config) >>
        sdx_participant_policies(sdx_config) >>
        sdx_postprocessing(sdx_config)
    )
 

###
### SDX primary functions
###

def sdx_parse_config(config_file):
    sdx = SDX()
    
    sdx_config = json.load(open(config_file, 'r'))
    #print sdx_config
    sdx_ports = {}
    sdx_vports = {}
    sdx_participants = {}
    
    ''' 
        Create SDX environment ...
    '''
    for participant_name in sdx_config:
        
        ''' Adding physical ports '''
        participant = sdx_config[participant_name]
        sdx_ports[participant_name] = [PhysicalPort(id_ = participant["Ports"][i]['Id'], mac = MAC(participant["Ports"][i]["MAC"]),ip=IP(participant["Ports"][i]["IP"])) for i in range(0, len(participant["Ports"]))]     
        #print sdx_ports[participant_name][0].ip
        ''' Adding virtual port '''
        sdx_vports[participant_name] = VirtualPort() #Check if we need to add a MAC here
    sdx.sdx_ports=sdx_ports   
    for participant_name in sdx_config:
        peers = {}
        
        ''' Assign peers to each participant '''
        for peer_name in sdx_config[participant_name]["Peers"]:
            peers[peer_name] = sdx_vports[peer_name]
            
        ''' Creating a participant object '''
        sdx_participants[participant_name] = SDXParticipant(id_ = participant_name, vport=sdx_vports[participant_name], phys_ports = sdx_ports[participant_name], peers = peers)
        
        ''' Adding the participant in the SDX '''
        sdx.add_participant(sdx_participants[participant_name])
    
    return (sdx, sdx_participants)
                    
    
def sdx_parse_policies(policy_file, sdx, participants):
        
    sdx_policies = json.load(open(policy_file, 'r')) 
 
    ''' 
        Get participants policies
    '''
    for participant_name in sdx_policies:
        participant = participants[participant_name]
        policy_modules = [import_module(sdx_policies[participant_name][i]) 
                          for i in range(0, len(sdx_policies[participant_name]))]
        
        participant.policies = parallel([
             policy_modules[i].policy(participant, sdx) 
             for i in range(0, len(sdx_policies[participant_name]))])  
        print "Before pre",participant.policies
        # translate these policies for VNH Assignment
        participant.policies=pre_VNH(participant.policies,sdx,participant_name)
        #print "After pre: ",participant.policies
    #print sdx.out_var_to_port[u'outB_1'].id_  
        
    # Virtual Next Hop Assignment
    vnh_assignment(sdx,participants) 
    print "Completed VNH Assignment"
    # translate these policies post VNH Assignment
    
    classifier=[]
    for participant_name in participants:
        participants[participant_name].policies=post_VNH(participants[participant_name].policies,sdx,participant_name)        
        start_comp=time.time()
        classifier.append(participants[participant_name].policies.compile())
        print participant_name, time.time() - start_comp, "seconds"
    """
    print classifier
    base=None
    for rule in classifier:
        print rule
    """
    

            
    