#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sparql
from dateutil.parser import parse as date_parser
import datetime
import os.path

class TestDates(unittest.TestCase):
    def test_simple(self):
        """ Simple query with unbound variables """
        resultfp = open(os.path.join(os.path.dirname(__file__),
                        "dateexamples.srx"))
        sparql.set_converter(sparql.XSD_DATETIME, date_parser)
        sparql.set_converter(sparql.XSD_DATE, date_parser)
        sparql.set_converter(sparql.XSD_TIME, date_parser)
        result = sparql._ResultsParser(resultfp)
        self.assertEqual([u'name', u'lastupdated', u'entryCreated', u'foundingDate', u'timeexample'], result.variables)

        rows = map(sparql.unpack_row, result.fetchall())
        row0 = rows[0]
        self.assertEqual(1981,row0[2].year)
        self.assertEqual(18,row0[4].hour)
        self.assertEqual(21,row0[4].second)


if __name__ == '__main__':
    unittest.main()
