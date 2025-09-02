""" 
Azure File System Docker volume driver.

Usage:
  afs <command> [options]

Commands:
  install               Install the AFS driver on all agents

Options:
  -n --name=NAME
    Azure storage account name
  -k --key
    Azure storage account key

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts
"""

from ..acs_utils import *
from .base import Base

import subprocess
from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps

class Afs(Base): 

    def run(self):
        args = docopt(__doc__, argv=self.options)
        # print("Global args")
        # print(args)
        self.args = args
        
        command = self.args["<command>"]
        result = None
        methods = getmembers(self, predicate = ismethod)
        for name, method in methods:
            if name == command:
                result = method()
                if result is None:
                    result = command + " returned no results"
        if result:
            print(result)
        else:
            print("Unknown command: '" + command + "'")
            self.help()
                    
    def help(self):
    	return __doc__

    def install(self):
        """
        Add the AFS feature to the ACS cluster provided.
        """
        self.createStorage()

        driver_version = "0.2"
        mount = self.config.get("Storage", "mount")
        package = "cifs-utils"
        
        ips = Base.getAgentIPs(self)
        for ip in ips:
            self.log.debug("Installing AFS on: " + ip)
     
            result = ""

            cmd = "rm azurefile-dockervolumedriver*"
            result = result + self.executeOnAgent(cmd, ip)
            
            cmd = "wget https://github.com/Azure/azurefile-dockervolumedriver/releases/download/" + driver_version + "/azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "cp azurefile-dockervolumedriver /usr/bin/azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "chmod +x /usr/bin/azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "wget https://raw.githubusercontent.com/Azure/azurefile-dockervolumedriver/" + driver_version + "/contrib/init/systemd/azurefile-dockervolumedriver.service"
            result = result + self.executeOnAgent(cmd, ip)
            cmd = "sudo cp azurefile-dockervolumedriver.service /etc/systemd/system/azurefile-dockervolumedriver.service"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "echo 'AZURE_STORAGE_ACCOUNT=" + self.config.get("Storage", "name") + "' > azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)
        
            cmd = "echo 'AZURE_STORAGE_ACCOUNT_KEY=" + self.getStorageAccountKey() + "' >> azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)
            
            cmd = "sudo cp azurefile-dockervolumedriver /etc/default/azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "sudo systemctl daemon-reload"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "sudo systemctl enable azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "sudo systemctl start azurefile-dockervolumedriver"
            result = result + self.executeOnAgent(cmd, ip)

            cmd = "mkdir -p " + mount
            result = result + self.executeOnAgent(cmd, ip)
        
            urn = self.getShareEndpoint().replace("https:", "") + self.config.get("Storage", "shareName")
            username = self.config.get("Storage", "name")
            password = self.getStorageAccountKey()
            cmd = "sudo mount -t cifs " + urn + " " + mount + " -o uid=1000,gid=1000,vers=2.1,username=" + username + ",password=" + password
            result = result + self.executeOnAgent(cmd, ip)

            return result

    def createStorage(self):
        """
        Create a storage account for this cluster as defined in the config file.
        """
        self.log.debug("Creating Storage Account")

        Base.createResourceGroup(self)
    
        command = "azure storage account create"
        command = command + " --type " + self.config.get('Storage', 'type')
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " --location " + self.config.get('Group', 'region')
        command = command + " " + self.config.get('Storage', 'name')
    
        os.system(command)

        key = self.getStorageAccountKey()

        try:
            command = "azure storage share create"
            command = command + " --account-name " + self.config.get('Storage', 'name')
            command = command + " --account-key " + key
            command = command + " " + self.config.get('Storage', 'shareName')

            out = subprocess.check_output(command, shell=True)
        except:
            # FIXME: test if the share already exists, if it does then don't try to recreate it
            # For now we just assume that an error is always that the share alrady exists 
            self.log.warning("Failed to create share, assuming it is because it already exists")

    def getShareEndpoint(self):
        """
        Get the a share endpoint for the storage account defined in the ini file
        """
        command = "azure storage account show"
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " " + self.config.get('Storage', 'name')
        command = command + " --json"
        
        data = json.loads(subprocess.check_output(command, shell=True))
        endpoint = data['primaryEndpoints']['file']

        return endpoint

    def getStorageAccountKey(self):
        """
        Get the storage account key for the storage account defined in the ini file
        FIXME: this and related storage methods should move to their own module or class
        """
        command = "azure storage account keys list"
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " " + self.config.get('Storage', 'name')
        command = command + " --json"
        self.log.debug("Command to get storage keys: " + command)

        keys = json.loads(subprocess.check_output(command, shell=True))
        return keys['key1']



