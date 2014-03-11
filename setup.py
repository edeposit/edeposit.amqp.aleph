from setuptools import setup, find_packages


version = '1.2.1'
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.txt').read(),
    open('CHANGES.txt').read()
])


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
    }
)
