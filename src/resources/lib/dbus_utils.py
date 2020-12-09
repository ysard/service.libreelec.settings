# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import asyncio
import dbussy
import ravel
import threading

LOOP = asyncio.get_event_loop()
BUS = ravel.system_bus()
BUS.attach_asyncio(LOOP)
LOOP_THREAD = threading.Thread(target=LOOP.run_forever, daemon=True).start()


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

    async def call_async_method(self, path, interface, method_name, *args, **kwargs):
        interface = await BUS[self.bus_name][path].get_async_interface(interface)
        method = getattr(interface, method_name)
        result = await method(*args, **kwargs)
        first = next(iter(result or []), None)
        return convert_from_dbussy(first)

    def call_method(self, path, interface, method_name, *args, **kwargs):
        interface = BUS[self.bus_name][path].get_interface(interface)
        method = getattr(interface, method_name)
        result = method(*args, **kwargs)
        first = next(iter(result or []), None)
        return convert_from_dbussy(first)

    def run_method(self, path, interface, method_name, *args, **kwargs):
        future = asyncio.run_coroutine_threadsafe(self.call_async_method(path, interface, method_name, *args, **kwargs), LOOP)
        return future.result()
