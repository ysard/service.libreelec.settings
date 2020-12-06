# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import dbus_utils

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
        return self.call_method('/', INTERFACE_CLOCK, 'SetProperty', 'Timeservers', (self.get_signature('as'), timeservers))

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
        return self.call_method(path, INTERFACE_SERVICE, 'Connect')

    def service_disconnect(self, path):
        return self.call_method(path, INTERFACE_SERVICE, 'Disconnect')

    def service_get_properties(self, path):
        return self.call_method(path, INTERFACE_SERVICE, 'GetProperties')

    def service_remove(self, path):
        return self.call_method(path, INTERFACE_SERVICE, 'Remove')

    def technology_scan_wifi(self):
        return self.call_method(PATH_TECH_WIFI, INTERFACE_TECHNOLOGY, 'Scan')
