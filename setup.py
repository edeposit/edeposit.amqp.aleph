import os
import os.path
import shutil

from setuptools import setup, find_packages
from distutils.command.sdist import sdist


DOCS_GENERATED = False
version = '1.2.4'
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read()
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

            global DOCS_GENERATED
            DOCS_GENERATED = True

            os.chdir(d)

        sdist.run(self)

        if os.path.exists(DOCS_OUT):
            shutil.rmtree(DOCS_OUT)


setup(
    name='edeposit.amqp.aleph',
    version=version,
    description="E-Deposit AMQP module providing communication with Aleph",
    long_description=long_description,

    url='https://github.com/jstavel/edeposit.amqp.aleph',

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
        "pyDHTMLParser>=1.7.4,<2.0.0",
        "httpkie>=1.1.0,<2.0.0",
    ],
    extras_require={
        "test": [
            "unittest2",
            "robotsuite",
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
