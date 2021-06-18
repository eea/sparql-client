#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Original Code is "SPARQL Client"
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) 2011 by European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
#  Søren Roug, EEA
#  Alex Morega, Eau de Web
#  David Bătrânu, Eau de Web

"""
The `sparql` module can be invoked in several different ways. To quickly run a
query use :func:`query`. Results are encapsulated in a
:class:`_ResultsParser` instance::

    >>> result = sparql.query(endpoint, query)
    >>> for row in result:
    >>>    print(row)


Command-line use
----------------

::

    sparql.py [-i] endpoint
        -i Interactive mode

If interactive mode is enabled, the program reads queries from the console
and then executes them. Use a double line (two 'enters') to separate queries.

Otherwise, the query is read from standard input.
"""

from base64 import b64encode
from six.moves import input, map
from six.moves.urllib.parse import urlencode
from xml.dom import pulldom
from xml.sax import SAXParseException
import copy
import decimal
import re
import tempfile
import eventlet
import six

if six.PY2:
    from eventlet.green import urllib2 as ev_request
    import compiler
else:
    from eventlet.green.urllib import request as ev_request
    import ast as astcompiler

try:
    __version__ = open('version.txt').read().strip()
except Exception:
    __version__ = "2.6"

USER_AGENT = "sparql-client/%s +https://www.eionet.europa.eu/software/sparql-client/" % __version__

CONTENT_TYPE = {
    'turtle': "application/turtle",
    'n3': "application/n3",
    'rdfxml': "application/rdf+xml",
    'ntriples': "application/n-triples",
    'xml': "application/xml"
}

RESULTS_TYPES = {
    'xml': "application/sparql-results+xml",
    'xmlschema': "application/x-ms-access-export+xml",
    'json': "application/sparql-results+json"
}

# The purpose of this construction is to use shared strings when
# they have the same value. This way comparisons can happen on the
# memory address rather than looping through the content.
XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string'
XSD_INT = 'http://www.w3.org/2001/XMLSchema#int'
XSD_LONG = 'http://www.w3.org/2001/XMLSchema#long'
XSD_DOUBLE = 'http://www.w3.org/2001/XMLSchema#double'
XSD_FLOAT = 'http://www.w3.org/2001/XMLSchema#float'
XSD_INTEGER = 'http://www.w3.org/2001/XMLSchema#integer'
XSD_DECIMAL = 'http://www.w3.org/2001/XMLSchema#decimal'
XSD_DATETIME = 'http://www.w3.org/2001/XMLSchema#dateTime'
XSD_DATE = 'http://www.w3.org/2001/XMLSchema#date'
XSD_TIME = 'http://www.w3.org/2001/XMLSchema#time'
XSD_BOOLEAN = 'http://www.w3.org/2001/XMLSchema#boolean'

datatype_dict = {
    '': '',
    XSD_STRING: XSD_STRING,
    XSD_INT: XSD_INT,
    XSD_LONG: XSD_LONG,
    XSD_DOUBLE: XSD_DOUBLE,
    XSD_FLOAT: XSD_FLOAT,
    XSD_INTEGER: XSD_INTEGER,
    XSD_DECIMAL: XSD_DECIMAL,
    XSD_DATETIME: XSD_DATETIME,
    XSD_DATE: XSD_DATE,
    XSD_TIME: XSD_TIME,
    XSD_BOOLEAN: XSD_BOOLEAN
}

# allow import from RestrictedPython
__allow_access_to_unprotected_subobjects__ = {
    'Datatype': 1, 'unpack_row': 1,
    'RDFTerm': 1, 'IRI': 1,
    'Literal': 1, 'BlankNode': 1
}


def Datatype(value):
    """
    Replace the string with a shared string.
    intern() only works for plain strings - not unicode.
    We make it look like a class, because it conceptually could be.
    """
    if value is None:
        r = None
    elif value in datatype_dict:
        r = datatype_dict[value]
    else:
        r = datatype_dict[value] = value
    return r


class RDFTerm(object):
    """
    Super class containing methods to override. :class:`IRI`,
    :class:`Literal` and :class:`BlankNode` all inherit from :class:`RDFTerm`.
    """

    __allow_access_to_unprotected_subobjects__ = {'n3': 1}

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return self.value

    def n3(self):
        """ Return a Notation3 representation of this term. """
        # To override
        # See N-Triples syntax: http://www.w3.org/TR/rdf-testcases/#ntriples
        raise NotImplementedError("Subclasses of RDFTerm must implement `n3`")

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.n3())


