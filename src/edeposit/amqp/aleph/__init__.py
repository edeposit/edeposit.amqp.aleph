# This package may contain traces of nuts
from collections import namedtuple

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
                               'isbns',
                           ])):
    """
    see https://e-deposit.readthedocs.org/cs/latest/dm01.html
    """
    pass

class ISBN(namedtuple("ISBN",['ISBN',])):
    def isValid():
        return True

class Author(namedtuple("Author",['firstName','lastName'])):
    pass
