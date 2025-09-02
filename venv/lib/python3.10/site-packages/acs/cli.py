"""
acs

Usage:
  acs [--config-file=<file>] [--version] [--help] <command> [<args>...]

Options: 
  -h --help                           Show this screen.

Commands:
  service    Create and manage Azure Container Service
  docker     Send docker commands to the cluster
  afs        Add the Azure Files Docker volume driver to each agent
  oms        Add or configure Operational Management Suite monitoring

See `acs help <command>` for information on a specific command.

Help:
  For help using this tool please open an issue on the GitHub repository:
  https://github.com/rgardler/acs-scripts
"""

from . import __version__ as VERSION
from acs.commands.base import Config

from docopt import docopt
from inspect import getmembers, isclass
import os.path
import sys

def main():
  """Main CLI entrypoint"""
  from . import commands

  args = docopt(__doc__, version=VERSION, options_first=True)

  print("Global args:")
  print(args)

  config = Config(args['--config-file'])
  command_name = args["<command>"]
  argv = args['<args>']
  module = getattr(commands, command_name)
  commands = getmembers(module, isclass)
  command_class = None
  command = None
  for k, command_class in commands:
      print("Considering command class: " + command_class.__name__)
      if command_name.lower() in command_class.__name__.lower():
        command = command_class(config, argv)
  if command is None:
    raise Exception("Unrecognized command: " + command_name)
  command.run()
