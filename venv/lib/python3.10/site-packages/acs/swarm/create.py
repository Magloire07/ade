#!/usr/bin/python

from ..acs_utils import *

acs = ACSUtils("swarm_cluster.ini")
log = ACSLog()

log.debug("Starting the scratch application")

log.debug("Create an ACS deployment")
acs.createDeployment()

log.debug("Copy private key to master")
acs.configureSSH()

log.debug("Add a storage account and a file share to the ACS resource group")
acs.createStorage()

log.debug("Install package on all agents")
agentHostNames = acs.getAgentHostNames()
acs.addAzureFileService(agentHostNames)
