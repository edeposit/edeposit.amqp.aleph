Changelog
=========

1.5.1
-----
    - Added new Query class - DocumentQuery.
    - Documentation cleaned.
    - Added documentation for convertor.
    - Fixed bug in unittests.

1.5.0
-----
    - Queries to test base are now handled by OAI API, which has access.
    - Export is working.

1.4.9
-----
    - Fixed bug in export script.
    - Changelog made more compact.

1.4.5 - 1.4.8
-------------
    - Fixed bug #23 in _removeSpecialCharacters().
    - Fixed export bugs (see #21 and #22).
    - Fixed reported bugs in export script.
    - Fixed bug in ISBN submodule.
    - Added unicode support to settings.py.

1.4.4
-----
    - Documentation of the whole package updated.
    - Fixed bugs in MARC XML parser and Aleph lowlevel API.
    - Added ``run_tests.sh``.
    - Added TitleQuery.

1.4.1 - 1.4.3
-------------
    - Documentation of export.py updated.
    - Assertions in export.py are now annotated (useful for debugging).
    - Version of package and documentation is now automatically parsed from this file.

1.4.0
-----
    - API change in reactToAMQPmessage(), which now takes just two parameters and returns values, instead of calling callbacks.
    - Documentation updated and made useful.

1.3.0
-----
    - Serializers removed from convertors.py. (De)serialization will be handled in edeposit.amqp, because other packages also uses it.

1.2.0 - 1.2.5
-------------
    - Fixed bug with package installation, when the package couldn't find README.rst.
    - User defined JSON configuration is now supported.
    - Documentation is now even for settings.py's attributes.
    - Documentation is now generated automatically everytime the package is generated.
    - Tests and HTML help is now included in PYPI package.
    - All source files are now documented with google style docstrings.
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