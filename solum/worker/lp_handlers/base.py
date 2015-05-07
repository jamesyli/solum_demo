# Copyright 2015 - Rackspace Hosting
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

"""Base LP handler for building apps"""

from docker import client as docker_client
from oslo.config import cfg

from solum.uploaders import tenant_logger

cfg.CONF.import_opt('task_log_dir', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('docker_daemon_url', 'solum.worker.config', group='worker')
log_dir = cfg.CONF.worker.task_log_dir
docker_daemon_url = cfg.CONF.docker_daemon_url


class BaseHandler(object):

    def __init__(self, context, assembly):
        self.context = context
        self.assembly = assembly
        self._docker = None

    def _clone_repo(self, repo_url, destination, commit_sha=None, branch=None):
        # Clone a repo with the constraints of disk and memory usage
        # Need to consider limiting network bandwidth as well.
        pass

    def _validate_pub_repo(self, repo_url):
        pass

    @property
    def docker(self):
        if self._docker is None:
            self._docker = docker_client.Client(base_url=docker_daemon_url)
        return self._docker

    def _get_tenant_logger(self, stage):
        return tenant_logger.TenantLogger(self.context,
                                          self.assembly, log_dir, stage)

    def unittest_app(self, *args):
        """Interface to implement in derived class."""
        pass

    def build_app(self, *args):
        """Interface to implement in derived class."""
        pass
