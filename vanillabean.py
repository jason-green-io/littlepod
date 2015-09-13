#!/usr/bin/env python

import sys
sys.path.append('/minecraft')
import rcon


def send(command):
    host, port, password = ("127.0.0.1", 25575, "babybee")
    print u"Server >> " + repr(command)
    client = rcon.client(host, port, password)
    response = client.send(command.encode('utf-8'))

    client.disconnect()

    print u"Server << " +repr( response)
    return response


if __name__ == "__main__":
    send(sys.argv[1])
