Changelog
=========

1.8.3
-----
    - ISBN is now discriminated to valid and INVALID. See ``EPublication.invalid_ISBN``.

1.8.0 - 1.8.2
-------------
    - Removed old robot tests and added alternatives in pytest. More will come.
    - Added tests of conversion functions for ``EPublication`` and ``SemanticInfo``.
    - Removed ``marcxml.py`` (#45), which was moved into standalone module [marcxml_parser](https://github.com/edeposit/marcxml_parser).
    - Module refactored to work with ``marcxml.py``, which brings many improvements.
    - Implemented #46: ``convertor.py`` removed, functions moved to static methods and standalone submodule (see ``doc_number.py``).
    - Updated documentation.
    - README.rst updated.
    - Fixed small bug in MANIFEST.in.

1.7.4
-----
    - Implemented #43 - new attributes to SemanticInfo.
    - Removed ``_remove_hairs()`` function, which is now in stanalone package.
    - Added dependency to ``remove_hairs`` standalone package.

1.7.0 - 1.7.3
-------------
    - isbn.py is no longer part of the edeposit.amqp.aleph, but `standalone module <https://github.com/edeposit/isbn_validator>`_.
    - Small syntax improvements in ISBN module.
    - Improved parsing of `summaryRecordSysNumber` in SemanticInfo submodule.
    - Fixed paths in ``run_tests.sh``.
    - Added new items to ``SemanticInfo`` structure (``.isClosed``, ``.summaryRecordSysNumber``, ``.parsedSummaryRecordSysNumber``).
    - Added new query ``ICZQuery``.
    - Fixed #41 - case of deleted record with stub left after deletion.

1.6.0 - 1.6.5
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
    - Added different way of tracking SemanticInfo.hasISBNAgencyFields.
    - Fixed bug in convertor.py.
    - ``reactToAMQPMessage()`` parameters modified.

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

1.4.0 - 1.4.9
-------------
    - API change in reactToAMQPmessage(), which now takes just two parameters and returns values, instead of calling callbacks.
    - Documentation updated and made useful.
    - Documentation of export.py updated.
    - Assertions in export.py are now annotated (useful for debugging).
    - Version of package and documentation is now automatically parsed from this file.
    - Documentation of the whole package updated.
    - Fixed bugs in MARC XML parser and Aleph lowlevel API.
    - Added ``run_tests.sh``.
    - Added TitleQuery.
    - Fixed bug in export script.
    - Changelog made more compact.
    - Fixed bug #23 in _removeSpecialCharacters().
    - Fixed export bugs (see #21 and #22).
    - Fixed reported bugs in export script.
    - Fixed bug in ISBN submodule.
    - Added unicode support to settings.py.

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