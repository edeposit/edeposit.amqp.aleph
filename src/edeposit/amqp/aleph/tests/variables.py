# -*- coding: utf-8 -*-
import edeposit.amqp.aleph

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
    lastName="May"
)

isbn = edeposit.amqp.aleph.ISBN(
    ISBN="80-7174-091-8"
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
    isbns=[isbn],
)
