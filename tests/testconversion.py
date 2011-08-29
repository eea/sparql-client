#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sparql
import os.path
from mock import Mock, patch

_dirname = os.path.dirname(__file__)

class TestConversion(unittest.TestCase):

    def setUp(self):
        self._fp = open(os.path.join(_dirname, "xsdtypes.srx"))
        self.result = sparql._ResultsParser(self._fp)

    def tearDown(self):
        self._fp.close()

    def test_date(self):
        """ Simple query with unbound variables """
        import dateutil # make sure python-dateutil is installed
        self.assertEqual([u'name', u'decimalData', u'lastupdated',
                          u'entryCreated', u'foundingDate', u'timeexample'],
                         self.result.variables)

        rows = map(sparql.unpack_row, self.result.fetchall())
        row0 = rows[0]
        self.assertEqual(1981,row0[3].year)
        self.assertEqual(18,row0[5].hour)
        self.assertEqual(21,row0[5].second)

    def test_decimal(self):
        import decimal
        self.assertEqual(self.result.variables[1], 'decimalData')
        row0 = map(sparql.unpack_row, self.result.fetchall())[0]
        decval = row0[1]
        self.assertEqual(type(decval), decimal.Decimal)
        self.assertEqual(str(decval), "123.456")

    def test_custom_function(self):
        convert = Mock()
        no_default_converters = patch('sparql._types', {})
        no_default_converters.start()
        try:
            row0 = sparql.unpack_row(list(self.result.fetchall())[0], convert)
            self.assertTrue(row0[0] is convert.return_value)
            convert.assert_called_with("18:58:21", sparql.XSD_TIME)
        finally:
            no_default_converters.stop()


if __name__ == '__main__':
    unittest.main()
