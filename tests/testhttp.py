import unittest
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


class MockResponse(object):
    def getcode(self):
        return 200


class MockQuery(sparql._Query):
    def _get_response(self, opener, request, buf):
        self.querystring = request.get_data()
        return MockResponse()

    def _read_response(self, response, buf, timeout):
        try:
            from urlparse import parse_qs
        except ImportError:
            from cgi import parse_qs
        query = parse_qs(self.querystring).get('query', [''])[0]
        buf.write(QUERIES[query])


class TestSparqlEndpoint(unittest.TestCase):

    def setUp(self):
        self.old_Query = sparql._Query
        sparql._Query = MockQuery

    def tearDown(self):
        sparql._Query = self.old_Query

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


if __name__ == '__main__':
    unittest.main()
