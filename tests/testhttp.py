import unittest
import urllib2
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


class MockSparql(object):

    def start(self):
        self.urllib2_patch = patch('sparql.urllib2')
        mock_urllib2 = self.urllib2_patch.start()
        mock_urllib2.Request = urllib2.Request
        mock_urllib2.urlopen = self.mock_urlopen

    def stop(self):
        self.urllib2_patch.stop()

    def mock_urlopen(self, request):
        try:
            from urlparse import parse_qs
        except ImportError:
            from cgi import parse_qs
        query = parse_qs(request.get_data()).get('query', [''])[0]

        response = Mock()
        response.fp = StringIO(QUERIES[query])
        return response


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
