#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from string import Template


import pika


import aleph
import settings
import convertors


#= Variables ==================================================================
SERVER_TEMPLATE = "amqp://$USERNAME:$PASSWORD@$SERVER:$PORT/%2f" # %2f is required


#= Functions & objects ========================================================
def _genRandomID():
    pass


def _serialize(structure):
    pass


def _sendRequest(serialized_data, exchange):
    pass


def _sendResponse(serialized_data, exchange):
    pass


def getISBNCount(isbn):
    pass


def getAuthorsBooksCount(author):
    pass


def getPublishersBooksCount(publisher):
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

    data = open("tests/resources/aleph_data_examples/aleph_sources/example.xml").read()

    epub = convertors.toEPublication(data)

    json_data = convertors.toJSON(epub)

    print json_data

    print
    print

    print convertors.fromJSON(json_data)
