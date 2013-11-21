**************************
SPARQL HTTP client library
**************************

`sparql-client` is a library to query a SPARQL endpoint. It will automatically
convert literals to the coresponding Python types.

Visit http://www.eionet.europa.eu/software/sparql-client/ for documentation and
examples.


API
---

First you open a connection to the endpoint::

    s = sparql.Service(endpoint, "utf-8", "GET")

Then you make the query::

    result = s.query(statement)

If you have made a SELECT query, then you can read the result with fetchone() or fetchall()::

    for row in result.fetchone():

If you have made an ASK query, then you can read the result (a boolean value) with hasresult():

    works = result.hasresult()


Conversion of data types
------------------------

The library will automatically convert typed literals to a coresponding
simple type in Python. Dates are also converted if the dateutil_ library is
available.

.. _dateutil: http://labix.org/python-dateutil


Running the unit tests
----------------------

If you have nose_ installed, just run ``nosetests`` in the top-level directory.
Some tests require the python-dateutil_ (version 1.5) or mock_ libraries.
Tested under Python 2.4 through 2.7.

.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
.. _python-dateutil: http://niemeyer.net/python-dateutil
.. _mock: http://www.voidspace.org.uk/python/mock/


License
-------
The contents of this package are subject to the Mozilla Public
License Version 1.1 (the "License"); you may not use this package
except in compliance with the License. You may obtain a copy of
the License at http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS
IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
implied. See the License for the specific language governing
rights and limitations under the License.

The Original Code is SPARQL client version 1.0.

The Initial Owner of the Original Code is European Environment
Agency (EEA). Portions created by Eau de Web for EEA are
Copyright (C) European Environment Agency. All Rights Reserved.


Authors
-------
* Søren Roug, EEA
* Alex Morega, Eau de Web
