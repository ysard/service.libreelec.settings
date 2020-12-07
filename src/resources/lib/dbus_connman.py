# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import dbus_utils
import dbussy
import ravel

BUS_NAME = 'net.connman'
INTERFACE_AGENT = 'net.connman.Agent'
INTERFACE_CLOCK = 'net.connman.Clock'
INTERFACE_MANAGER = 'net.connman.Manager'
INTERFACE_SERVICE = 'net.connman.Service'
INTERFACE_TECHNOLOGY = 'net.connman.Technology'
PATH_TECH_ETHERNET = '/net/connman/technology/ethernet'
PATH_TECH_WIFI = '/net/connman/technology/wifi'
PATH_AGENT = '/kodi/agent'


class Dbus_Connman(dbus_utils.Dbus):

    def __init__(self):
        super().__init__(BUS_NAME)

    def clock_get_properties(self):
        return self.call_method('/', INTERFACE_CLOCK, 'GetProperties')

    def clock_set_timeservers(self, timeservers):
        return self.call_method('/', INTERFACE_CLOCK, 'SetProperty', 'Timeservers', (dbussy.DBUS.Signature('as'), timeservers))

    def manager_get_properties(self):
        return self.call_method('/', INTERFACE_MANAGER, 'GetProperties')

    def manager_get_services(self):
        return self.call_method('/', INTERFACE_MANAGER, 'GetServices')

    def manager_get_technologies(self):
        return self.call_method('/', INTERFACE_MANAGER, 'GetTechnologies')

    def manager_register_agent(self):
        return self.call_method('/', INTERFACE_MANAGER, 'RegisterAgent', PATH_AGENT)

    def manager_unregister_agent(self):
        return self.call_method('/', INTERFACE_MANAGER, 'UnregisterAgent', PATH_AGENT)

    def service_connect(self, path):
        return self.run_method(path, INTERFACE_SERVICE, 'Connect')

    def service_disconnect(self, path):
        return self.call_method(path, INTERFACE_SERVICE, 'Disconnect')

    def service_get_properties(self, path):
        return self.call_method(path, INTERFACE_SERVICE, 'GetProperties')

    def service_remove(self, path):
        return self.call_method(path, INTERFACE_SERVICE, 'Remove')

    def technology_wifi_scan(self):
        return self.call_method(PATH_TECH_WIFI, INTERFACE_TECHNOLOGY, 'Scan')

    def technology_wifi_set_property(self, name, value):
        return self.call_method(PATH_TECH_WIFI, INTERFACE_TECHNOLOGY, 'SetProperty', name, value)

    def technology_wifi_set_powered(self, state):
        return self.technology_wifi_set_property('Powered', (dbussy.DBUS.Signature('b'), state))

    def technology_wifi_set_tethering(self, state):
        return self.technology_wifi_set_property('Tethering', (dbussy.DBUS.Signature('b'), state))

    def technology_wifi_set_tethering_identifier(self, identifier):
        return self.technology_wifi_set_property('TetheringIdentifier', (dbussy.DBUS.Signature('s'), identifier))

    def technology_wifi_set_tethering_passphrase(self, passphrase):
        return self.technology_wifi_set_property('TetheringPassphrase', (dbussy.DBUS.Signature('s'), passphrase))


@ravel.interface(ravel.INTERFACE.SERVER, name=INTERFACE_AGENT)
class Connman_Agent(object):

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
