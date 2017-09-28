# -*- coding: utf-8 -*-

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'sparql-client'
copyright = u'2011, European Environment Agency'

from sparql import __version__ as version
release = version

exclude_patterns = ['_build']
pygments_style = 'sphinx'
intersphinx_mapping = {'python': ('http://docs.python.org', None)}

html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'sparql-clientdoc'
