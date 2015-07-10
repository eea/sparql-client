Installing `sparql-client`
==========================

The `sparql-client` library is available from PyPI and has dependency on pycurl,
which also depends on libcurl
In order to install sparql-client first you have to install libcurl >= 7.19.0, or you can
build it from the sources following the instructions from

    http://curl.haxx.se/docs/install.html

The next step is to install pycurl:

    pip install pycurl

The last step is to install sparql-client:

    pip install sparql-client

We recommend also instlaling `python-dateutil`, to enable parsing of dates and
times from query results.
