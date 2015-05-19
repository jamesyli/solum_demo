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

from solum.common import clients
from solum.worker.lp_handlers import base


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
        pass

    def unittest_app(self, *args):
        pass

    def build_app(self, *args):
        pass
