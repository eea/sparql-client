import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

NAME = 'sparql-client'
VERSION = open('version.txt').read().strip()


setup(name=NAME,
      version=VERSION,
      description='Python API to query a SPARQL endpoint',
      long_description=open('README.rst').read() + "\n\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 2.7",
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords="Sparql Client",
      author='European Environment Agency: IDM2 A-Team',
      author_email='eea-edw-a-team-alerts@googlegroups.com',
      long_description_content_type='text/x-rst',
      url='https://github.com/eea/sparql-client',
      license="MPL",
      py_modules=['sparql'],
      install_requires=[
          'eventlet',
          'six',
          'dnspython < 2.0.0',
      ],
      extras_require={
            'test': [
                'mock',
            ]
      },

      )
