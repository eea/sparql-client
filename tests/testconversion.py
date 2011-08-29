#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sparql
import os.path
from mock import Mock, patch

_dirname = os.path.dirname(__file__)

class TestConversion(unittest.TestCase):

    def test_date(self):
        """ Simple query with unbound variables """
        import dateutil # make sure python-dateutil is installed
        resultfp = open(os.path.join(_dirname, "dateexamples.srx"))
        result = sparql._ResultsParser(resultfp)
        self.assertEqual([u'name', u'lastupdated', u'entryCreated', u'foundingDate', u'timeexample'], result.variables)

        rows = map(sparql.unpack_row, result.fetchall())
        row0 = rows[0]
        self.assertEqual(1981,row0[2].year)
        self.assertEqual(18,row0[4].hour)
        self.assertEqual(21,row0[4].second)

    def test_custom_function(self):
        resultfp = open(os.path.join(_dirname, "dateexamples.srx"))
        convert = Mock()
        no_default_converters = patch('sparql._types', {})
        no_default_converters.start()
        try:
            result = sparql._ResultsParser(resultfp)
            row0 = sparql.unpack_row(list(result.fetchall())[0], convert)
            self.assertTrue(row0[0] is convert.return_value)
            convert.assert_called_with("18:58:21", "http://www.w3.org/2001/XMLSchema#time")
        finally:
            no_default_converters.stop()


if __name__ == '__main__':
    unittest.main()