class IRI(RDFTerm):
    """ An RDF resource. """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value.encode("unicode-escape")

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.value == other.value:
            return True
        return False

    def n3(self):
        return '<%s>' % self.value


_n3_quote_char = re.compile(r'[^ -~]|["\\]')
_n3_quote_map = {
    '"': '\\"',
    '\n': '\\n',
    '\t': '\\t',
    '\\': '\\\\',
}


def _n3_quote(string):
    def escape(m):
        ch = m.group()
        if ch in _n3_quote_map:
            return _n3_quote_map[ch]
        return "\\u%04x" % ord(ch)

    return '"' + _n3_quote_char.sub(escape, string) + '"'


class Literal(RDFTerm):
    """
    Literals. These can take a data type or a language code.
    """

    def __init__(self, value, datatype=None, lang=None):
        self.value = six.text_type(value)
        self.lang = lang
        self.datatype = datatype

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        elif (self.value == other.value and
              self.lang == other.lang and
              self.datatype == other.datatype):
            return True

        return False

    def n3(self):
        n3_value = _n3_quote(self.value)

        if self.datatype is not None:
            n3_value += '^^<%s>' % self.datatype

        if self.lang is not None:
            n3_value += '@' + self.lang

        return n3_value


class BlankNode(RDFTerm):
    """ Blank node. Similar to `IRI` but lacks a stable identifier. """

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.value == other.value:
            return True
        return False

    def n3(self):
        return '_:%s' % self.value


_n3parser_lang = re.compile(r'@(?P<lang>\w+)$')
_n3parser_datatype = re.compile(r'\^\^<(?P<datatype>[^\^"\'>]+)>$')


def parse_n3_term(src):
    """
    Parse a Notation3 value into a RDFTerm object (IRI or Literal).

    This parser understands IRIs and quoted strings; basic non-string types
    (integers, decimals, booleans, etc) are not supported yet.
    """

    src = six.text_type(src)

    if src.startswith('<'):
        # `src` is an IRI
        if not src.endswith('>'):
            raise ValueError

        value = src[1:-1]
        if '<' in value or '>' in value:
            raise ValueError

        return IRI(value)

    else:
        datatype_match = _n3parser_datatype.search(src)
        if datatype_match is not None:
            datatype = datatype_match.group('datatype')
            src = _n3parser_datatype.sub('', src)
        else:
            datatype = None

        lang_match = _n3parser_lang.search(src)
        if lang_match is not None:
            lang = lang_match.group('lang')
            src = _n3parser_lang.sub('', src)
        else:
            lang = None

        # Python literals syntax is mostly compatible with N3.
        # We don't execute the code, just turn it into an AST.
        try:
            if six.PY2:
                ast = compiler.parse("value = u" + src)
            else:
                # should be fixed due to #111217
                ast = astcompiler.parse("value = " + src)
        except:
            raise ValueError

        if six.PY2:
            # Don't allow any extra tokens in the AST
            if len(ast.node.getChildNodes()) != 1:
                raise ValueError
            assign_node = ast.node.getChildNodes()[0]
            if len(assign_node.getChildNodes()) != 2:
                raise ValueError
            value_node = assign_node.getChildNodes()[1]
            if value_node.getChildNodes():
                raise ValueError
            if value_node.__class__ != compiler.ast.Const:
                raise ValueError
            value = value_node.value
        else:
            # Don't allow any extra tokens in the AST
            if len(ast.body) != 1:
                raise ValueError
            assign_node = ast.body[0]

            # type_comment is added since 3.8, discard it from condition check
            if len(assign_node._fields) != 2 and len(tuple(f for f in assign_node._fields if f != "type_comment")) != 2:
                raise ValueError

            value_node = assign_node.value
            if len(value_node._fields) != 1:
                if not isinstance(value_node, astcompiler.Constant):
                    raise ValueError

            # if value_node.__class__ != ast.Constant():
            #     raise ValueError
            value = getattr(value_node, value_node._fields[0])

        if type(value) is not six.text_type:
            raise ValueError

        return Literal(value, datatype, lang)


#########################################
#
# _ServiceMixin
#
#########################################


