"""
Add the
[OMS](https://blogs.technet.microsoft.com/momteam/2015/11/03/announcing-linux-docker-container-management-with-oms/)
monitoring solution to the cluster.

Visit http://mms.microsoft.com and sign up for a free OMS
account. Then click "Settings" and then "Connected Sources". You will
need to copy your Workspace ID and your Workspace Primary Key into
your config file. Finally, run the `install` command to install OMS on
each of your agents (please note that this command restarts the Docker
Engine and thus any containers on it will be stopped).

Usage:
  oms <command> [help] [options]

Commands:
  install                Install the OMS monitoring agent on all ACS agents

Options:

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps

from .base import Base

class Oms(Base):

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

  def install(self):
      """
      Install the OMS agent on all ACS agents
      """

      ips = Base.getAgentIPs(self)
      for ip in ips:
        self.log.debug("Installing OMS on: " + ip)
        
        result = ""

        cmd = "wget https://github.com/Microsoft/OMS-Agent-for-Linux/releases/download/v1.1.0-28/omsagent-1.1.0-28.universal.x64.sh\n"
        result = result + self.executeOnAgent(cmd, ip)

        cmd = "chmod +x ./omsagent-1.1.0-28.universal.x64.sh\n"
        result = result + self.executeOnAgent(cmd, ip)

        workspace_id = self.config.get('OMS', "workspace_id")
        workspace_key = self.config.get('OMS', "workspace_primary_key")
        cmd = "sudo ./omsagent-1.1.0-28.universal.x64.sh --upgrade -w " + workspace_id + " -s " + workspace_key + "\n"
        result = result + self.executeOnAgent(cmd, ip)

        cmd = "sudo sed -i -E \"s/(DOCKER_OPTS=\\\")(.*)\\\"/\\1\\2 --log-driver=fluentd --log-opt fluentd-address=localhost:25225\\\"/g\" /etc/default/docker\n"
        result = result + self.executeOnAgent(cmd, ip)

        cmd = "sudo service docker restart\n"
        result = result + self.executeOnAgent(cmd, ip)

        return result

  def help(self):
    print(__doc__)
