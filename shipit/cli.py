import argparse
import logging
import sys
from .commands import build, initialize, deploy, destroy


class ShipitCommand(object):

    def __init__(self):
        # Parse the command arguments
        parser = argparse.ArgumentParser(description='Quickly deploy machine learning models to the web.')
        parser.add_argument('command', help="init | build")
        parser.add_argument('-t', '--tag', default="shipit", help="Tag for docker image")
        parser.add_argument('-v', '--verbosity', type=int, default=1, help="Level of console output")
        self.args = parser.parse_args()
        self.command = self.args.command

        # Setup logging
        self.logger = logging.getLogger('shipit')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run(self):
        if self.command == 'build':
            return build(tag=self.args.tag, verbosity=self.args.verbosity)
        elif self.command == 'init':
            return initialize()
        elif self.command == 'deploy':
            return deploy(tag=self.args.tag)
        elif self.command == 'destroy':
            return destroy(tag=self.args.tag)
        else:
            self.logger.warning('No such command {0}'.format(self.command))


def main():
    cmd = ShipitCommand()
    cmd.run()