class _ServiceMixin(object):
    def __init__(self, endpoint, method="POST", accept=RESULTS_TYPES['xml']):
        self._method = method
        self.endpoint = endpoint
        self._default_graphs = []
        self._named_graphs = []
        self._prefix_map = {}

        self._headers_map = {}
        self._headers_map['Accept'] = accept
        self._headers_map['User-Agent'] = USER_AGENT

    def _setMethod(self, method):
        if method in ("GET", "POST"):
            self._method = method
        else:
            raise ValueError("Only GET or POST is allowed")

    def _getMethod(self):
        return self._method

    method = property(_getMethod, _setMethod)

    def addDefaultGraph(self, g):
        self._default_graphs.append(g)

    def defaultGraphs(self):
        return self._default_graphs

    def addNamedGraph(self, g):
        self._named_graphs.append(g)

    def namedGraphs(self):
        return self._named_graphs

    def setPrefix(self, prefix, uri):
        self._prefix_map[prefix] = uri

    def prefixes(self):
        return self._prefix_map

    def headers(self):
        return self._headers_map


#########################################
#
# Service
#
#########################################


class Service(_ServiceMixin):
    """
    This is the main entry to the library.
    The user creates a :class:`Service`, then sends a query to it.
    If we want to have persistent connections, then open them here.
    """

    def __init__(self, endpoint, qs_encoding="utf-8", method="POST",
                 accept="application/sparql-results+xml"):
        _ServiceMixin.__init__(self, endpoint, method, accept)
        self.qs_encoding = qs_encoding

    def createQuery(self):
        q = _Query(self)
        q._default_graphs = copy.deepcopy(self._default_graphs)
        q._headers_map = copy.deepcopy(self._headers_map)
        q._named_graphs = copy.deepcopy(self._named_graphs)
        q._prefix_map = copy.deepcopy(self._prefix_map)
        return q

    def query(self, query, timeout=0, raw=False):
        q = self.createQuery()
        return q.query(query, timeout, raw=raw)

    def authenticate(self, username, password):
        cred = b64encode("{}:{}".format(username, password).encode()).decode()
        head = "Basic {}".format(cred)
        self._headers_map['Authorization'] = head


def _parseBoolean(val):
    return val.lower() in ('true', '1')


# XMLSchema types and cast functions
_types = {
    XSD_INT: int,
    XSD_LONG: int,
    XSD_DOUBLE: float,
    XSD_FLOAT: float,
    XSD_INTEGER: int,  # INTEGER is a DECIMAL, but Python `int` has no size
    # limit, so it's safe to use
    XSD_DECIMAL: decimal.Decimal,
    XSD_BOOLEAN: _parseBoolean,
}

try:
    import dateutil.parser

    _types[XSD_DATETIME] = dateutil.parser.parse
    _types[XSD_DATE] = lambda v: dateutil.parser.parse(v).date()
    _types[XSD_TIME] = lambda v: dateutil.parser.parse(v).time()
except ImportError:
    pass


def unpack_row(row, convert=None, convert_type={}):
    """
    Convert values in the given row from :class:`RDFTerm` objects to plain
    Python values: :class:`IRI` is converted to a unicode string containing
    the IRI value; :class:`BlankNode` is converted to a unicode string with
    the BNode's identifier, and :class:`Literal` is converted based on its
    XSD datatype.

    The library knows about common XSD types (STRING becomes :class:`unicode`,
    INTEGER and LONG become :class:`int`, DOUBLE and FLOAT become
    :class:`float`, DECIMAL becomes :class:`~decimal.Decimal`, BOOLEAN becomes
    :class:`bool`). If the `python-dateutil` library is found, then DATE,
    TIME and DATETIME are converted to :class:`~datetime.date`,
    :class:`~datetime.time` and :class:`~datetime.datetime` respectively.  For
    other conversions, an extra argument `convert` may be passed. It should be
    a callable accepting two arguments: the serialized value as a
    :class:`unicode` object, and the XSD datatype.
    """
    out = []
    known_types = dict(_types)
    known_types.update(convert_type)
    for item in row:
        if item is None:
            value = None
        elif isinstance(item, Literal):
            if item.datatype in known_types:
                to_python = known_types[item.datatype]
                value = to_python(item.value)
            elif convert is not None:
                value = convert(item.value, item.datatype)
            else:
                value = item.value
        else:
            value = item.value
        out.append(value)
    return out


#########################################
#
# _Query
#
#########################################


