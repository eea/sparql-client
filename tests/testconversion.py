#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, date, time
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
                          u'foundingDate', u'timeexample'],
                         self.result.variables)

        rows = map(sparql.unpack_row, self.result.fetchall())
        row0 = rows[0]

        self.assertEqual(type(row0[2]), datetime)
        self.assertEqual(datetime(2009, 11, 02, 14, 31, 40), row0[2])

        self.assertEqual(type(row0[3]), date)
        self.assertEqual(date(1991, 8, 20), row0[3])

        self.assertEqual(type(row0[4]), time)
        self.assertEqual(time(18, 58, 21), row0[4])

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
            self.assertTrue(row0[2] is convert.return_value)
            convert.assert_called_with("18:58:21", sparql.XSD_TIME)
        finally:
            no_default_converters.stop()

    def test_custom_mapping(self):
        convert_datetime = Mock()
        row = list(self.result.fetchall())[0]
        unpacked_row = sparql.unpack_row(row, convert_type={
            sparql.XSD_DATETIME: convert_datetime,
        })
        self.assertTrue(unpacked_row[2] is convert_datetime.return_value)
        convert_datetime.assert_called_with("2009-11-02 14:31:40")


if __name__ == '__main__':
    unittest.main()
