# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Starter script for the Solum Worker service."""

import logging as std_logging
import os
import sys

from oslo.config import cfg

import solum
from solum.common.rpc import service
from solum.common import trace_data
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging
from solum.worker.handlers import noop as noop_handler
from solum.worker.handlers import shell as shell_handler

LOG = logging.getLogger(__name__)


cli_opts = [
    cfg.IntOpt('run_container_cmd_as', metavar='UID',
               help='Run commands in containers as the user assigned '
                    'with the UID, which can be used to constrain resource, '
                    'e.g. disk usage, on a worker host.'),
]

def main():
    cfg.CONF.register_cli_opts(cli_opts)
    cfg.CONF(sys.argv[1:], project='solum')
    logging.setup('solum')
    solum.TLS.trace = trace_data.TraceData()

    LOG.info(_('Starting server in PID %s') % os.getpid())
    LOG.debug("Configuration:")
    cfg.CONF.log_opt_values(LOG, std_logging.DEBUG)

    cfg.CONF.import_opt('topic', 'solum.worker.config', group='worker')
    cfg.CONF.import_opt('host', 'solum.worker.config', group='worker')
    cfg.CONF.import_opt('handler', 'solum.worker.config', group='worker')

    handlers = {
        'noop': noop_handler.Handler,
        'shell': shell_handler.Handler,
    }

    endpoints = [
        handlers[cfg.CONF.worker.handler](),
    ]

    server = service.Service(cfg.CONF.worker.topic,
                             cfg.CONF.worker.host, endpoints)
    server.serve()
