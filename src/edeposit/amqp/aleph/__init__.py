# This package may contain traces of nuts
from collections import namedtuple
from datetime import datetime

class Producent(namedtuple("Producent",['title','phone','fax','email','url','identificator','ico'])):
    pass

class EPublication(namedtuple("EPublication",
                              ['nazev',
                               'podnazev',
                               'vazba',
                               'cena',
                               'castDil',
                               'nazevCasti',
                               'nakladatelVydavatel',
                               'datumVydani',
                               'poradiVydani',
                               'zpracovatelZaznamu',
                               'kategorieProRIV',
                               'mistoDistribuce',
                               'distributor',
                               'datumDistribuce',
                               'datupProCopyright',
                               'format',
                               'url',
                               'mistoVydani',
                               'ISBNSouboruPublikaci',
                               'authori',
                               'originaly',
                           ])):
    """
    see https://e-deposit.readthedocs.org/cs/latest/dm01.html
    """
    pass

class OriginalFile(namedtuple("OriginalFile",['url','format','file','isbn'])):
    """ type of isbn: ISBN"""
    pass

class Author(namedtuple("Author",['firstName','lastName'])):
    pass

def send_to_aleph(epublication):
    pass


class AlephQuery(namedtuple("AlephQuery",
                            ['base',
                             'phrase',
                             'considerSimilar',
                             'field'])):
    """ 
    base ... base in Aleph
         NKC, ...
         see:  http://aleph.nkp.cz/F/?func=file&file_name=base-list
    
    """
    pass

class AlephRecord(namedtuple("AlephRecord",
                             ['base',
                              'docNumber',
                              'xml'])):
    pass


class AlephExportRequest(namedtuple("AlephExportRequest",
                                    ['epublication',
                                     'linkOfEPublication'])):
    """ epublication ... type of EPublication
        linkOfEPublication  ... url with epublication
    """
    pass


class AlephExportResult(namedtuple("AlephExportResult",
                                   ['docNumber',
                                    'base',
                                    'xml',
                                    'success',
                                    'message'])):
    """ docNumber ... docNumber of a record in Aleph
        base      ... base of Aleph
        success   ... whether import was successfull
        message   ... message of error or success
    """
    pass
