from distutils.core import setup

from sparql import __version__ as version

setup(name='sparql-client',
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
      long_description=open('README').read(),
      author='Soren Roug',
      author_email='soren.roug@eea.europa.eu',
      url='http://www.eionet.europa.eu/software/sparql-client',
      py_modules =['sparql'],
      )
