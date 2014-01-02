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
#        Muhammad Shahbaz
#        Arpit Gupta
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

## General imports
import json
from importlib import import_module
from ipaddr import IPv4Network
from netaddr import *

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.bgp_interface import *
from pyretic.sdx.lib.set_operations import *
from pyretic.sdx.lib.language import *
#from pyretic.sdx.lib.policy_converter import *
from pyretic.sdx.lib.vnh_assignment import *

###
### SDX classes
###
# TODO: These should be automatically generated using the sdx_config.cfg file

participant_2_port={'A':{'A':[1],'B':[2],'C':[3],'D':[4]},
                    'B':{'A':[1],'B':[2,21,22],'C':[3],'D':[4]},
                    'C':{'A':[1],'B':[2],'C':[3],'D':[4]},
                    'D':{'A':[1],'B':[2],'C':[3],'D':[4]}
                   }

port_2_participant = {
        1  : 'A',
        2  : 'B',
        21 : 'B',
        22 : 'B',
        3  : 'C',
        4  : 'D'
    }

# TODO: these should be added in the config file too and auto-generated
VNH_2_IP = {
            'VNH':list(IPNetwork('172.0.0.1/28'))
          }
VNH_2_MAC={
            'VNH':'AA:00:00:00:00:00'
          }

#peer_groups={'pg1':[1,2,3,4]}

#prefixes_announced={'pg1':{
#                               'A':['10.0.0.0/24'],
#                               'B':['11.0.0.0/24','12.0.0.0/24','13.0.0.0/24','14.0.0.0/24','16.0.0.0/24'],
#                               'C':['13.0.0.0/24','14.0.0.0/24','15.0.0.0/24','16.0.0.0/24'],
#                               'D':['11.0.0.0/24','12.0.0.0/24','13.0.0.0/24','14.0.0.0/24','15.0.0.0/24','16.0.0.0/24'],
#                               }
#                        }

# Set of prefixes for A's best paths
# We will get this data structure from RIB
#participant_to_ebgp_nh_received = {
#        'A' : {'11.0.0.0/24':'D','12.0.0.0/24':'D','13.0.0.0/24':'D','14.0.0.0/24':'C','15.0.0.0/24':'C','16.0.0.0/24':'C'}
#    }
    
#prefixes={'p1':IPv4Network('11.0.0.0/24'),
#          'p2':IPv4Network('12.0.0.0/24'),
#          'p3':IPv4Network('13.0.0.0/24'),
#          'p4':IPv4Network('14.0.0.0/24'),
#          'p5':IPv4Network('15.0.0.0/24'),
#          'p6':IPv4Network('16.0.0.0/24')
#              }


class SDX(object):
    """Represent a SDX platform configuration"""
    def __init__(self):
        self.participants = {}
        
        self.sdx_ports={}
        self.participant_id_to_in_var = {}
        self.out_var_to_port = {}
        self.port_id_to_out_var = {}
        
        #self.policy_2_prefix={}
        #self.prefix_2_policy={}
        #self.prefix_2_participant=prefix_2_participant # This will be later updated from the BGP RIB table
        #self.policy_2_VNH={}
        
        self.participant_2_port=participant_2_port
        
        #self.prefixes_announced=prefixes_announced
        #self.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received
        #self.peer_groups=peer_groups
        
        VNH_2_pfx = None
        self.VNH_2_IP=VNH_2_IP
        self.VNH_2_MAC=VNH_2_MAC
        self.part_2_VNH={}
        
        #self.prefixes=prefixes
        
        self.port_2_participant=port_2_participant
        self.part_2_prefix_old={}
        self.part_2_prefix_lcs={}
        self.lcs_old=[]
        
    ''' Get the name of the participant belonging to the IP address '''
    def get_participant_name(self,ip):
        
        for participant_name in self.sdx_ports:
            for port in self.sdx_ports[participant_name]:  
                if ip is str(port.ip):
                    return participant_name
    
    def get_neighborList(self,sname):
        #print type(sname)
        neighbor_list=[]
        for participant in self.participants:
            #print participant.peers.keys()
            if sname in self.participants[participant].peers.keys():
                #print "Neighbor found",participant.id_
                neighbor_list.append(self.participants[participant].id_) 
        return neighbor_list
    
    def add_participant(self, participant, name):
        self.participants[name] = participant
        self.participant_id_to_in_var[participant.id_] = "in" + participant.id_.upper()
        i = 0
        for port in participant.phys_ports:
            self.port_id_to_out_var[port.id_] = "out" + participant.id_.upper() + "_" + str(i)
            self.out_var_to_port["out" + participant.id_.upper() + "_" + str(i)] = port
            i += 1
    
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
        for port in sdx_config.participants[participant].phys_ports:
            preprocessing_policies.append((match(inport=port.id_) >> 
                modify(state=sdx_config.participant_id_to_in_var[sdx_config.participants[participant].id_])))
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
                    [sdx_restrict_state(sdx_config, sdx_config.participants[participant]) for participant in sdx_config.participants]
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
    
    ''' 
        Create SDX environment ...
    '''
    for participant_name in sdx_config:
        
        ''' Adding physical ports '''
        participant = sdx_config[participant_name]
        sdx_ports[participant_name] = [PhysicalPort(id_=participant["Ports"][i]['Id'],mac=MAC(participant["Ports"][i]["MAC"]),ip=IP(participant["Ports"][i]["IP"])) for i in range(0, len(participant["Ports"]))]     
        print sdx_ports[participant_name]
        ''' Adding virtual port '''
        sdx_vports[participant_name] = VirtualPort(participant=participant_name) #Check if we need to add a MAC here
    
    sdx.sdx_ports=sdx_ports   
    for participant_name in sdx_config:
        peers = {}
        
        ''' Assign peers to each participant '''
        for peer_name in sdx_config[participant_name]["Peers"]:
            peers[peer_name] = sdx_vports[peer_name]
            
        ''' Creating a participant object '''
        sdx_participant = SDXParticipant(id_=participant_name,vport=sdx_vports[participant_name],phys_ports=sdx_ports[participant_name],peers=peers)
        
        ''' Adding the participant in the SDX '''
        sdx.add_participant(sdx_participant,participant_name)
    
    return sdx
                
def sdx_parse_policies(policy_file,sdx):
        
    sdx_policies = json.load(open(policy_file,'r'))  
    ''' 
        Get participants policies
    '''
    for participant_name in sdx_policies:
        participant = sdx.participants[participant_name]
        policy_modules = [import_module(sdx_policies[participant_name][i]) 
                          for i in range(0, len(sdx_policies[participant_name]))]
        
        participant.policies = parallel([
             policy_modules[i].policy(participant, sdx) 
             for i in range(0, len(sdx_policies[participant_name]))])  
        print "Before pre",participant.policies
        # translate these policies for VNH Assignment
        participant.original_policies=participant.policies
        participant.policies=pre_VNH(participant.policies,sdx,participant_name,participant)
        
        print "After pre: ",participant.policies
    #print sdx.out_var_to_port[u'outB_1'].id_  
       
    # Virtual Next Hop Assignment
    vnh_assignment(sdx) 
    print "Completed VNH Assignment"
    # translate these policies post VNH Assignment
    
    classifier=[]
    for participant_name in sdx.participants:
        sdx.participants[participant_name].policies=post_VNH(sdx.participants[participant_name].policies,
                                                         sdx,participant_name)        
        print "After Post VNH: ",sdx.participants[participant_name].policies
        start_comp=time.time()
        classifier.append(sdx.participants[participant_name].policies.compile())
        print participant_name, time.time() - start_comp, "seconds"
    