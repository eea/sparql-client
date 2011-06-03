import unittest
import sparql

_string_literals = [
    ('""', ''), # empty string
    ("''", ''), # empty string
    ('""""""', ''), # triple quotes (")
    ("''''''", ''), # triple quotes (')
    ('" "', ' '), # one space
    ('"hi"', 'hi'),
    ("'hi'", 'hi'),
    ("'some\\ntext'", 'some\ntext'), # newline
    ("'some\\ttext'", 'some\ttext'), # tab
    ("'''some\ntext\n   with spaces'''", 'some\ntext\n   with spaces'),
]

from testdatatypes import _literal_data
for _value, _n3 in _literal_data:
    _string_literals.append((_n3, _value))


class N3ParsingTest(unittest.TestCase):

    def test_unicode(self):
        value = 'http://example.com/some_iri'
        class Tricky(object):
            def __unicode__(self):
                return '<%s>' % value
        self.assertEqual(sparql.parse_n3_term(Tricky()), sparql.IRI(value))

    def test_parse_IRI(self):
        value = 'http://example.com/some_iri'
        result = sparql.parse_n3_term('<%s>' % value)
        self.assertTrue(type(result) is sparql.IRI)
        self.assertEqual(result.value, value)

        i = sparql.IRI(value)
        self.assertEqual(sparql.parse_n3_term(i.n3()), i)

    def test_IRI_error(self):
        parse = sparql.parse_n3_term
        self.assertRaises(ValueError, parse, '<http://bro.ken/iri')
        self.assertRaises(ValueError, parse, 'http://bro.ken/iri>')
        self.assertRaises(ValueError, parse, '<http://bro.ken/i<ri>')
        self.assertRaises(ValueError, parse, '<http://bro.ken/i>ri>')

    def test_literal(self):
        for n3_value, value in _string_literals:
            result = sparql.parse_n3_term(n3_value)
            self.assertTrue(type(result) is sparql.Literal)
            self.assertEqual(result.lang, None)
            self.assertEqual(result.value, value)

            l = sparql.Literal(value)
            self.assertEqual(sparql.parse_n3_term(l.n3()), l)

    def test_literal_with_lang(self):
        for n3_value, value in _string_literals:
            n3_value_with_lang = n3_value + '@en'
            result = sparql.parse_n3_term(n3_value_with_lang)
            self.assertTrue(type(result) is sparql.Literal)
            self.assertEqual(result.lang, 'en')
            self.assertEqual(result.value, value)

            l = sparql.Literal(value, lang='en')
            self.assertEqual(sparql.parse_n3_term(l.n3()), l)

    def test_typed_literals(self):
        million_uri = u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD"
        for n3_value, value in _string_literals:
            n3_value_with_type = n3_value + '^^<' + million_uri + '>'
            result = sparql.parse_n3_term(n3_value_with_type)
            self.assertTrue(type(result) is sparql.Literal)
            self.assertEqual(result.datatype, million_uri)
            self.assertEqual(result.value, value)

            l = sparql.Literal(value, million_uri)
            self.assertEqual(sparql.parse_n3_term(l.n3()), l)

    def test_evil_literals(self):
        parse = sparql.parse_n3_term
        self.assertRaises(ValueError, parse, '"hello" + " world"')
        self.assertRaises(ValueError, parse, '"hello"\nx = " world"')
        self.assertRaises(ValueError, parse, 'hello')
