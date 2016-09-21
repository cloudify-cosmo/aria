# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import aria
from aria.logger import (
    create_logger,
    create_console_log_handler,
    create_file_log_handler,
    LoggerMixin,
)
from aria_command_line.args_parser import config_parser

from aria_command_line.commands import (
    InitCommand,
    RequirementsCommand,
    InstallCommand,
    UninstallCommand,
    ExecuteCommand,
    InstancesCommand,
    PluginsCommand,
    OutputCommand,
)
from aria_command_line.storage import user_space


__version__ = '0.1.0'


class AriaCli(LoggerMixin):
    TITLE = (
        "\n"
        "***************************\n"
        "***** /\ ****** ( ) *******  Aria SDK Version: {aria_version}\n"
        "**** /  \   _ __ _  __ _ **  CLI Version: {cli_version}\n"
        "*** / /\ \ | '__| |/ _` | *\n"
        "** / ____ \| |  | | (_| | *  Configuration Directory: {config_path}\n"
        "* /_/    \_\_|  |_|\__,_| *\n"
        "***************************\n"
    )

    def __init__(self, *args, **kwargs):
        super(AriaCli, self).__init__(*args, **kwargs)
        self.logger.info(self.TITLE.format(
            aria_version=aria.__version__,
            cli_version=__version__,
            config_path=user_space()))
        self.commands = {
            'init': InitCommand.with_logger(base_logger=self.logger),
            'requirements': RequirementsCommand.with_logger(base_logger=self.logger),
            'install': InstallCommand.with_logger(base_logger=self.logger),
            'uninstall': UninstallCommand.with_logger(base_logger=self.logger),
            'plugins': PluginsCommand.with_logger(base_logger=self.logger),
            'execute': ExecuteCommand.with_logger(base_logger=self.logger),
            'instances': InstancesCommand.with_logger(base_logger=self.logger),
            'output': OutputCommand.with_logger(base_logger=self.logger),
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Here we will handle errors
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        # todo: error handling
        # todo: cleanup if needed
        # TODO: user message if needed
        pass

    def run(self):
        parser = config_parser()
        args = parser.parse_args()

        command_handler = self.commands[args.command]
        self.logger.debug('Running command: {args.command} handler: {0}'.format(
            command_handler, args=args))
        command_handler(args)


def main():
    create_logger(
        handlers=[
            create_console_log_handler(),
            create_file_log_handler(file_path='/tmp/aria_cli.log'),
        ],
        level=logging.INFO)
    with AriaCli() as aria:
        aria.run()


if __name__ == '__main__':
    main()
