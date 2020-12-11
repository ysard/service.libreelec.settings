# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import dbus_utils
import dbussy
import ravel

BUS_NAME = 'net.connman'
ERROR_AGENT_CANCELLED = 'net.connman.Agent.Error.Canceled'
INTERFACE_AGENT = 'net.connman.Agent'
INTERFACE_CLOCK = 'net.connman.Clock'
INTERFACE_MANAGER = 'net.connman.Manager'
INTERFACE_SERVICE = 'net.connman.Service'
INTERFACE_TECHNOLOGY = 'net.connman.Technology'
PATH_TECH_ETHERNET = '/net/connman/technology/ethernet'
PATH_TECH_WIFI = '/net/connman/technology/wifi'
PATH_AGENT = '/kodi/agent'


@ravel.interface(ravel.INTERFACE.SERVER, name=INTERFACE_AGENT)
class Agent(object):

    agent = None

    @classmethod
    def register_agent(cls):
        if cls.agent is not None:
            raise RuntimeError('An agent is already registered')
        cls.agent = cls()
        dbus_utils.BUS.request_name(
            BUS_NAME, flags=dbussy.DBUS.NAME_FLAG_DO_NOT_QUEUE)
        dbus_utils.BUS.register(
            path=PATH_AGENT, interface=cls.agent, fallback=True)
        return cls.agent

    @ravel.method(
        in_signature='',
        out_signature=''
    )
    def Cancel(self):
        raise NotImplementedError

    @ravel.method(
        in_signature='',
        out_signature=''
    )
    def Release(self):
        raise NotImplementedError

    @ravel.method(
        in_signature='os',
        out_signature='',
        arg_keys=['path', 'error'],
        result_keyword='result'
    )
    async def ReportError(self, path, error):
        self.report_error(path, error)

    def report_error(self, path, error):
        pass

    @ravel.method(
        in_signature='os',
        out_signature='',
        arg_keys=['service', 'url'],
    )
    def RequestBrowser(self, path, url):
        raise NotImplementedError

    @ravel.method(
        in_signature='oa{sv}',
        out_signature='a{sv}',
        args_keyword='request',
        result_keyword='reply',
    )
    async def RequestInput(self, request, reply):
        request = dbus_utils.convert_from_dbussy(request)
        input = self.request_input(*request)
        input = {k: (dbussy.DBUS.Signature('s'), v)
                 for (k, v) in input.items()}
        reply[0] = input

    def request_input(self, request):
        pass


class Listener(object):

    def listen(self):
        dbus_utils.BUS.listen_signal(
            interface='net.connman.Manager',
            fallback=True,
            func=self._on_property_changed,
            path='/',
            name='PropertyChanged')
        dbus_utils.BUS.listen_signal(
            interface='net.connman.Service',
            fallback=True,
            func=self._on_property_changed,
            path='/',
            name='PropertyChanged')
        dbus_utils.BUS.listen_signal(
            interface='net.connman.Manager',
            fallback=True,
            func=self._on_services_changed,
            path='/',
            name='ServicesChanged')
        dbus_utils.BUS.listen_signal(
            interface='net.connman.Technology',
            fallback=True,
            func=self._on_technology_changed,
            path='/',
            name='PropertyChanged')

    @ravel.signal(name='PropertyChanged', in_signature='sv', arg_keys=('name', 'value'), path_keyword='path')
    async def _on_property_changed(self, name, value, path):
        value = dbus_utils.convert_from_dbussy(value)
        await self.on_property_changed(name, value, path)

    @ravel.signal(name='ServicesChanged', in_signature='a(oa{sv})ao', arg_keys=('services', 'removed'))
    async def _on_services_changed(self, services, removed):
        services = dbus_utils.convert_from_dbussy(services)
        removed = dbus_utils.convert_from_dbussy(removed)
        await self.on_services_changed(services, removed)

    @ravel.signal(name='PropertyChanged', in_signature='sv', arg_keys=('name', 'value'), path_keyword='path')
    async def _on_technology_changed(self, name, value, path):
        value = dbus_utils.convert_from_dbussy(value)
        await self.on_technology_changed(name, value, path)


def agent_abort():
    raise ravel.ErrorReturn(ERROR_AGENT_CANCELLED, 'Input cancelled')

def clock_get_properties():
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_CLOCK, 'GetProperties')


def clock_set_timeservers(timeservers):
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_CLOCK, 'SetProperty', 'Timeservers', (dbussy.DBUS.Signature('as'), timeservers))


def manager_get_properties():
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_MANAGER, 'GetProperties')


def manager_get_services():
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_MANAGER, 'GetServices')


def manager_get_technologies():
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_MANAGER, 'GetTechnologies')


def manager_register_agent():
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_MANAGER, 'RegisterAgent', PATH_AGENT)


def manager_unregister_agent():
    return dbus_utils.call_method(BUS_NAME, '/', INTERFACE_MANAGER, 'UnregisterAgent', PATH_AGENT)


def service_connect(path):
    return dbus_utils.run_method(BUS_NAME, path, INTERFACE_SERVICE, 'Connect')


def service_disconnect(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_SERVICE, 'Disconnect')


def service_get_properties(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_SERVICE, 'GetProperties')


def service_remove(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_SERVICE, 'Remove')


def technology_wifi_scan():
    return dbus_utils.call_method(BUS_NAME, PATH_TECH_WIFI, INTERFACE_TECHNOLOGY, 'Scan')


def technology_wifi_set_property(name, value):
    return dbus_utils.call_method(BUS_NAME, PATH_TECH_WIFI, INTERFACE_TECHNOLOGY, 'SetProperty', name, value)


def technology_wifi_set_powered(state):
    return self.technology_wifi_set_property('Powered', (dbussy.DBUS.Signature('b'), state))


def technology_wifi_set_tethering(state):
    return self.technology_wifi_set_property('Tethering', (dbussy.DBUS.Signature('b'), state))


def technology_wifi_set_tethering_identifier(identifier):
    return self.technology_wifi_set_property('TetheringIdentifier', (dbussy.DBUS.Signature('s'), identifier))


def technology_wifi_set_tethering_passphrase(passphrase):
    return self.technology_wifi_set_property('TetheringPassphrase', (dbussy.DBUS.Signature('s'), passphrase))
