from .ACSLogs import *

import azurerm
import ConfigParser
import json

class AgentPool:
    """

    An Agent Pool is a collection of agents available within an ACS
    cluster. Each pool is implemented as a Virtual Machine Scale Set
    (VMSS).

    """
    def __init__(self, config):
        self.log = ACSLog("AgentPool")
        defaults = {"orchestratorType": "Mesos"}
        self.config = config

    def getAccessToken(self):
        tenant_id = self.config.get('Subscription', 'tenant_id')
        app_id = self.config.get('Subscription', 'app_id')
        app_secret = self.config.get('Subscription', 'app_secret')
        return azurerm.get_access_token(tenant_id, app_id, app_secret)

    def getPools(self):
        """
        Get a list of all the agent pools in this resource group
        """
        subscription_id = self.config.get('Subscription', 'subscription_id')
        rg_name = self.config.get('Group', 'name')
        access_token = self.getAccessToken()

        vmss_list = azurerm.list_vm_scale_sets(access_token, subscription_id, rg_name)['value']
        self.log.debug("List of VMSS: " + json.dumps(vmss_list, indent=True))
        return vmss_list

    def getNICs(self):
        """
        Get a list of NICs attached to an agent pool
        """
        nics = []
        vmss_list = self.getPools()
        for vmss in vmss_list:
            vmss_name = vmss['name']
            self.log.debug("Looking up VMs in VMSS called " + vmss_name)

            subscription_id = self.config.get('Subscription', 'subscription_id')
            rg_name = self.config.get('Group', 'name')
            access_token = self.getAccessToken()
            nics = nics + azurerm.get_vmss_nics(access_token, subscription_id, rg_name, vmss_name)['value']
            self.log.debug("List of VMSS NICs: " + json.dumps(nics, indent=True))
        return nics

    def getAgents(self):
        """
        Get a list of all agents in the Pool.
        """
        vms = []
        vmss_list = self.getPools()
        for vmss in vmss_list:
            vmss_name = vmss['name']
            self.log.debug("Looking up VMs in VMSS called " + vmss_name)

            subscription_id = self.config.get('Subscription', 'subscription_id')
            rg_name = self.config.get('Group', 'name')
            access_token = self.getAccessToken()
            vms = vms + azurerm.list_vmss_vms(access_token, subscription_id, rg_name, vmss_name)['value']
        return vms

