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
from keystone import config
from keystone import exception
from keystone import test
from keystone import token
import webob

import fixtures
import kslegacyv1.core as kslegacyv1_core

CONF = config.CONF


class LegacyV1Test(test.TestCase):
    def setUp(self):
        super(LegacyV1Test, self).setUp()

        self.load_backends()

        self.controller = kslegacyv1_core.LegacyV1Controller()

    def test_no_headers_fails_unauthorized(self):
        self.assertEquals(self.controller.auth({}).status,
                          webob.Response(status='401 Unauthorized').status)

    def test_no_user_tenant_in_tenant_unauthorized(self):
        context = {'headers': {'foo': 'bar'}}
        self.assertEquals(self.controller.auth(context).status,
                          webob.Response(status='401 Unauthorized').status)

    def test_no_user_tenant_in_header_key(self):
        context = {'headers': {'X-Auth-Key': 'bar', 'X-Auth-User': 'foo'}}
        self.assertEquals(self.controller.auth(context).status,
                          webob.Response(status='401 Unauthorized').status)

    def test_bad_authentication(self):
        context = {'headers': {'X-Auth-Key': 'user',
                               'X-Auth-User': 'foo:bar'}}

        def fake_authenticate(*args, **kwargs):
            raise exception.Unauthorized

        self.stubs.Set(token.controllers.Auth, 'authenticate',
                       fake_authenticate)
        self.assertEquals(self.controller.auth(context).status,
                          webob.Response(status='401 Unauthorized').status)

    def test_no_user_storage_url(self):
        context = {'headers': {'X-Auth-Key': 'user',
                               'X-Auth-User': 'foo:bar'}}

        def fake_authenticate(*args, **kwargs):
            return {'access': {}}

        self.stubs.Set(token.controllers.Auth, 'authenticate',
                       fake_authenticate)
        self.assertEquals(self.controller.auth(context).status,
                          webob.Response(status='401 Unauthorized').status)

    def _test_good(self, tokenFixture):
        context = {'headers': {'X-Auth-Key': 'user',
                               'X-Auth-User': 'foo:bar'}}

        def fake_authenticate(*args, **kwargs):
            return tokenFixture

        self.stubs.Set(token.controllers.Auth, 'authenticate',
                       fake_authenticate)
        resp = self.controller.auth(context)
        self.assertIn('X-Auth-Token', resp.headers)
        self.assertIn('X-Storage-Token', resp.headers)
        self.assertIn('X-Storage-Url', resp.headers)
        self.assertIn('Content-Type', resp.headers)
        self.assertEquals(resp.headers['Content-Type'], 'text/xml')

        _tok = [i for i in tokenFixture['access']['serviceCatalog']
                if i['type'] == 'object-store']
        tokenFixture_storage_url = _tok[0]['endpoints'][0]['publicURL']
        self.assertEquals(resp.headers['X-Storage-Url'],
                          tokenFixture_storage_url)

        tokenFixture_storage_token_id = tokenFixture['access']['token']['id']
        self.assertEquals(resp.headers['X-Auth-Token'],
                          tokenFixture_storage_token_id)

        self.assertEquals(resp.headers['X-Storage-Token'],
                          tokenFixture_storage_token_id)


    def test_good_v2(self):
        self._test_good(fixtures.SAMPLE_V2_TOKEN)

    def test_good_v3(self):
        self._test_good(fixtures.SAMPLE_V2_TOKEN)
