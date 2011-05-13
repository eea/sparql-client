#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sparql
import os.path

def _open_datafile(name):
    return open(os.path.join(os.path.dirname(__file__), name))

class TestParser(unittest.TestCase):

    def test_simple(self):
        """ Simple query with unbound variables """
        resultfp = _open_datafile("countries.srx")
        result = sparql._ResultsParser(resultfp)
        self.assertEqual([u'eeaURI', u'gdpTotal', u'eeacode', u'nutscode', u'faocode', u'gdp', u'name'], result.variables)

        rows = map(sparql.unpack_row, result.fetchall())
        row0 = rows[0]
        self.assertEqual("http://rdfdata.eionet.europa.eu/eea/countries/BE", str(row0[0]))
        self.assertEqual(sparql.IRI(u"http://rdfdata.eionet.europa.eu/eea/countries/BE"), row0[0])
        self.assertEqual(44.252934, row0[5])
        self.assertNotEqual("471161.0", row0[1])
        self.assertEqual("471161.0", str(row0[1]))

    def test_fetchmany(self):
        """ Simple query with unbound variables """
        resultfp = _open_datafile("countries.srx")
        result = sparql._ResultsParser(resultfp)
        self.assertEqual([u'eeaURI', u'gdpTotal', u'eeacode', u'nutscode', u'faocode', u'gdp', u'name'], result.variables)

        rows = result.fetchmany(2)
        self.assertEqual(2, len(rows))
        row0 = rows[0]
        self.assertEqual("http://rdfdata.eionet.europa.eu/eea/countries/BE", str(row0[0]))
        rows = result.fetchmany(2)
        self.assertEqual(1, len(rows))
        row0 = rows[0]
        assert str(row0[6]) == "Japan"

    def test_ask_query(self):
        """ Check that http://www.w3.org/TR/rdf-sparql-XMLres/output2.srx works """
        resultfp = _open_datafile("w3-output2.srx")
        result = sparql._ResultsParser(resultfp)
        rows = result.fetchall()
        assert len(rows) == 0


#       for row in result.fetchone():
#           print row
#       row1 = result.fetchone()
#       print row1[0]

    def test_w3_example(self):
        """ Check that http://www.w3.org/TR/rdf-sparql-XMLres/output.srx works """
        resultfp = _open_datafile("w3-output.srx")
        result = sparql._ResultsParser(resultfp)
        self.assertEqual([u'x', u'hpage', u'name', u'mbox', u'age', u'blurb', u'friend'], result.variables)
        rows = result.fetchall()
        row0 = rows[0]
        self.assertEqual("http://work.example.org/alice/", str(row0[1]))

    def test_hasresult(self):
        """ Check that http://www.w3.org/TR/rdf-sparql-XMLres/output2.srx works """
        resultfp = _open_datafile("w3-output2.srx")
        result = sparql._ResultsParser(resultfp)
        assert result.hasresult() == True

    def test_national(self):
        """ Simple query with UTF-8 """
        resultfp = _open_datafile("national.srx")
        result = sparql._ResultsParser(resultfp)
        self.assertEqual([u'subj', u'nameen', u'nameru'], result.variables)

        rows = result.fetchall()
        row0 = rows[0]
        self.assertEqual("http://aims.fao.org/aos/geopolitical.owl#Germany", str(row0[0]))
        self.assertEqual(sparql.IRI(u"http://aims.fao.org/aos/geopolitical.owl#Germany"), row0[0])
        self.assertEqual(u"Германия", unicode(row0[2]))


if __name__ == '__main__':
    unittest.main()
