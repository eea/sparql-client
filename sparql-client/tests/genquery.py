#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six.moves.urllib.request
import six.moves.urllib.parse
import six.moves.urllib.error
import six.moves.urllib.request
import six.moves.urllib.error
import six.moves.urllib.parse

statement = open('code.rq').read()
query = {'query': statement, 'format': 'xml'}

qs = six.moves.urllib.parse.urlencode(query)
print qs
url = 'http://dbpedia.org/sparql?' \
    + six.moves.urllib.parse.urlencode(query)

opener = \
    six.moves.urllib.request.build_opener(six.moves.urllib.request.HTTPHandler)
six.moves.urllib.request.install_opener(opener)
req = six.moves.urllib.request.Request(url)

# req.add_header("Accept", "application/xml")

try:
    conn = six.moves.urllib.request.urlopen(req, timeout=10)
except Exception:
    conn = None

if not conn:
    raise IOError('Failure in open')

data = conn.read()
conn.close()
print data
