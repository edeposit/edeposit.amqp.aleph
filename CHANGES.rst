Changelog
=========

1.6.4
-----
    - Fixed bug in convertor.py.

1.6.3
-----
    - Added different way of tracking SemanticInfo.hasISBNAgencyFields.

1.6.0 - 1.6.2
-------------
    - Added new fields to SemanticInfo structure.
    - Fixed few bugs in aleph.py.
    - Fixed bugs, old code, small improvements.
    - aleph.py: Added new function downloadRecords().
    - aleph.py: Added four new functions: getISBNsXML(), getAuthorsBooksXML(), getPublishersBooksXML() and getBooksTitleIDs().
    - aleph.py: Refactored few unnecessarily long variables.
    - convertor.py: Added new function getDocNumber().
    - __init__.py switched to use aleph.downloadRecord().
    - Fixed #27 - parsing of internal url field.
    - convertor.py refactored slightly, fixed few little bugs.

1.5.0 - 1.5.9
-------------
    - Fixed bug in marcxml.py.
    - Added more detections to convertor.py / toSemanticInfo().
    - marcxml.py changed and fixed. It can now convert MARC XML <-> OAI without any problems, just by changing .oai_marc property.
    - Fixed bug in ISBN submodule.
    - Added detection of ``ISBNQuery`` in ``ISBNValidationRequest``.
    - Updated setup.py to new version of dhtmlparser.
    - Fixed bug in deserialization of semanticinfo.
    - Added tracking of export progress.
    - Added new Query class - DocumentQuery.
    - Documentation cleaned.
    - Added documentation for convertor.
    - Fixed bug in unittests.
    - Queries to test base are now handled by OAI API, which has access.
    - Export is working.

1.4.5 - 1.4.9
-------------
    - Fixed bug in export script.
    - Changelog made more compact.
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