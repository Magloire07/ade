#!/usr/bin/python

from acs.acs_utils import ACSLog

class SwarmTest:
    def __init__(self, acs):
        self.acs = acs
        self.log = ACSLog()

    def testAll(self):
        """Run all tests against the supplied ACS"""

        response = self.acs.openSwarmTunnel()
        self.log.info(response);

        self.log.info("docker info")
        response = self.acs.dockerCommand('info')
        self.log.info(response);
        self.log.info("End test")

        self.log.info("docker ps")
        response = self.acs.dockerCommand('ps')
        self.log.info(response);
        self.log.info("End test")

        self.log.info("Deploy a two container app")
        response = self.acs.composeCommand('up', options = '-d')
        self.log.info(response);
        self.log.info("End")
    
        self.log.info("docker ps")
        response = self.acs.dockerCommand('ps')
        self.log.info(response);
        self.log.info("End test")
        
        self.log.info("Stop the applicaton")
        response = self.acs.composeCommand('stop')
        self.log.info(response);
        self.log.info("End test")


        self.log.info("docker ps")
        response = self.acs.dockerCommand('ps')
        self.log.info(response);
        self.log.info("End test")


