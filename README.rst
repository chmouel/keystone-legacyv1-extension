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

install it by the way you install things on your system (be it
puppet/packages/source checkin/etc..)

add this to your keystone.conf (before the ``[composite::main]`` stanza)::

  [filter:legacyv1]
  paste.filter_factory = kslegacyv1:LegacyV1.factory

  [pipeline:legacyv1]
  pipeline = access_log sizelimit stats_monitoring url_normalize debug legacyv1 public_service

and add this to your ``[composite:main]``::

  /v1.0 = legacyv1

=====
Usage
=====

A auth will look like this::

  -$ curl -i -H 'X-Auth-Key: password' -H 'X-Auth-User: admin:admin' http://keystone:5000/v1.0
  HTTP/1.1 200 OK
  X-Auth-Token: abc5f71626314741972e0dd0d7c68307
  X-Storage-Token: abc5f71626314741972e0dd0d7c68307
  X-Storage-Url: http://172.16.129.140:8080/v1/AUTH_53cb88355ea24a0ea79383ca80dbae4e
  Vary: X-Auth-Token,X-Storage-Token,X-Storage-Url
  Content-Type: text/xml
  Content-Length: 0
  Date: Sun, 24 Mar 2013 16:27:25 GMT

It should be easy to use cyberduck without any hack as long you
configure your keystone under ssl or via a reverse proxy.

====
TODO
====

- Tests.
