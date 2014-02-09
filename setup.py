from strings import Template
from setuptools import setup, find_packages

version = '0.1'
long_description = """$README

Contributors
============
$CONTRIBUTORS

Changes
=======
$CHANGES
"""


setup(
    name='edeposit.amqp.aleph',
    version=version,
    description="E-Deposit AMQP module for communication with Aleph",
    long_description=Template(long_description).substitute(
        README=open('README.txt').read(),
        CONTRIBUTORS=open('CONTRIBUTORS.txt').read(),
        CHANGES=open('CHANGES.txt').read()
    ),

    url='https://github.com/jstavel/edeposit.amqp.aleph',

    author='',
    author_email='',

    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='',
    license='gpl',

    packages=find_packages('src'),
    package_dir = {'': 'src'},

    namespace_packages=[
        'edeposit',
        'edeposit.amqp'
    ],
    include_package_data=True,

    zip_safe=False,
    install_requires=['setuptools'],
    extras_require={
        "test": [
            "unittest2",
            "robotsuite",
            "mock",
        ],
        "docs": [
            "sphinxcontrib-robotdoc",
            "sphinx",
        ]
    },
    # entry_points="""
    # # -*- Entry points: -*-
    # """,
)
