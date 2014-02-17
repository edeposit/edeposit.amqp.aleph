#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from string import Template


import pika


from __init__ import AlephSearchQuery
import settings

import aleph
from convertors import toJSON, fromJSON


#= Variables ==================================================================
SERVER_TEMPLATE = "amqp://$USERNAME:$PASSWORD@$SERVER:$PORT/%2f" # %2f is required


#= Functions & objects ========================================================
def _genRandomID():
    pass


def _sendRequest(serialized_data, exchange):
    pass


def _sendResponse(serialized_data, exchange):
    pass


def genericAlephSearch(base, phrase, considerSimilar, field):
    query = AlephSearchQuery(
        base=base,
        phrase=phrase,
        considerSimilar=considerSimilar,
        field=field,
        uuid=_genRandomID()
    )

    _sendRequest(
        toJSON(query),
        settings.INPUT_EXCHANGE_FOR_ALEPH_SEARCH
    )

    return query.uuid


def sendISBNCountRequest(isbn):
    pass


def sendAuthorsBooksCountRequest(author):
    pass


def sendPublishersBooksCountRequest(publisher):
    pass


#= Main program ===============================================================
if __name__ == '__main__':
    # connection = pika.BlockingConnection(
    #     pika.URLParameters(
    #         Template(SERVER_TEMPLATE).substitute(
    #             USERNAME=settings.RABBITMQ_USER_NAME,
    #             PASSWORD=settings.RABBITMQ_USER_PASSWORD,
    #             SERVER=settings.RABBITMQ_HOST,
    #             PORT=settings.RABBITMQ_PORT
    #         )
    #     )
    # )
