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
from solum.worker.lp_handlers import utils

cfg.CONF.import_opt('task_log_dir', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('docker_daemon_url', 'solum.worker.config', group='worker')
log_dir = cfg.CONF.worker.task_log_dir
docker_daemon_url = cfg.CONF.docker_daemon_url
docker_cmd_runner = cfg.CONF.run_container_cmd_as

MAX_GIT_CLONE_RETRY = 5
GIT_CLONE_TIMEOUT = 900 # 15 minutes

class BaseHandler(object):

    def __init__(self, context, assembly):
        self.context = context
        self.assembly = assembly
        self._docker = None

    def _clone_repo(self, repo_url, destination, revision='master'):
        # Clone a repo with the constraints of disk and memory usage
        # Need to consider limiting network bandwidth as well.
        container_dest = '/tmp/code'
        if utils.is_git_sha(revision):
            clone_cmd = ('git clone {url} {dst} &&'
                         ' cd {dst}'
                         ' git checkout -B solum {rev}').format(
                url=repo_url, dst=container_dest, rev=revision)
        else:
            clone_cmd = ('git clone -b {branch} --depth 1'
                         ' {url} {dst}').format(
                branch=revision, url=repo_url, dst=container_dest)

        timeout_clone = ('timeout --signal=SIGKILL {t}'
                         ' /bin/bash -c \"{clone}\"').format(
            t=GIT_CLONE_TIMEOUT, clone=clone_cmd)
        cmd = ('RETRIES=0;'
               ' until [ $RETRIES -ge 5 ]; do'
               ' rm -rf {dst};'
               ' {clone_cmd} && break;'
               ' RETRIES=$[$RETRIES+1];'
               ' sleep 5;'
               ' done').format(dst=container_dest, clone_cmd=timeout_clone)
        dockerfile = ('FROM solum/cloner\n'
                      'RUN useradd -s /bin/bash -u {uid} solum-cloner\n'
                      'USER solum-cloner\n'
                      'CMD {cmd}').format(uid=docker_cmd_runner, cmd=cmd)

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
