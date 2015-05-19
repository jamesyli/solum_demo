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

"""LP handler for building apps running on solum language packs"""

import logging
import os
import random
import string

from solum.common import clients
from solum.worker.lp_handlers import base
from solum.worker.lp_handlers import utils


class DockerHandler(base.BaseHandler):

    def __init__(self, context, assembly, lp_type, image_storage):
        super(DockerHandler, self).__init__(context, assembly)

        self.lp_type = lp_type
        self.image_storage = image_storage
        if self.image_storage == 'glance':
            self.glance = clients.OpenStackClients(context).glance()

    def _download_lp(self):
        # try cache before downloading from origin
        pass

    def build_lp(self, lp_name, git_info):
        logger = self._get_tenant_logger('language_pack')
        tenant = self.context.tenant
        ts = utils.timestamp()
        ranid = (''.join(random.choice(string.ascii_uppercase)
                 for i in range(20)))
        work_dir = '/tmp/lps/{tenant}/{id}'.format(tenant=tenant, id=ranid)
        try:
            os.makedirs(work_dir)
        except OSError:
            return

        source_url = git_info['source_url']
        head_sha = self._clone_repo(git_info['source_url'], work_dir, logger)
        if not head_sha:
            return

        storage_obj_name = '{name}-{ts}-{sha}'.format(name=lp_name, ts=ts,
                                                      sha=head_sha)
        lp_image_tag = '{tenant}-{obj}'.format(tenant=tenant,
                                               obj=storage_obj_name)
        dockerfile = '{}/code'.format(work_dir)

        for l in self.docker.build(path=dockerfile, forcerm=True, quiet=True,
                                   tag=lp_image_tag):
            logger.log(logging.INFO, l)

        lp = self.docker.get_image(lp_image_tag)
        lp_file = '{}/{}'.format(work_dir, storage_obj_name)
        with open(lp_file, 'w') as f:
            f.write(lp.data)

        return storage_obj_name

    def unittest_app(self, *args):
        pass

    def build_app(self, *args):
        pass
