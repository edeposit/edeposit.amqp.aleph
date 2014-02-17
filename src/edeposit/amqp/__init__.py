from collections import namedtuple

class AMQPMessage(namedtuple('AMQPMessage',
                             ['data',
                              'headers',
                              'properties'
                              ])):
    """
    data ... serialized main message
    headers
    """
    pass



