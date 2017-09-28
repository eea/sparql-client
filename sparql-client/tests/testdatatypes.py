#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sparql


class TestLiterals(unittest.TestCase):

    def test_literal_same(self):
        """ Two literals with same language must be the same """
        l1 = sparql.Literal(u"Hello world",lang=u"en")
        l2 = sparql.Literal(u"Hello world",lang=u"en")
        self.assertEqual(l1, l2)

    def test_literal_notsame1(self):
        """ Two literals different language must be different """
        l1 = sparql.Literal(u"Hello world",lang=u"en")
        l2 = sparql.Literal(u"Hello world",lang=u"en-US")
        self.assertNotEqual(l1, l2)

    def test_literal_notsame2(self):
        """ Difference on both value and language """
        l1 = sparql.Literal(u"Hello world",lang=u"en")
        l2 = sparql.Literal(u"Hallo Welt",lang=u"de")
        self.assertNotEqual(l1, l2)

    def test_literal_notsame3(self):
        """ Two literals with same language must be the same """
        l1 = sparql.Literal(u"Hello world",lang=u"en")
        self.assertNotEqual(u"Hello world", l1)
        self.assertNotEqual(l1, u"Hello world")

    def test_compare_with_non_literal(self):
        l1 = sparql.Literal("hi")
        self.assertFalse(l1 == "hi")
        self.assertFalse(l1 == u"hi")
        self.assertFalse(l1 == None)
        self.assertFalse(l1 == 13)
        self.assertFalse(l1 == 13.0)
        self.assertFalse(l1 == ['hi'])
        self.assertFalse(l1 == {'hi': 'hi'})

    def test_convert_to_unicode(self):
        """ Literals should convert values to unicode when saving them """
        class SomeType(object):
            def __unicode__(self):
                return u"hello world"
        l = sparql.Literal(SomeType())
        self.assertEqual(str(l), "hello world")

    def test_repr(self):
        """ repr should return the literal in N3 syntax """
        l = sparql.Literal(u"Hello world")
        self.assertEqual(u'<Literal "Hello world">', repr(l))

class TestTypedLiterals(unittest.TestCase):

    def test_isinstance(self):
        """ Type literals are instances of RDFTerm """
        l = sparql.Literal(u"Hello world",u"http://www.w3.org/2001/XMLSchema#string")
        assert isinstance(l, sparql.RDFTerm)

    def test_repr(self):
        """ repr should return the literal in N3 syntax """
        l = sparql.Literal(u"Hello world",u"http://www.w3.org/2001/XMLSchema#string")
        self.assertEqual(u'<Literal "Hello world"^^<http://www.w3.org/2001/XMLSchema#string>>', repr(l))

    def test_str(self):
        """ str should return the literal without type """
        l = sparql.Literal(u"Hello world",u"http://www.w3.org/2001/XMLSchema#string")
        assert str(l) == u"Hello world"

    def test_literal_same(self):
        """ Two literals with same language must be the same """
        l1 = sparql.Literal(u"Hello world",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        l2 = sparql.Literal(u"Hello world",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        self.assertEqual(l1, l2)

    def test_literal_notsame1(self):
        """ Two literals different language must be different """
        l1 = sparql.Literal(u"Hello world",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        l2 = sparql.Literal(u"Hello world",u"http://www.w3.org/2001/XMLSchema#string")
        self.assertNotEqual(l1, l2)

    def test_literal_notsame2(self):
        """ Difference on both value and language """
        l1 = sparql.Literal(u"Hello world",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        l2 = sparql.Literal(u"Hallo Welt",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        self.assertNotEqual(l1, l2)

    def test_literal_notsame3(self):
        """ Two literals with same language must be the same """
        l1 = sparql.Literal(u"Hello world",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        self.assertNotEqual(u"Hello world", l1)
        self.assertNotEqual(l1, u"Hello world")
        assert l1 != u"Hello world"

    def test_compare_with_non_literal(self):
        l1 = sparql.Literal("hi",u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        self.assertFalse(l1 == "hi")
        self.assertFalse(l1 == u"hi")
        self.assertFalse(l1 == None)
        self.assertFalse(l1 == 13)
        self.assertFalse(l1 == 13.0)
        self.assertFalse(l1 == ['hi'])
        self.assertFalse(l1 == {'hi': 'hi'})

    def test_convert_to_unicode(self):
        """ Literals should convert values to unicode when saving them """
        class SomeType(object):
            def __unicode__(self):
                return u"hello world"
        l = sparql.Literal(SomeType(),u"http://aims.fao.org/aos/geopolitical.owl#MillionUSD")
        self.assertEqual(str(l), "hello world")

class TestIRIs(unittest.TestCase):

    def test_repr(self):
        """ repr should return the literal in N3 syntax """
        i = sparql.IRI("http://example.com/asdf")
        self.assertEqual(repr(i), "<IRI <http://example.com/asdf>>")

    def test_compare_with_non_iri(self):
        i1 = sparql.IRI("http://example.com/asdf")
        self.assertFalse(i1 == "http://example.com/asdf")
        self.assertFalse(i1 == u"http://example.com/asdf")
        self.assertFalse(i1 == None)
        self.assertFalse(i1 == 13)
        self.assertFalse(i1 == 13.0)
        self.assertFalse(i1 == ['http://example.com/asdf'])
        self.assertFalse(i1 == {'http://example.com/asdf':
                                'http://example.com/asdf'})

_literal_data = [
    (''                     , '""'),
    (' '                    , '" "'),
    ('hello'                , '"hello"'),
    ("back\\slash"          , '"back\\\\slash"'),
    ('quot"ed'              , '"quot\\"ed"'),
    ("any\"quot'es"         , '"any\\"quot\'es"'),
    ("new\nlines"           , '"new\\nlines"'),
    ("ta\tbs"               , '"ta\\tbs"'),
    (u"ascii-unicode"       , '"ascii-unicode"'),
    (u"̈Ünɨcøðé"             , '"\\u0308\\u00dcn\\u0268c\\u00f8\\u00f0\\u00e9"'),
    (u"\u6f22\u5b57(kanji)" , '"\u6f22\u5b57(kanji)"'),
]

class TestNotation3(unittest.TestCase):

    def test_literal(self):
        """ Notation3 representation of a literal """
        for value, expected in _literal_data:
            self.assertEqual(sparql.Literal(value).n3(), expected)
            self.assertEqual(sparql.Literal(value, lang='en').n3(), expected+'@en')

    def test_typed_literal(self):
        """ N3 notation of a typed literal """
        datatype = u"http://www.w3.org/2001/XMLSchema#string"
        for value, expected in _literal_data:
            tl = sparql.Literal(value, datatype)
            self.assertEqual(tl.n3(), '%s^^<%s>' % (expected, datatype))

if __name__ == '__main__':
    unittest.main()