class _Query(_ServiceMixin):

    def __init__(self, service):
        _ServiceMixin.__init__(self, service.endpoint, service.method)

    def _build_request(self, query):
        if self.method == "GET":
            if '?' in self.endpoint:
                separator = '&'
            else:
                separator = '?'
            uri = self.endpoint.strip() + separator + query
            return ev_request.Request(uri)
        else:
            # uri = self.endpoint.strip().encode('ASCII')
            uri = self.endpoint.strip()
            return ev_request.Request(uri, data=query)

    def _get_response(self, opener, request, buf, timeout=None):
        try:
            response = opener.open(request, timeout=timeout)
            response_code = response.getcode()
            if response_code != 200:
                buf.seek(0)
                ret = buf.read()
                buf.close()
                raise SparqlException(response_code, ret)
            else:
                return response
        except SparqlException as error:
            raise SparqlException('Error', error.message)
        else:
            return ''

    def _read_response(self, response, buf, timeout):
        if timeout > 0:
            with eventlet.timeout.Timeout(timeout):
                try:
                    buf.write(response.read())
                except eventlet.timeout.Timeout as error:
                    raise SparqlException('Timeout', repr(error))
        else:
            buf.write(response.read())

    def _build_response(self, query, opener, buf, timeout):
        request = self._build_request(query)
        if type(query) is not bytes and not six.PY2:
            query = query.encode()
        return self._get_response(opener, request, buf,
                                  timeout if timeout > 0 else None)

    def _request(self, statement, timeout=0):
        """
        Builds the query string, then opens a connection to the endpoint
        and returns the file descriptor.
        """
        query = self._queryString(statement)
        buf = tempfile.NamedTemporaryFile()

        opener = ev_request.build_opener(RedirectHandler)
        opener.addheaders = list(self.headers().items())
        try:
            if type(query) is not bytes and not six.PY2:
                query = query.encode()
            response = self._build_response(query, opener, buf, timeout)
        except SparqlException as error:
            self.endpoint = error.message
            response = self._build_response(query, opener, buf, timeout)

        self._read_response(response, buf, timeout)
        buf.seek(0)
        return buf

    def query(self, statement, timeout=0, raw=False):
        """
        Sends the request and starts the parser on the response.
        """
        response = self._request(statement, timeout)
        if raw:
            return response

        return _ResultsParser(response)

    def _queryString(self, statement):
        """
        Creates the REST query string from the statement and graphs.
        """
        args = []
        # refs #72876 removing the replace of newline to allow the comments in sparql queries
        # statement = statement.replace("\n", " ").encode('utf-8')
        # not needed py3
        # statement = statement.encode('utf-8')

        pref = ' '.join(["PREFIX %s: <%s> " % (p, self._prefix_map[p]) for p in self._prefix_map])
        if six.PY2:
            statement = pref + statement
        else:
            statement = pref.encode() + statement.encode()

        args.append(('query', statement))

        for uri in self.defaultGraphs():
            args.append(('default-graph-uri', uri))

        for uri in self.namedGraphs():
            args.append(('named-graph-uri', uri))
        if six.PY2:
            return urlencode(args).encode('utf-8')
        return urlencode(args)


