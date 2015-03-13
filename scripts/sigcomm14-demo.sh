#!/bin/bash
######################################
# SDX: Software Defined Exchange
# Author: Arpit Gupta
######################################

$HOME/pyretic/pyretic/sdx/scripts/sdx-setup.sh init gec20_demo
$HOME/pyretic/pyretic/sdx/scripts/sdx-setup.sh clearrib
$HOME/pyretic/pyretic/sdx/scripts/sdx-setup.sh pyretic > $HOME/pyretic/pyretic/sdx/scripts/log/pyretic.log 2> $HOME/pyretic/pyretic/sdx/scripts/log/pyretic_err.log &
$HOME/pyretic/pyretic/sdx/scripts/sdx-setup.sh exabgp > $HOME/pyretic/pyretic/sdx/scripts/log/exabgp.log 2> $HOME/pyretic/pyretic/sdx/scripts/log/exabgp_err.log &
$HOME/pyretic/pyretic/sdx/scripts/sdx-setup.sh demo gec20_demo 
