# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import asyncio
import dbussy
import config
import threading
import ravel

'''
BUS = ravel.system_bus()
_LOOP = asyncio.get_event_loop()
BUS.attach_asyncio(_LOOP)
threading.Thread(target=_LOOP.run_forever, daemon=True).start()
'''
BUS = config.BUS


def convert_from_dbussy(data):
    if isinstance(data, bool):
        return Bool(data)
    if isinstance(data, dict):
        return {key: convert_from_dbussy(data[key]) for key in data.keys()}
    if isinstance(data, list):
        return [convert_from_dbussy(item) for item in data]
    if isinstance(data, tuple) and isinstance(data[0], dbussy.DBUS.Signature):
        return convert_from_dbussy(data[1])
    return data


class Bool(int):

    def __new__(cls, value):
        return int.__new__(cls, bool(value))

    def __str__(self):
        return '1' if self == True else '0'


class Dbus(object):

    def __init__(self, bus_name):
        self.bus_name = bus_name

    def call_method(self, path, interface, method_name, *args, **kwargs):
        dbus_interface = BUS[self.bus_name][path].get_interface(interface)
        method = getattr(dbus_interface, method_name)
        result = convert_from_dbussy(method(*args, **kwargs))
        return next(iter(result or []), None)

    def get_signature(self, signature):
        return dbussy.parse_signature(signature)