class RedirectHandler(ev_request.HTTPRedirectHandler):
    """
    Subclass the HTTPRedirectHandler to re-contruct request when follow redirect
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307):
            raise SparqlException(code, newurl)
        else:
            return req


class _ResultsParser(object):
    """
    Parse the XML result.
    """

    __allow_access_to_unprotected_subobjects__ = {
        'fetchone': 1,
        'fetchmany': 1,
        'fetchall': 1,
        'hasresult': 1,
        'variables': 1
    }

    def __init__(self, fp):
        self.__fp = fp
        self._vals = []
        self._hasResult = None
        self.variables = []
        self._fetchhead()

    def __del__(self):
        self.__fp.close()

    def _fetchhead(self):
        """
        Fetches the head information. If there are no variables in the
        <head>, then we also fetch the boolean result.
        """
        self.events = pulldom.parse(self.__fp)

        for (event, node) in self.events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'variable':
                    self.variables.append(node.attributes['name'].value)
                elif node.tagName == 'boolean':
                    self.events.expandNode(node)
                    self._hasResult = (node.firstChild.data == 'true')
                elif node.tagName == 'result':
                    return  # We should not arrive here
            elif event == pulldom.END_ELEMENT:
                if node.tagName == 'head' and self.variables:
                    return
                elif node.tagName == 'sparql':
                    return

    def hasresult(self):
        """
        ASK queries are used to test if a query would have a result.  If the
        query is an ASK query there won't be an actual result, and
        :func:`fetchone` will return nothing. Instead, this method can be
        called to check the result from the ASK query.

        If the query is a SELECT statement, then the return value of
        :func:`hasresult` is `None`, as the XML result format doesn't tell you
        if there are any rows in the result until you have read the first one.
        """
        return self._hasResult

    def __iter__(self):
        """ Synonym for :func:`fetchone`. """
        return self.fetchone()

    def fetchone(self):
        """ Fetches the next set of rows of a query result, returning a list.
            An empty list is returned when no more rows are available.
            If the query was an ASK request, then an empty list is returned as
            there are no rows available.
        """
        idx = -1

        try:
            for (event, node) in self.events:
                if event == pulldom.START_ELEMENT:
                    if node.tagName == 'result':
                        self._vals = [None] * len(self.variables)
                    elif node.tagName == 'binding':
                        idx = self.variables.index(node.attributes['name'].value)
                    elif node.tagName == 'uri':
                        self.events.expandNode(node)
                        data = ''.join(t.data for t in node.childNodes)
                        self._vals[idx] = IRI(data)
                    elif node.tagName == 'literal':
                        self.events.expandNode(node)
                        data = ''.join(t.data for t in node.childNodes)
                        lang = node.getAttribute('xml:lang') or None
                        datatype = Datatype(node.getAttribute('datatype')) or None
                        self._vals[idx] = Literal(data, datatype, lang)
                    elif node.tagName == 'bnode':
                        self.events.expandNode(node)
                        data = ''.join(t.data for t in node.childNodes)
                        self._vals[idx] = BlankNode(data)
                elif event == pulldom.END_ELEMENT:
                    if node.tagName == 'result':
                        # print "rtn:", len(self._vals), self._vals
                        yield tuple(self._vals)
        except SAXParseException as e:
            if six.PY2:
                message = e.message
            else:
                message = e.getMessage()
            faultString = 'The data is ' + message
            print(faultString)
            yield tuple()

    def fetchall(self):
        """ Loop through the result to build up a list of all rows.
            Patterned after DB-API 2.0.
        """
        result = []
        for row in self.fetchone():
            result.append(row)
        return result

    def fetchmany(self, num):
        result = []
        for row in self.fetchone():
            result.append(row)
            num -= 1
            if num <= 0:
                return result
        return result


def query(endpoint, query, timeout=0, qs_encoding="utf-8", method="POST",
          accept="application/sparql-results+xml", raw=False):
    """
    Convenient method to execute a query. Exactly equivalent to::

        sparql.Service(endpoint).query(query)
    """
    s = Service(endpoint, qs_encoding, method, accept)
    return s.query(query, timeout, raw=raw)


def _interactive(endpoint):
    while True:
        try:
            lines = []
            while True:
                next = input()
                if not next:
                    break
                else:
                    lines.append(next)

            if lines:
                sys.stdout.write("Querying...")
                result = query(endpoint, " ".join(lines))
                sys.stdout.write("  done\n")

                for row in result.fetchone():
                    print("\t".join(map(six.text_type, row)))
                lines = []

        except Exception as e:
            sys.stderr.write(str(e))


class SparqlException(Exception):
    """ Sparql Exceptions """

    def __init__(self, code, message):
        self.code = code
        self.message = message


if __name__ == '__main__':
    import sys
    import codecs
    from optparse import OptionParser

    try:
        c = codecs.getwriter(sys.stdout.encoding)
    except Exception:
        c = codecs.getwriter('ascii')
    sys.stdout = c(sys.stdout, 'replace')

    parser = OptionParser(usage="%prog [-i] endpoint",
                          version="%prog " + str(__version__))
    parser.add_option("-i", dest="interactive", action="store_true",
                      help="Enables interactive mode")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("Endpoint must be specified")

    endpoint = args[0]

    if options.interactive:
        _interactive(endpoint)

    q = sys.stdin.read()
    try:
        result = query(endpoint, q)
        for row in result.fetchone():
            print("\t".join(map(six.text_type, row)))
    except SparqlException as e:
        if six.PY2:
            message = e.message
        else:
            message = e.getMessage()
        faultString = message
        print(faultString)
