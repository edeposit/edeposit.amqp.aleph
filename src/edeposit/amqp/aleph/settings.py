# -*- coding: utf-8 -*-
import os.path


BASE_PATH = (os.path.dirname(__file__))

ALEPH_URL = "http://aleph.nkp.cz"
PATH_OF_EXPORT_DIRECTORY = os.path.join(BASE_PATH, "tests", "var", "export")

INPUT_EXCHANGE_FOR_ALEPH_SEARCH = "aleph-search" # TODO: sync with project

# TODO: remove, for test purposes only
# https://raw.github.com/jstavel/edeposit.amqp/master/edeposit/amqp/settings.py
RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_PORT = '5672'
RABBITMQ_USER_NAME = 'guest'
RABBITMQ_USER_PASSWORD = 'guest'
