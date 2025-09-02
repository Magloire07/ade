from acs_utils import *

import os
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import subprocess

def addTo(acs):
    """
    Add the AFS feature to the ACS cluster provided.
    """
    driver_version = "0.2"
    mount = acs.config.get("Storage", "mount")
    package = "cifs-utils"

    agents = acs.getAgentHostNames()
    for agent in agents:
        acs.log.debug("Installing AFS on: " + agent)

        cmd = "rm azurefile-dockervolumedriver*"
        acs.executeOnAgent(cmd, agent)

        cmd = "wget https://github.com/Azure/azurefile-dockervolumedriver/releases/download/" + driver_version + "/azurefile-dockervolumedriver"
        acs.executeOnAgent(cmd, agent)

        cmd = "cp azurefile-dockervolumedriver /usr/bin/azurefile-dockervolumedriver"
        acs.executeOnAgent(cmd, agent)

        cmd = "chmod +x /usr/bin/azurefile-dockervolumedriver"
        acs.executeOnAgent(cmd, agent)

        cmd = "wget https://raw.githubusercontent.com/Azure/azurefile-dockervolumedriver/" + driver_version + "/contrib/init/upstart/azurefile-dockervolumedriver.conf"
        acs.executeOnAgent(cmd, agent)

        cmd = "sudo cp azurefile-dockervolumedriver.conf /etc/init/azurefile-dockervolumedriver.conf"
        acs.executeOnAgent(cmd, agent)

        cmd = "echo 'AF_ACCOUNT_NAME=" + acs.config.get("Storage", "name") + "' > azurefile-dockervolumedriver.default"
        acs.executeOnAgent(cmd, agent)

        cmd = "echo 'AF_ACCOUNT_KEY=" + acs.getStorageAccountKey() + "' >> azurefile-dockervolumedriver.default"
        acs.executeOnAgent(cmd, agent)

        cmd = "sudo cp azurefile-dockervolumedriver.default /etc/default/azurefile-dockervolumedriver"
        acs.executeOnAgent(cmd, agent)

        cmd = "sudo initctl reload-configuration"
        acs.executeOnAgent(cmd, agent)

        cmd = "sudo initctl start azurefile-dockervolumedriver"
        acs.executeOnAgent(cmd, agent)

        cmd = "mkdir -p " + mount
        acs.executeOnAgent(cmd, agent)
        
        urn = acs.getShareEndpoint().replace("https:", "") + acs.config.get("Storage", "shareName")
        username = acs.config.get("Storage", "name")
        password = acs.getStorageAccountKey()
        cmd = "sudo mount -t cifs " + urn + " " + mount + " -o uid=1000,gid=1000,vers=2.1,username=" + username + ",password=" + password
        acs.executeOnAgent(cmd, agent)


