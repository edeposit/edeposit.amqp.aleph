# This package may contain traces of nuts
from collections import namedtuple
from datetime import datetime

class Producent(namedtuple("Producent",['title','phone','fax','email','url','identificator','ico'])):
    pass

class EPublication(namedtuple("EPublication",
                              ['title',
                               'subtitle',
                               'bookBinding',
                               'price',
                               'volume',
                               'volumeTitle',
                               'volumeNumber',
                               'edition',
                               'editionNumber',
                               'subedition',
                               'subeditionNumber',
                               'placeOfPublishing',
                               'publisher',
                               'dateOfPublishing',
                               'publishedWithCoedition',
                               'publishedAtOrder',
                               'personWhoProcessedThis',
                               'librariesThatCanAccessAtLibraryTerminal',
                               'librariesThatCanAccessAtPublic',
                               'alephDocNumber',
                               'generateISBN',
                               'categoryForRIV',
                               'placeOfDistribution',
                               'distributor',
                               'dateOfDistribution',
                               'producer',
                               'dateOfProduction',
                               'dateOfCopyright',
                               'development',
                               'mediaType',
                               'authors',
                               'originalFiles',
                           ])):
    """
    see https://e-deposit.readthedocs.org/cs/latest/dm01.html
    """
    pass

class OriginalFile(namedtuple("OriginalFile",['url','format','file','isbns'])):
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
