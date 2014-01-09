# This package may contain traces of nuts
from collections import namedtuple

class Result(namedtuple("Result",['valid','producent','publication'])):
    """
    valid: [True | False]
    producent: type Producent
    publication: type Publication
    """
    pass

class Producent(namedtuple("Producent",['title','phone','fax','email','url','identificator','ico'])):
    pass

class Publication(namedtuple("Publication",['stream',])):
    """
    stream: string v MARCXML xml format
    """
    pass

def process_isbn(isbn):
    return Result(valid=None, 
                  producent=None,
                  publication=Publication(stream=""))

def producent_info(result):
    return result.producent

def publication_info(result):
    return result.publication
