# -*- coding: utf-8 -*-
from datetime import date
import edeposit.amqp.aleph
from edeposit.amqp.aleph.settings import *

producent = edeposit.amqp.aleph.Producent (
    title='Návrat',
    phone=None,
    fax=None,
    email=None,
    url=None,
    identificator=None,
    ico=None
)

author = edeposit.amqp.aleph.Author (
    firstName="Karel",
    lastName="May"
)

originalFile = edeposit.amqp.aleph.OriginalFile (
    isbns = [],
    url = "",
    file = None,
    format = None
)

epublication = edeposit.amqp.aleph.EPublication(
    title='Ardistan a Džinistan',
    subtitle='Karel May ; [ilustroval Josef Pospíchal ; z němčiny přeložil Vladimír Šunda]',
    bookBinding='',
    price='CZK 182,00',
    volume='',
    volumeTitle='díl 1.',
    volumeNumber='1',
    edition='Souborné vydání díla Karla Maye',
    editionNumber='110,111',
    subedition='',
    subeditionNumber='',
    placeOfPublishing='',
    publisher='',
    dateOfPublishing='1998',
    publishedWithCoedition='',
    publishedAtOrder='',
    personWhoProcessedThis='',
    librariesThatCanAccessAtLibraryTerminal=[],
    librariesThatCanAccessAtPublic=[],
    alephDocNumber='',
    generateISBN='',
    categoryForRIV='',
    placeOfDistribution='',
    distributor='',
    dateOfDistribution='',
    producer=None,
    dateOfProduction='',
    dateOfCopyright='',
    development='',
    mediaType='',
    authors=[author],
    originalFiles=[],
)

linkOfEPublication = "http://localhost/epublication-01/"

exportRequest = edeposit.amqp.aleph.AlephExportRequest(
    epublication = epublication,
    linkOfEPublication = linkOfEPublication,
)


""" it is important to fill those three variables with results that are sent in RabbitMQ """
amqp_data = None
amqp_properties = None
amqp_headers = None
