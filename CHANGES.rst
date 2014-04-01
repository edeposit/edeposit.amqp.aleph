Changelog
=========


1.4.3
-----
    - Documentation of export.py updated.

1.4.2
-----
    - Assertions in export.py are now annotated (useful for debugging).

1.4.1
-----
    - Version of package and documentation is now automatically parsed from this file.

1.4.0
-----
    - API change in reactToAMQPmessage(), which now takes just two parameters and returns values, instead of calling callbacks.
    - Documentation updated and made useful.

1.3.0
-----
    - Serializers removed from convertors.py. (De)serialization will be handled in edeposit.amqp, because other packages also uses it.

1.2.5
-----
    - Fixed bug with package installation, when the package couldn't find README.rst.

1.2.4
-----
    - Documentation is now even for settings.py's attributes.
    - User defined JSON configuration is now supported.

1.2.3
-----
    - Documentation is now generated automatically everytime the package is generated.

1.2.2
-----
    - Tests and HTML help is now included in PYPI package.

1.2.1
-----
    - All source files are now documented with google style docstrings.


1.2.0
-----
    - Added experimental export support.

1.1.0
-----
    - Project released at PYPI.

1.0 (unreleased)
----------------
    - Communication with Aleph is now working.

0.1-dev (unreleased)
--------------------
    - Package created using templer.