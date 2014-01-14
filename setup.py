from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='edeposit.amqp.aleph',
      version=version,
      description="E-Deposit AMQP module for communication with Aleph",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='https://github.com/jstavel/edeposit.amqp.aleph',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['edeposit', 'edeposit.amqp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={"test": [
          "unittest2",
          "robotsuite",
          "mock",
      ], "docs": [
          "sphinxcontrib-robotdoc",
          "sphinx",
      ]},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
