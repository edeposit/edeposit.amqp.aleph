#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is used to put data to Aleph. It is based on custom made webform,
which is currently used to report new books by publishers.

Most important function from this module is :func:`exportEPublication`,
which will do everything, that is needed to do, to export
:class:`.EPublication` structure to the Aleph.

Warning:
    This whole module is highly dependent on processes, which are defined as
    import processes at the Czech National Library.

Warning:
    If you want to use export ability in your library, you should rewrite this
    and take care, that you are sending data somewhere, where someone will
    process them. Otherwise, you can fill your library's database with crap.

Note:
    Source code of the webform is not available at this moment (it was created
    by third party), but it is possible, that it will be in future. This will
    highly depend on number of people, which will use this project.
"""
# Imports =====================================================================
import isbn_validator
from httpkie import Downloader

import settings
from datastructures import Author
from datastructures import FormatEnum
from datastructures import EPublication


# Variables ===================================================================
ANNOTATION_PREFIX = "Nakladatelská anotace: "


# Functions & objects =========================================================
class ExportException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidISBNException(ExportException):
    def __init__(self, message):
        super(InvalidISBNException, self).__init__(message)


class ExportRejectedException(ExportException):
    def __init__(self, message):
        super(ExportRejectedException, self).__init__(message)


class PostData(object):
    """
    This class is used to transform data from
    :class:`.EPublication` to dictionary, which is sent as POST request to
    Aleph third-party webform_.

    .. _webform: http://aleph.nkp.cz/F/?func=file&file_name=service-isbn

    Note:
        Class is used instead of simple function, because there is 29 POST
        parameters with internal dependencies, which need to be processed and
        validated before they can be passed to webform.

    Args:
        epub (EPublication): structure, which will be converted (see
                             :class:`.EPublication` for details).

    Attr:
        _POST (dict):   dictionary with parsed data
        mapping (dict): dictionary with some of mapping, which are applied to
                        :attr:`._POST` dict in post processing

    Warning:
        Don't manipulate :attr:`._POST` property directly, if you didn't really
        know the internal structure and how the :attr:`.mapping` is applied.
    """
    def __init__(self, epub):
        self._POST = {
            "sid": settings.EDEPOSIT_EXPORT_SIGNATURE,
            "P0100LDR__": "-----nam-a22------a-4500",
            "P0200FMT__": "BK",
            "P0300BAS__a": "30",  # Báze, pro eknihy 49
            "P0501010__a": "",    # ISBN (uppercase)
            "P0502010__b": "online",  # vazba/forma
            "P0504010__d": "",    # cena
            # "P1201901__b": "",    # ean
            "P0601010__a": "",    # ISBN souboru
            "P0602010__b": "",    # same thing
            "P07012001_a": "",    # název
            "P07022001_b": "",    # vyplneno na zaklade vazby/formy
            "P07032001_e": "",    # podnázev
            "P07042001_h": "",    # Část (svazek, díl)
            "P07052001_i": "",    # Název části
            "P1301ZAK__b": "",    # autor
            "P1302ZAK__c": "",    # autor2
            "P1303ZAK__c": "",    # autor3
            # "P10012252_a": "",    # edice
            # "P10022252_v": "",    # Číslo svazku
            "P110185640u": "",    # URL
            "P0503010__x": "",    # Formát (poze pro epublikace)
            "P0901210__a": "",    # Místo vydání
            "P0902210__c": "",    # Nakladatel
            "P0903210__d": "",    # Měsíc a rok vydání
            "P1401PJM__a": "",    # Vydáno v koedici s
            "P0801205__a": "",    # Pořadí vydání
            "P1501IST1_a": "ow",  # Zpracovatel záznamu (hidden)
            "P1502IST1_b": "",    # Zpracovatel záznamu (viditelna)
            "P1601ISB__a": "",    # ISBN2 - validated (hidden)
            "P1801URL__u": "",    # internal URL
            # "REPEAT": "Y",        # predvyplnit zaznam
            "P1001330__a": "",    # anotace
        }

        self.mapping = {
            "mapa": [
                "-----nem-a22------a-4500",
                "MP",
                "30",
                "kartografický dokument",
                "ow"
            ],
            "CD-ROM": [
                "-----nam-a22------a-4500",
                "BK",
                "30",
                "elektronický zdroj",
                "ow"
            ],
            "online": [
                "-----nam-a22------a-4500",
                "BK",
                "49",
                "elektronický zdroj",
                "ox",
            ],
            # "else": [
            #     "-----nam-a22------a-4500",
            #     "BK",
            #     "30",
            #     "",
            #     "ow"
            # ],
            "else": [
                "-----nam-a22------a-4500",
                "BK",
                "49",
                "elektronický zdroj",
                "ox",
            ]
        }
        self.mapping["DVD"] = self.mapping["CD-ROM"]

        self._import_epublication(epub)

    def _import_epublication(self, epub):
        """
        Fill internal property ._POST dictionary with data from EPublication.
        """
        # mrs. Svobodová requires that annotation exported by us have this
        # prefix
        prefixed_annotation = ANNOTATION_PREFIX + epub.anotace

        self._POST["P0501010__a"] = epub.ISBN
        self._POST["P07012001_a"] = epub.nazev
        self._POST["P07032001_e"] = epub.podnazev
        self._POST["P0502010__b"] = epub.vazba
        self._POST["P0504010__d"] = epub.cena
        self._POST["P07042001_h"] = epub.castDil
        self._POST["P07052001_i"] = epub.nazevCasti
        self._POST["P0902210__c"] = epub.nakladatelVydavatel
        self._POST["P0903210__d"] = epub.datumVydani
        self._POST["P0801205__a"] = epub.poradiVydani
        self._POST["P1502IST1_b"] = epub.zpracovatelZaznamu
        self._POST["P0503010__x"] = epub.format
        self._POST["P110185640u"] = epub.url or ""
        self._POST["P0901210__a"] = epub.mistoVydani
        self._POST["P0601010__a"] = epub.ISBNSouboruPublikaci
        self._POST["P1801URL__u"] = epub.internal_url
        self._POST["P1001330__a"] = prefixed_annotation if epub.anotace else ""

        if len(epub.autori) > 3:
            epub.autori[2] = ", ".join(epub.autori[2:])
            epub.autori = epub.autori[:3]

        # check whether the autors have required type (string)
        for author in epub.autori:
            error_msg = "Bad type of author (%s) (str is required)."
            assert isinstance(author, basestring), (error_msg % type(author))

        authors_fields = ("P1301ZAK__b", "P1302ZAK__c", "P1303ZAK__c")
        self._POST.update(dict(zip(authors_fields, epub.autori)))

    def _apply_mapping(self, mapping):
        """
        Map some case specific data to the fields in internal dictionary.
        """
        self._POST["P0100LDR__"] = mapping[0]
        self._POST["P0200FMT__"] = mapping[1]
        self._POST["P0300BAS__a"] = mapping[2]
        self._POST["P07022001_b"] = mapping[3]
        self._POST["P1501IST1_a"] = mapping[4]

    def _validate_isbn(self, raw_isbn, accept_blank=False):
        if raw_isbn and type(raw_isbn) in [tuple, list]:
            raw_isbn = raw_isbn[0]

        # blank list -> blank str
        raw_isbn = raw_isbn or ""

        if not raw_isbn and accept_blank:
            return raw_isbn

        if not isbn_validator.is_valid_isbn(raw_isbn):
            raise InvalidISBNException(
                raw_isbn + " has invalid ISBN checksum!"
            )

        return raw_isbn.upper()

    def _postprocess(self):
        """
        Move data between internal fields, validate them and make sure, that
        everything is as it should be.
        """
        # validate series ISBN
        self._POST["P0601010__a"] = self._validate_isbn(
            self._POST["P0601010__a"],
            accept_blank=True
        )
        if self._POST["P0601010__a"] != "":
            self._POST["P0601010__b"] = "soubor : " + self._POST["P0601010__a"]

        # validate ISBN of the book
        self._POST["P0501010__a"] = self._validate_isbn(
            self._POST["P0501010__a"],
            accept_blank=False
        )
        self._POST["P1601ISB__a"] = self._POST["P0501010__a"]

    @staticmethod
    def _czech_isbn_check(isbn_field):
        isbn_field = isbn_field.replace("-", "").strip()

        return any([
            isbn_field.startswith("80"),
            isbn_field.startswith("97880"),
        ])

    def _check_required_fields(self):
        """
        Make sure, that internal dictionary contains all fields, which are
        required by the webform.
        """
        assert self._POST["P0501010__a"] != "", "ISBN is required!"

        # export script accepts only czech ISBNs
        for isbn_field_name in ("P0501010__a", "P1601ISB__a"):
            check = PostData._czech_isbn_check(self._POST[isbn_field_name])
            assert check, "Only czech ISBN is accepted!"

        assert self._POST["P1601ISB__a"] != "", "Hidden ISBN field is required!"

        assert self._POST["P07012001_a"] != "", "Nazev is required!"
        assert self._POST["P0901210__a"] != "", "Místo vydání is required!"

        assert self._POST["P0903210__d"] != "", "Datum vydání is required!"
        assert self._POST["P0801205__a"] != "", "Pořadí vydání is required!"

        # Zpracovatel záznamu
        assert self._POST["P1501IST1_a"] != "", "Zpracovatel is required! (H)"
        assert self._POST["P1502IST1_b"] != "", "Zpracovatel is required! (V)"

        # vazba/forma
        assert self._POST["P0502010__b"] != "", "Vazba/forma is required!"

        # assert self._POST["P110185640u"] != "", "URL is required!"

        # Formát (pouze pro epublikace)
        if self._POST["P0502010__b"] == FormatEnum.ONLINE:
            assert self._POST["P0503010__x"] != "", "Format is required!"

        assert self._POST["P0902210__c"] != "", "Nakladatel is required!"

        def to_unicode(inp):
            try:
                return unicode(inp)
            except UnicodeDecodeError:
                return unicode(inp, "utf-8")

        # check lenght of annotation field - try to convert string to unicode,
        # to count characters, not combination bytes
        annotation_length = len(to_unicode(self._POST["P1001330__a"]))
        annotation_length -= len(to_unicode(ANNOTATION_PREFIX))
        assert annotation_length <= 500, "Annotation is too long (> 500)."

    def get_POST_data(self):
        """
        Returns:
            dict: POST data, which can be sent to webform using \
                  :py:mod:`urllib` or similar library
        """
        self._postprocess()

        # some fields need to be remapped (depends on type of media)
        self._apply_mapping(
            self.mapping.get(self._POST["P0502010__b"], self.mapping["else"])
        )

        self._check_required_fields()

        return self._POST


def _sendPostDict(post_dict):
    """
    Send `post_dict` to the :attr:`.ALEPH_EXPORT_URL`.

    Args:
        post_dict (dict): dictionary from :class:`PostData.get_POST_data()`

    Returns:
        str: Reponse from webform.
    """
    downer = Downloader()
    downer.headers["Referer"] = settings.EDEPOSIT_EXPORT_REFERER
    data = downer.download(settings.ALEPH_EXPORT_URL, post=post_dict)
    rheaders = downer.response_headers

    error_msg = rheaders.get("aleph-info", "").lower().strip()
    if "aleph-info" in rheaders and error_msg.startswith("error"):
        raise ExportRejectedException(
            "Export request was rejected by import webform: %s" %
            rheaders["aleph-info"]
        )

    return data


def _removeSpecialCharacters(epub):
    """
    Remove most of the unnecessary interpunction from epublication, which can
    break unimark if not used properly.
    """
    special_chars = "/:,- "

    epub_dict = epub._asdict()

    for key in epub_dict.keys():
        if isinstance(epub_dict[key], basestring):
            epub_dict[key] = epub_dict[key].strip(special_chars)

        elif type(epub_dict[key]) in [tuple, list]:
            out = []
            for item in epub_dict[key]:
                if not isinstance(item, Author):
                    out.append(item)
                    continue

                new_item = item._asdict()

                for key in new_item.keys():
                    new_item[key] = new_item[key].strip(special_chars)

                out.append(Author(**new_item))

            epub_dict[key] = out

    return EPublication(**epub_dict)


def exportEPublication(epub):
    """
    Send `epub` :class:`.EPublication` object to Aleph, where it will be
    processed by librarians.

    Args:
        epub (EPublication): structure for export

    Warning:
        The export function is expecting some of the EPublication properties to
        be filled with non-blank data.

        Specifically:

        - :attr:`.EPublication.ISBN`
        - :attr:`.EPublication.nazev`
        - :attr:`.EPublication.mistoVydani`
        - :attr:`.EPublication.datumVydani`
        - :attr:`.EPublication.poradiVydani`
        - :attr:`.EPublication.zpracovatelZaznamu`
        - :attr:`.EPublication.vazba`
        - :attr:`.EPublication.format`
        - :attr:`.EPublication.format`
        - :attr:`.EPublication.nakladatelVydavatel`
    """
    epub = _removeSpecialCharacters(epub)
    post_dict = PostData(epub).get_POST_data()
    return _sendPostDict(post_dict)
