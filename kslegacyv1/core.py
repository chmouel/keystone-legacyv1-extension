# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 eNovance
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import webob

from keystone import config
from keystone import token
from keystone import exception
from keystone.common import wsgi

CONF = config.CONF
DEFAULT_DOMAIN_ID = CONF.identity.default_domain_id


class LegacyV1Controller(token.controllers.Auth):
    def auth(self, context):
        if not context.get('headers'):
            #Raise invalid
            return

        header_user_tenant = context.get('headers').get('X-Auth-User')
        header_token = context.get('headers').get('X-Auth-Token')

        if (not header_user_tenant or not header_token
            or not ':' in header_user_tenant):
            return webob.Response(status='401 Unauthorized')

        try:
            (userName, tenantName) = header_user_tenant.split(':')
        except(ValueError):
            return webob.Response(status='401 Unauthorized')

        auth = {
            "passwordCredentials": {
                "username": userName,
                "password": header_token
            }, "tenantName": tenantName}

        try:
            user_ref = self.authenticate(context, auth=auth)
        except(exception.Error):
            return webob.Response(status='401 Unauthorized')

        storage_url = None
        for access in user_ref['access']:
            if access == "serviceCatalog":
                for service in user_ref["access"][access]:
                    if service['type'] == 'object-store':
                        storage_url = service['endpoints'][0]['publicURL']

        if not storage_url:
            return webob.Response(status='401 Unauthorized')

        token_id = user_ref['access']['token']['id']
        headers = [('X-Auth-Token', token_id)]
        headers.append(('X-Storage-Token', token_id))
        headers.append(('X-Storage-Url', storage_url))
        headers.append(('Vary', 'X-Auth-Token,X-Storage-Token,X-Storage-Url'))

        # Go figure why RAX cloud is returning that
        headers.append(('Content-Type', 'text/xml'))
        status = (200, 'OK')
        return webob.Response(status='%s %s' % status,
                              headerlist=headers)


class LegacyV1(wsgi.ExtensionRouter):
    def add_routes(self, mapper):
        legacy_v1_controller = LegacyV1Controller()
        mapper.connect('/',
                       controller=legacy_v1_controller,
                       action='auth')
