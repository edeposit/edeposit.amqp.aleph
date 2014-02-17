# -*- coding: utf-8 -*-
import edeposit.amqp.aleph
from edeposit.amqp.aleph.settings import *

producent = edeposit.amqp.aleph.Producent(
    title='Návrat',
    phone=None,
    fax=None,
    email=None,
    url=None,
    identificator=None,
    ico=None
)

author = edeposit.amqp.aleph.Author(
    firstName="Karel",
    lastName="May",
    title=""
)

originalFile = edeposit.amqp.aleph.OriginalFile(
    url="",
    file=None,
    format=None,
    isbns=[]
)

epublication = edeposit.amqp.aleph.EPublication(
    nazev='Ardistan a Džinistan',
    podnazev='Karel May ; [ilustroval Josef Pospíchal ; z němčiny přeložil Vladimír Šunda]',
    vazba='',
    cena='CZK 182,00',
    castDil='',
    nazevCasti='díl 1.',
    nakladatelVydavatel="",
    datumVydani='1998',
    poradiVydani='',
    zpracovatelZaznamu='',
    kategorieProRIV='',
    mistoDistribuce='',
    distributor="",
    datumDistribuce="",
    datumProCopyright='',
    format='',
    url='',
    mistoVydani='',
    ISBNSouboruPublikaci='',
    autori=[author],
    originaly=[]
    # librariesThatCanAccessAtLibraryTerminal=[],
    # librariesThatCanAccessAtPublic=[],
    # alephDocNumber='',
    # generateISBN='',
)

search_request = edeposit.amqp.aleph.AlephSearchQuery(
    base="nkc",
    phrase="test",
    considerSimilar=False,
    field="wrd"
)

count_request = edeposit.amqp.aleph.AlephCount(
    base="nkc",
    phrase="test",
    considerSimilar=False,
    field="wrd"
)

linkOfEPublication = "http://localhost/epublication-01/"

exportRequest = edeposit.amqp.aleph.AlephExportRequest(
    epublication=epublication,
    linkOfEPublication=linkOfEPublication,
)


"""
it is important to fill those three variables with results that are sent in
RabbitMQ
"""
amqp_data = None
amqp_properties = None
amqp_headers = None
