Installing `sparql-client`
==========================

The `sparql-client` library is available from PyPI and has dependency on pycurl2,
which also depends on libcurl
In order to install sparql-client first you have to install libcurl, or you can
build it from the sources following the instructions from

    http://curl.haxx.se/docs/install.html

The next step is to install pycurl2:

    pip install pycurl2

The last step is to install sparql-client:

    pip install sparql-client

We recommend also instlaling `python-dateutil`, to enable parsing of dates and
times from query results.
