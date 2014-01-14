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

class ISBN(namedtuple("ISBN",['ISBN',])):
    def isValid():
        return True

class Author(namedtuple("Author",['firstName','lastName'])):
    pass

def send_to_aleph(epublication):
    pass
