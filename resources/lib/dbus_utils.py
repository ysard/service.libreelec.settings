# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import asyncio
import dbussy
import ravel
import threading


class LoopThread(threading.Thread):

    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.is_stopped = False

    async def wait(self):
        while not self.is_stopped:
            await asyncio.sleep(1)

    def run(self):
        self.loop.run_until_complete(self.wait())
        self.loop.close()

    def stop(self):
        self.is_stopped = True
        self.join()


LOOP = asyncio.get_event_loop()
BUS = ravel.system_bus()
BUS.attach_asyncio(LOOP)
LOOP_THREAD = LoopThread(LOOP)


class Bool(int):

    def __new__(cls, value):
        return int.__new__(cls, bool(value))

    def __str__(self):
        return '1' if self == True else '0'


def list_names():
    return BUS[dbussy.DBUS.SERVICE_DBUS]['/'].get_interface(dbussy.DBUS.INTERFACE_DBUS).ListNames()[0]


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


def call_method(bus_name, path, interface, method_name, *args, **kwargs):
    interface = BUS[bus_name][path].get_interface(interface)
    method = getattr(interface, method_name)
    result = method(*args, **kwargs)
    first = next(iter(result or []), None)
    return convert_from_dbussy(first)


async def call_async_method(bus_name, path, interface, method_name, *args, **kwargs):
    interface = await BUS[bus_name][path].get_async_interface(interface)
    method = getattr(interface, method_name)
    result = await method(*args, **kwargs)
    first = next(iter(result or []), None)
    return convert_from_dbussy(first)


def run_method(bus_name, path, interface, method_name, *args, **kwargs):
    future = asyncio.run_coroutine_threadsafe(call_async_method(
        bus_name, path, interface, method_name, *args, **kwargs), LOOP)
    return future.result()
