"""This is essentially a pass-thru command for the Docker CLI. It
executes the provided command string on all agents in an ACS
cluster. It is useful for perfoming actions such as pre-pulling
images.

Usage:
  docker <docker_cmd> [help]

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-cli

"""

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps

from .base import Base

class Docker(Base):

  def run(self):
    args = docopt(__doc__, argv=self.options)
    print("Command args")
    print(args)
    self.args = args

    command = self.args["<docker_cmd>"]
    print(self.execute(command))
    
    	  
  def help(self):
    print(__doc__)

  def execute(self, cmd):
    """ Run a Docker command on each of the agents """
    self.log.debug("Docker command to run: " + cmd)

    result = ""
    ips = Base.getAgentIPs(self)
    for ip in ips:
      result = result + ip + ": " + cmd + "\n"
      result = result + self.executeOnAgent("docker -H :2375 " + cmd, ip)
      result = result + "\n"

    return result
