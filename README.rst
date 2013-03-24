:Author: Chmouel Boudjnah
:Maintainer: Chmouel Boudjnah <chmouel@enovance.com>
:Issues: https://github.com/enovance/keystone-legacyv1-extension
:Source Code: https://github.com/enovance/keystone-legacyv1-extension
:License: Apache
:Version: 0.1

=================
Keystone Legacyv1
=================

An extension that allows to access keystone with v1 auth type (i.e: rackspace cloud files).

=====
Setup
=====

add this to your keystone.conf::

  [filter:legacyv1]
  paste.filter_factory = kslegacyv1:LegacyV1.factory

  [pipeline:legacyv1]
  pipeline = access_log sizelimit stats_monitoring url_normalize legacyv1 token_auth admin_token_auth xml_body json_body debug stats_reporting ec2_extension s3_extension service_v3

and add this to your ``[composite:main]``::

  /v1.0 = legacyv1
