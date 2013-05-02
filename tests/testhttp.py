import unittest
#import urllib2
import pycurl2 as pycurl
from StringIO import StringIO
from mock import Mock, patch
import sparql

QUERIES = {
"SELECT * WHERE {?s ?p ?o} LIMIT 2": """\
<?xml version='1.0' encoding='UTF-8'?>
<sparql xmlns='http://www.w3.org/2005/sparql-results#'>
  <head>
    <variable name='s'/>
    <variable name='p'/>
    <variable name='o'/>
  </head>
  <results>
    <result>
      <binding name='s'>
        <uri>http://rdfdata.eionet.europa.eu/eea/languages/en</uri>
      </binding>
      <binding name='p'>
        <uri>http://www.w3.org/1999/02/22-rdf-syntax-ns#type</uri>
      </binding>
      <binding name='o'>
        <uri>http://rdfdata.eionet.europa.eu/eea/ontology/Language</uri>
      </binding>
    </result>
    <result>
      <binding name='s'>
        <uri>http://rdfdata.eionet.europa.eu/eea/languages/da</uri>
      </binding>
      <binding name='p'>
        <uri>http://www.w3.org/1999/02/22-rdf-syntax-ns#type</uri>
      </binding>
      <binding name='o'>
        <uri>http://rdfdata.eionet.europa.eu/eea/ontology/Language</uri>
      </binding>
    </result>
  </results>
</sparql>
"""
}

class MockCurl(object):
    def setopt(self, opt, value):
        if opt == pycurl.WRITEFUNCTION:
            self.writefunction = value
        if opt == pycurl.URL:
            self.url = value

    def perform(self):
        try:
            from urlparse import parse_qs
        except ImportError:
            from cgi import parse_qs
        querystring = self.url.split('?', 1)[1]
        query = parse_qs(querystring).get('query', [''])[0]

        self.writefunction(QUERIES[query])
        return

    def getinfo(self, info):
        return 200

class MockSparql(object):

    def start(self):
        self.pycurl_patch = patch('sparql.pycurl')
        mock_pycurl = self.pycurl_patch.start()
        mock_pycurl.Curl = self.mock_Curl
        mock_pycurl.WRITEFUNCTION = pycurl.WRITEFUNCTION
        mock_pycurl.URL = pycurl.URL

    def stop(self):
        self.pycurl_patch.stop()

    def mock_Curl(self):
        return MockCurl()


class TestSparqlEndpoint(unittest.TestCase):

    def setUp(self):
        self.mock_sparql = MockSparql()
        self.mock_sparql.start()

    def tearDown(self):
        self.mock_sparql.stop()

    def test_simple_query(self):
        from sparql import IRI
        URI_LANG = 'http://rdfdata.eionet.europa.eu/eea/languages'
        URI_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        URI_LANG_TYPE = 'http://rdfdata.eionet.europa.eu/eea/ontology/Language'
        endpoint = "http://cr3.eionet.europa.eu/sparql"

        result = sparql.query(endpoint, "SELECT * WHERE {?s ?p ?o} LIMIT 2")

        self.assertEqual(result.variables, ['s', 'p', 'o'])
        self.assertEqual(list(result), [
            (IRI(URI_LANG+'/en'), IRI(URI_TYPE), IRI(URI_LANG_TYPE)),
            (IRI(URI_LANG+'/da'), IRI(URI_TYPE), IRI(URI_LANG_TYPE)),
        ])
