#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from docs import getVersion


# Variables ===================================================================
changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    changelog
])


# Package definitions =========================================================
setup(
    name='edeposit.amqp.aleph',
    version=getVersion(changelog),
    description="E-Deposit AMQP module providing communication with Aleph",
    long_description=long_description,

    url='https://github.com/edeposit/edeposit.amqp.aleph',

    author='Edeposit team',
    author_email='edeposit@email.cz',

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='GPL2+',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    namespace_packages=[
        'edeposit',
        'edeposit.amqp'
    ],
    include_package_data=True,

    zip_safe=False,
    install_requires=[
        'setuptools',
        "pyDHTMLParser>=2.0.7",
        "httpkie>=1.1.0,<2.0.0",
        "isbn_validator",
        "remove_hairs",
        "marcxml_parser",
    ],
    extras_require={
        "test": [
            "unittest2",
            "robotsuite",
            "pytest",
            "mock",
            "robotframework-httplibrary"
        ],
        "docs": [
            "sphinxcontrib-robotdoc",
            "sphinxcontrib-napoleon",
            "sphinx",
        ]
    },
)
