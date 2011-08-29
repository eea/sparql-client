:mod:`sparql` module
====================

.. automodule:: sparql


RDF wrapper classes
-------------------

.. autoclass:: sparql.RDFTerm
    :members:

.. autoclass:: sparql.IRI

.. autoclass:: sparql.Literal

.. autoclass:: sparql.BlankNode


Query utilities
---------------

.. autoclass:: Service

.. autoclass:: _ResultsParser
    :members:

    .. automethod:: __iter__

.. autofunction:: sparql.parse_n3_term

.. autofunction:: unpack_row

.. autofunction:: query
