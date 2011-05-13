#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Original Code is SPARQL client version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Søren Roug, EEA

import platform
from distutils.core import setup

version = '0.5'

setup(name='sparqlclient',
      version=version,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      description='Python API to query a SPARQL endpoint',
      long_description = (
"""
PySparqlClient is a library to query a SPARQL endpoint.
It will automatically convert literals to the coresponding Python types.

Visit http://www.eionet.europa.eu/software/pysparql for documentation and examples."""
),
      author='Soren Roug',
      author_email='soren.roug@eea.europa.eu',
      url='http://www.eionet.europa.eu/software/pysparql',
      py_modules =['sparqlclient'],
      )
