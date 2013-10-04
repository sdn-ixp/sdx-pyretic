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

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.common import *

## General imports
import json
from importlib import import_module

###
### SDX classes
###

class SDX(object):
    """Represent a SDX platform configuration"""
    def __init__(self):
        self.participants = []

        self.participant_id_to_in_var = {}
        self.out_var_to_port = {}
        self.port_id_to_out_var = {}
    
    def add_participant(self, participant):
        self.participants.append(participant)
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
               match(state=sdx_config.participant_id_to_in_var[participant.id_]) & 
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
            preprocessing_policies.append((match(inport=port.id_) & 
                modify(state=sdx_config.participant_id_to_in_var[participant.id_])))
    return parallel(preprocessing_policies)

def sdx_postprocessing(sdx_config):
    '''
        Forward outgoing packets to the appropriate participant's ports
        based on the outgoing state
    '''
    postprocessing_policies = []
    for output_var in sdx_config.out_var_to_port:
        postprocessing_policies.append((match(state=output_var) & pop("state") & 
            fwd(sdx_config.out_var_to_port[output_var].id_)))
    return parallel(postprocessing_policies)

def sdx_participant_policies(sdx_config):
    '''
        Sequentially compose the || composition of the participants policy k-times where
        k is the number of participants
    '''
    sdx_policy = passthrough
    for k in sdx_config.participants:
        sdx_policy = sequential([
                sdx_policy,
                parallel(
                    [sdx_restrict_state(sdx_config, participant) for participant in sdx_config.participants]
                )])
    return sdx_policy


###
### SDX primary functions
###

def sdx_parse_config(config_file):
    sdx = SDX()
    
    sdx_config = json.load(open(config_file, 'r'))

    sdx_ports = {}
    sdx_vports = {}
    sdx_participants = {}
    
    ''' 
        Create SDX environment ...
    '''
    for participant_name in sdx_config:
        
        ''' Adding physical ports '''
        participant = sdx_config[participant_name]
        sdx_ports[participant_name] = [PhysicalPort(id_ = participant["Ports"][i]['Id'], mac = MAC(participant["Ports"][i]["MAC"])) for i in range(0, len(participant["Ports"]))]     
        ''' Adding virtual port '''
        sdx_vports[participant_name] = VirtualPort() #Check if we need to add a MAC here
        
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
        participant_policy = import_module(sdx_policies[participant_name])
        participant_policy.policy(participants[participant_name], sdx.fwd)

def sdx_platform(sdx_config):
    '''
        Defines the SDX platform workflow
    '''
    return (
        sdx_preprocessing(sdx_config) >>
        sdx_participant_policies(sdx_config) >>
        sdx_postprocessing(sdx_config)
    )
 