#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import shutil

from setuptools import setup, find_packages
from distutils.command.sdist import sdist

try:
    from docs import getVersion
except ImportError:  # during packaging, docs are moved to html_docs
    from html_docs import getVersion


changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    changelog
])


class BuildSphinx(sdist):
    """
    Generates sphinx documentation, puts it into html_docs/, packs it to
    package and removes unused directory.
    """
    def run(self):
        d = os.path.abspath('.')
        DOCS = d + "/" + "docs"
        DOCS_IN = DOCS + "/_build/html"
        DOCS_OUT = d + "/html_docs"

        if not self.dry_run:
            print "Generating the documentation .."

            os.chdir(DOCS)
            os.system("make clean")
            os.system("make html")

            if os.path.exists(DOCS_OUT):
                shutil.rmtree(DOCS_OUT)

            shutil.copytree(DOCS_IN, DOCS_OUT)
            shutil.copy(DOCS + "/__init__.py", DOCS_OUT)  # for getVersion()
            os.chdir(d)

        sdist.run(self)

        if os.path.exists(DOCS_OUT):
            shutil.rmtree(DOCS_OUT)


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
    cmdclass={'sdist': BuildSphinx}
)
