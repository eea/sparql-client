Welcome to sparql-client!
=========================

sparql-client is a SPARQL query library that performs `SELECT` and `ASK`
queries against a SPARQL endpoint via HTTP.

API based on `SPARQL JavaScript Library`_ by Lee Feigenbaum and Elias Torres.
Heavy influence from Juan Manuel Caicedo's SPARQL library

.. _`SPARQL JavaScript Library`: http://www.thefigtrees.net/lee/sw/sparql.js


Briefly, here is how it works::

    >>> import sparql

    >>> q = ('SELECT DISTINCT ?station, ?orbits WHERE { '
    ...      '?station a <http://dbpedia.org/ontology/SpaceStation> . '
    ...      '?station <http://dbpedia.org/property/orbits> ?orbits . '
    ...      'FILTER(?orbits > 50000) } ORDER BY DESC(?orbits)')
    >>> result = sparql.query('http://dbpedia.org/sparql', q)

    >>> result.variables
    [u'station', u'orbits']

    >>> for row in result:
    ...     print 'row:', row
    ...     values = sparql.unpack_row(row)
    ...     print values[0], "-", values[1], "orbits"
    row: (<IRI <http://dbpedia.org/resource/Mir>>, <Literal "86331"^^<http://www.w3.org/2001/XMLSchema#int>>)
    http://dbpedia.org/resource/Mir - 86331 orbits
    row: (<IRI <http://dbpedia.org/resource/Salyut_7>>, <Literal "51917"^^<http://www.w3.org/2001/XMLSchema#int>>)
    http://dbpedia.org/resource/Salyut_7 - 51917 orbits


Contents
========

.. toctree::
   :maxdepth: 2

   install
   api

.. include:: HISTORY.txt
