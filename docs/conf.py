# -*- coding: utf-8 -*-

import sys, os

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'sparql-client'
copyright = u'2011, European Environment Agency'

version = '0.7'
release = version

exclude_patterns = ['_build']
pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'sparql-clientdoc'
