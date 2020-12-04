# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2017-present Team LibreELEC

import oe
import os
import xbmc
import dbus
import dbus.service
import xbmcgui
import threading
import oeWindows
import random
import string
import config
import dbussy
import ravel
import regdom


####################################################################
## Connection properties class
####################################################################

class connmanService(object):

    menu = {}

    @config.log_function
    def __init__(self, servicePath, oeMain):
        self.struct = {
            'AutoConnect': {
                'order': 1,
                'name': 32110,
                'type': 'Boolean',
                'menuLoader': 'menu_network_configuration',
                'settings': {'AutoConnect': {
                    'order': 1,
                    'name': 32109,
                    'value': '',
                    'type': 'bool',
                    'dbus': 'Boolean',
                    'action': 'set_value',
                    }},
                },
            'IPv4': {
                'order': 2,
                'name': 32111,
                'type': 'Dictionary',
                'settings': {
                    'Method': {
                        'order': 1,
                        'name': 32113,
                        'value': '',
                        'type': 'multivalue',
                        'dbus': 'String',
                        'values': [
                            'dhcp',
                            'manual',
                            'off',
                            ],
                        'action': 'set_value',
                        },
                    'Address': {
                        'order': 2,
                        'name': 32114,
                        'value': '',
                        'type': 'ip',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'action': 'set_value',
                        'notempty': True,
                        },
                    'Netmask': {
                        'order': 3,
                        'name': 32115,
                        'value': '',
                        'type': 'ip',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'action': 'set_value',
                        'notempty': True,
                        },
                    'Gateway': {
                        'order': 4,
                        'name': 32116,
                        'value': '',
                        'type': 'ip',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'action': 'set_value',
                        'notempty': True,
                        },
                    },
                },
            'IPv6': {
                'order': 3,
                'name': 32112,
                'type': 'Dictionary',
                'settings': {
                    'Method': {
                        'order': 1,
                        'name': 32113,
                        'value': '',
                        'type': 'multivalue',
                        'dbus': 'String',
                        'values': [
                            'auto',
                            'manual',
                            '6to4',
                            'off',
                            ],
                        'action': 'set_value',
                        },
                    'Address': {
                        'order': 2,
                        'name': 32114,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'action': 'set_value',
                        },
                    'PrefixLength': {
                        'order': 4,
                        'name': 32117,
                        'value': '',
                        'type': 'text',
                        'dbus': 'Byte',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'action': 'set_value',
                        },
                    'Gateway': {
                        'order': 3,
                        'name': 32116,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'action': 'set_value',
                        },
                    'Privacy': {
                        'order': 5,
                        'name': 32118,
                        'value': '',
                        'type': 'multivalue',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Method',
                            'value': ['manual'],
                            },
                        'values': [
                            'disabled',
                            'enabled',
                            'prefered',
                            ],
                        'action': 'set_value',
                        },
                    },
                },
            'Nameservers': {
                'order': 4,
                'name': 32119,
                'type': 'Array',
                'settings': {
                    '0': {
                        'order': 1,
                        'name': 32120,
                        'value': '',
                        'type': 'ip',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    '1': {
                        'order': 2,
                        'name': 32121,
                        'value': '',
                        'type': 'ip',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    '2': {
                        'order': 3,
                        'name': 32122,
                        'value': '',
                        'type': 'ip',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    },
                },
            'Timeservers': {
                'order': 6,
                'name': 32123,
                'type': 'Array',
                'settings': {
                    '0': {
                        'order': 1,
                        'name': 32124,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    '1': {
                        'order': 2,
                        'name': 32125,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    '2': {
                        'order': 3,
                        'name': 32126,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    },
                },
            'Domains': {
                'order': 5,
                'name': 32127,
                'type': 'Array',
                'settings': {
                    '0': {
                        'order': 1,
                        'name': 32128,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    '1': {
                        'order': 2,
                        'name': 32129,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    '2': {
                        'order': 3,
                        'name': 32130,
                        'value': '',
                        'type': 'text',
                        'dbus': 'String',
                        'action': 'set_value_checkdhcp',
                        },
                    },
                },
            }

        self.datamap = {
            0: {'AutoConnect': 'AutoConnect'},
            1: {'IPv4': 'IPv4'},
            2: {'IPv4.Configuration': 'IPv4'},
            3: {'IPv6': 'IPv6'},
            4: {'IPv6.Configuration': 'IPv6'},
            5: {'Nameservers': 'Nameservers'},
            6: {'Nameservers.Configuration': 'Nameservers'},
            7: {'Domains': 'Domains'},
            8: {'Domains.Configuration': 'Domains'},
            9: {'Timeservers': 'Timeservers'},
            10: {'Timeservers.Configuration': 'Timeservers'},
            }
        self.winOeCon = oeWindows.mainWindow('service-LibreELEC-Settings-mainWindow.xml', oe.__cwd__, 'Default', oeMain=oe, isChild=True)
        self.servicePath = servicePath
        oe.dictModules['connmanNetworkConfig'] = self
        self.service = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', servicePath), 'net.connman.Service')
        self.service_properties = self.service.GetProperties()
        for entry in sorted(self.datamap):
            for (key, value) in self.datamap[entry].items():
                if self.struct[value]['type'] == 'Boolean':
                    if key in self.service_properties:
                        self.struct[value]['settings'][value]['value'] = self.service_properties[key]
                if self.struct[value]['type'] == 'Dictionary':
                    if key in self.service_properties:
                        for setting in self.struct[value]['settings']:
                            if setting in self.service_properties[key]:
                                self.struct[value]['settings'][setting]['value'] = self.service_properties[key][setting]
                if self.struct[value]['type'] == 'Array':
                    if key in self.service_properties:
                        for setting in self.struct[value]['settings']:
                            if int(setting) < len(self.service_properties[key]):
                                self.struct[value]['settings'][setting]['value'] = self.service_properties[key][int(setting)]
        self.winOeCon.show()
        for strEntry in sorted(self.struct, key=lambda x: self.struct[x]['order']):
            dictProperties = {
                'modul': 'connmanNetworkConfig',
                'listTyp': oe.listObject['list'],
                'menuLoader': 'menu_loader',
                'category': strEntry,
                }
            self.winOeCon.addMenuItem(self.struct[strEntry]['name'], dictProperties)
        self.winOeCon.doModal()
        del self.winOeCon
        del oe.dictModules['connmanNetworkConfig']

    @config.log_function
    def cancel(self):
        self.winOeCon.close()

    @config.log_function
    def menu_loader(self, menuItem):
        self.winOeCon.showButton(1, 32140, 'connmanNetworkConfig', 'save_network')
        self.winOeCon.showButton(2, 32212, 'connmanNetworkConfig', 'cancel')
        self.winOeCon.build_menu(self.struct, fltr=[menuItem.getProperty('category')])

    @config.log_function
    def set_value_checkdhcp(self, listItem):
        if self.struct['IPv4']['settings']['Method']['value'] == 'dhcp':
            ok_window = xbmcgui.Dialog()
            answer = ok_window.ok('Not allowed', 'IPv4 method is set to DHCP.\n\nChanging this option is not allowed')
            return
        oe.dbg_log('connmanService::set_value_checkdhcp', 'enter_function', oe.LOGDEBUG)
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True

    @config.log_function
    def set_value(self, listItem):
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True

    @config.log_function
    def dbus_config(self, category):
        value = None
        postfix = ''
        if self.struct[category]['type'] == 'Dictionary':
            value = {}
            postfix = '.Configuration'
        elif self.struct[category]['type'] == 'Array':
            value = dbus.Array([], signature=dbus.Signature('s'), variant_level=1)
            postfix = '.Configuration'
        for entry in sorted(self.struct[category]['settings'], key=lambda x: self.struct[category]['settings'][x]['order']):
            setting = self.struct[category]['settings'][entry]
            if (setting['value'] != '' or (hasattr(setting, 'changed') and not hasattr(setting, 'notempty'))) \
               and (not 'parent' in setting or ('parent' in setting and self.struct[category]['settings'][setting['parent']['entry']]['value'] \
                                                in setting['parent']['value'])):
                if setting['dbus'] == 'Array':
                    value = dbus.Array(dbus.String(setting['value'], variant_level=1).split(','), signature=dbus.Signature('s'),
                                       variant_level=1)
                else:
                    if self.struct[category]['type'] == 'Boolean':
                        if setting['value'] == '1' or setting['value'] == dbus.Boolean(True, variant_level=1):
                            setting['value'] = True
                        else:
                            setting['value'] = False
                        value = getattr(dbus, setting['dbus'])(setting['value'], variant_level=1)
                    elif self.struct[category]['type'] == 'Dictionary':
                        value[entry] = getattr(dbus, setting['dbus'])(setting['value'], variant_level=1)
                    elif self.struct[category]['type'] == 'Array':
                        value.append(getattr(dbus, setting['dbus'])(setting['value'], variant_level=1))
        return (category + postfix, value)

    def save_network(self):
        try:
            oe.dbg_log('connmanService::save_network', 'enter_function', oe.LOGDEBUG)
            if self.struct['IPv4']['settings']['Method']['value'] == 'dhcp':
                for setting in self.struct['Nameservers']['settings']:
                    self.struct['Nameservers']['settings'][setting]['changed'] = True
                    self.struct['Nameservers']['settings'][setting]['value'] = ''
                for setting in self.struct['Timeservers']['settings']:
                    self.struct['Timeservers']['settings'][setting]['changed'] = True
                    self.struct['Timeservers']['settings'][setting]['value'] = ''
                for setting in self.struct['Domains']['settings']:
                    self.struct['Domains']['settings'][setting]['changed'] = True
                    self.struct['Domains']['settings'][setting]['value'] = ''
            for category in [
                'AutoConnect',
                'IPv4',
                'IPv6',
                'Nameservers',
                'Timeservers',
                'Domains',
                ]:
                (category, value) = self.dbus_config(category)
                if value != None:
                    self.service.SetProperty(dbus.String(category), value)
            oe.dbg_log('connmanService::save_network', 'exit_function', oe.LOGDEBUG)
            return 'close'
        except Exception as e:
            oe.dbg_log('connmanService::save_network', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)
            return 'close'

    def delete_network(self):
        try:
            oe.dbg_log('connmanService::delete_network', 'enter_function', oe.LOGDEBUG)
            oe.dictModules['connman'].delete_network(None)
            oe.dbg_log('connmanService::delete_network', 'exit_function', oe.LOGDEBUG)
            return 'close'
        except Exception as e:
            oe.dbg_log('connmanService::delete_network', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)
            return 'close'

    def connect_network(self):
        try:
            oe.dbg_log('connmanService::connect_network', 'enter_function', oe.LOGDEBUG)
            oe.dictModules['connman'].connect_network(None)
            oe.dbg_log('connmanService::connect_network', 'exit_function', oe.LOGDEBUG)
            return 'close'
        except Exception as e:
            oe.dbg_log('connmanService::connect_network', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)
            return 'close'

    def disconnect_network(self):
        try:
            oe.dbg_log('connmanService::disconnect_network', 'enter_function', oe.LOGDEBUG)
            oe.dictModules['connman'].disconnect_network(None)
            oe.dbg_log('connmanService::disconnect_network', 'exit_function', oe.LOGDEBUG)
            return 'close'
        except Exception as e:
            oe.dbg_log('connmanService::disconnect_network', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)
            return 'close'


####################################################################
## Connman main class
####################################################################

class connman:

    ENABLED = False
    CONNMAN_DAEMON = None
    WAIT_CONF_FILE = None
    NF_CUSTOM_PATH = "/storage/.config/iptables/"
    connect_attempt = 0
    log_error = 1
    net_disconnected = 0
    notify_error = 1
    menu = {
        '3': {
            'name': 32101,
            'menuLoader': 'menu_loader',
            'listTyp': 'list',
            'InfoText': 701,
            },
        '4': {
            'name': 32100,
            'menuLoader': 'menu_connections',
            'listTyp': 'netlist',
            'InfoText': 702,
            },
        }

    @config.log_function
    def __init__(self, oeMain):
        self.listItems = {}
        self.struct = {
            '/net/connman/technology/wifi': {
                'hidden': 'true',
                'order': 1,
                'name': 32102,
                'dbus': 'Dictionary',
                'settings': {
                    'Powered': {
                        'order': 1,
                        'name': 32105,
                        'value': '',
                        'action': 'set_technologie',
                        'type': 'bool',
                        'dbus': 'Boolean',
                        'InfoText': 726,
                        },
                    'Tethering': {
                        'order': 2,
                        'name': 32108,
                        'value': '',
                        'action': 'set_technologie',
                        'type': 'bool',
                        'dbus': 'Boolean',
                        'parent': {
                            'entry': 'Powered',
                            'value': ['1'],
                            },
                        'InfoText': 727,
                        },
                    'TetheringIdentifier': {
                        'order': 3,
                        'name': 32198,
                        'value': 'LibreELEC-AP',
                        'action': 'set_technologie',
                        'type': 'text',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Tethering',
                            'value': ['1'],
                            },
                        'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$',
                        'InfoText': 728,
                        },
                    'TetheringPassphrase': {
                        'order': 4,
                        'name': 32107,
                        'value': ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)),
                        'action': 'set_technologie',
                        'type': 'text',
                        'dbus': 'String',
                        'parent': {
                            'entry': 'Tethering',
                            'value': ['1'],
                            },
                        'validate': '^[\\x00-\\x7F]{8,64}$',
                        'InfoText': 729,
                        },
                    'regdom': {
                        'order': 5,
                        'name': 32240,
                        'value': '',
                        'action': 'custom_regdom',
                        'type': 'multivalue',
                        'values': [],
                        'parent': {
                            'entry': 'Powered',
                            'value': ['1'],
                            },
                        'InfoText': 749,
                        },
                    },
                'order': 0,
                },
            '/net/connman/technology/ethernet': {
                'hidden': 'true',
                'order': 2,
                'name': 32103,
                'dbus': 'Dictionary',
                'settings': {'Powered': {
                    'order': 1,
                    'name': 32105,
                    'value': '',
                    'action': 'set_technologie',
                    'type': 'bool',
                    'dbus': 'Boolean',
                    'InfoText': 730,
                    },},
                'order': 1,
                },
            'Timeservers': {
                'order': 4,
                'name': 32123,
                'dbus': 'Array',
                'settings': {
                    '0': {
                        'order': 1,
                        'name': 32124,
                        'value': '',
                        'action': 'set_timeservers',
                        'type': 'text',
                        'dbus': 'String',
                        'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$|^$',
                        'InfoText': 732,
                        },
                    '1': {
                        'order': 2,
                        'name': 32125,
                        'value': '',
                        'action': 'set_timeservers',
                        'type': 'text',
                        'dbus': 'String',
                        'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$|^$',
                        'InfoText': 733,
                        },
                    '2': {
                        'order': 3,
                        'name': 32126,
                        'value': '',
                        'action': 'set_timeservers',
                        'type': 'text',
                        'dbus': 'String',
                        'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$|^$',
                        'InfoText': 734,
                        },
                    },
                'order': 2,
                },
            'advanced': {
                'order': 6,
                'name': 32368,
                'settings': {
                    'wait_for_network': {
                        'order': 1,
                        'name': 32369,
                        'value': '0',
                        'action': 'set_network_wait',
                        'type': 'bool',
                        'InfoText': 736,
                        },
                    'wait_for_network_time': {
                        'order': 2,
                        'name': 32370,
                        'value': '10',
                        'action': 'set_network_wait',
                        'type': 'num',
                        'parent': {
                            'entry': 'wait_for_network',
                            'value': ['1'],
                            },
                        'InfoText': 737,
                        },
                    'netfilter': {
                        'order': 3,
                        'name': 32395,
                        'type': 'multivalue',
                        'values': [],
                        'action': 'init_netfilter',
                        'InfoText': 771,
                        },
                    },
                'order': 4,
                },
            }

        self.busy = 0
        self.visible = False

    @config.log_function
    def clear_list(self):
        remove = [entry for entry in self.listItems]
        for entry in remove:
            self.listItems[entry] = None
            del self.listItems[entry]

    @config.log_function
    def do_init(self):
        self.visible = True

    @config.log_function
    def exit(self):
        self.visible = False
        self.clear_list()
        oe.dbg_log('connman::exit', 'exit_function', oe.LOGDEBUG)

    @config.log_function
    def load_values(self):
        # Network Wait
        self.struct['advanced']['settings']['wait_for_network']['value'] = '0'
        self.struct['advanced']['settings']['wait_for_network_time']['value'] = '10'
        if os.path.exists(self.WAIT_CONF_FILE):
            wait_file = open(self.WAIT_CONF_FILE, 'r')
            for line in wait_file:
                if 'WAIT_NETWORK=' in line:
                    if line.split('=')[-1].lower().strip().replace('"', '') == 'true':
                        self.struct['advanced']['settings']['wait_for_network']['value'] = '1'
                    else:
                        self.struct['advanced']['settings']['wait_for_network']['value'] = '0'
                if 'WAIT_NETWORK_TIME=' in line:
                    self.struct['advanced']['settings']['wait_for_network_time']['value'] = line.split('=')[-1].lower().strip().replace('"',
                            '')
            wait_file.close()
        # IPTABLES
        nf_values = [oe._(32397), oe._(32398), oe._(32399)]
        nf_custom_rules = [self.NF_CUSTOM_PATH + "rules.v4" , self.NF_CUSTOM_PATH + "rules.v6"]
        for custom_rule in nf_custom_rules:
            if os.path.exists(custom_rule):
                nf_values.append(oe._(32396))
                break
        self.struct['advanced']['settings']['netfilter']['values'] = nf_values
        if oe.get_service_state('iptables') == '1':
            nf_option = oe.get_service_option('iptables', 'RULES', 'home')
            if nf_option == "custom":
                nf_option_str = oe._(32396)
            elif nf_option == "home":
                nf_option_str = oe._(32398)
            elif nf_option == "public":
                nf_option_str = oe._(32399)
        else:
            nf_option_str = oe._(32397)
        self.struct['advanced']['settings']['netfilter']['value'] = nf_option_str
        # regdom
        self.struct['/net/connman/technology/wifi']['settings']['regdom']['values'] = regdom.REGDOM_LIST
        regValue = regdom.get_regdom()
        self.struct['/net/connman/technology/wifi']['settings']['regdom']['value'] = str(regValue)

    @config.log_function
    def menu_connections(self, focusItem, services={}, removed={}, force=False):
        # type 1=int, 2=string, 3=array
        properties = {
            0: {
                'flag': 0,
                'type': 2,
                'values': ['State'],
                },
            1: {
                'flag': 0,
                'type': 1,
                'values': ['Strength'],
                },
            2: {
                'flag': 0,
                'type': 1,
                'values': ['Favorite'],
                },
            3: {
                'flag': 0,
                'type': 3,
                'values': ['Security'],
                },
            4: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4', 'Method'],
                },
            5: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4', 'Address'],
                },
            6: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4.Configuration', 'Method'],
                },
            7: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4.Configuration', 'Address'],
                },
            8: {
                'flag': 0,
                'type': 2,
                'values': ['Ethernet', 'Interface'],
                },
            }
        dbusConnmanManager = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Manager')
        dbusServices = dbusConnmanManager.GetServices()
        dbusConnmanManager = None
        rebuildList = 0
        if len(dbusServices) != len(self.listItems) or force:
            rebuildList = 1
            oe.winOeMain.getControl(int(oe.listObject['netlist'])).reset()
        else:
            for (dbusServicePath, dbusServiceValues) in dbusServices:
                if dbusServicePath not in self.listItems:
                    rebuildList = 1
                    oe.winOeMain.getControl(int(oe.listObject['netlist'])).reset()
                    break
        for (dbusServicePath, dbusServiceProperties) in dbusServices:
            dictProperties = {}
            if rebuildList == 1:
                if 'Name' in dbusServiceProperties:
                    apName = dbusServiceProperties['Name']
                else:
                    if 'Security' in dbusServiceProperties:
                        apName = oe._(32208) + ' (' + str(dbusServiceProperties['Security'][0]) + ')'
                    else:
                        apName = ''
                if apName != '':
                    dictProperties['entry'] = dbusServicePath
                    dictProperties['modul'] = self.__class__.__name__
                    if 'Type' in dbusServiceProperties:
                        dictProperties['netType'] = dbusServiceProperties['Type']
                        dictProperties['action'] = 'open_context_menu'
            for prop in properties:
                result = dbusServiceProperties
                for value in properties[prop]['values']:
                    if value in result:
                        result = result[value]
                        properties[prop]['flag'] = 1
                    else:
                        properties[prop]['flag'] = 0
                if properties[prop]['flag'] == 1:
                    if properties[prop]['type'] == 1:
                        result = str(int(result))
                    if properties[prop]['type'] == 2:
                        result = str(result)
                    if properties[prop]['type'] == 3:
                        if any(x in result for x in ['psk','ieee8021x','wep']):
                            result = str('1')
                        elif 'none' in result:
                            result = str('0')
                        else:
                            result = str('-1')
                    if rebuildList == 1:
                        dictProperties[value] = result
                    else:
                        if self.listItems[dbusServicePath] != None:
                            self.listItems[dbusServicePath].setProperty(value, result)
            if rebuildList == 1:
                self.listItems[dbusServicePath] = oe.winOeMain.addConfigItem(apName, dictProperties, oe.listObject['netlist'])

    @config.log_function
    def menu_loader(self, menuItem=None):
        if menuItem == None:
            menuItem = oe.winOeMain.getControl(oe.winOeMain.guiMenList).getSelectedItem()
        dbusConnmanManager = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Manager')
        self.technologie_properties = dbusConnmanManager.GetTechnologies()
        dbusConnmanManager = None
        self.clock = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Clock')
        self.clock_properties = self.clock.GetProperties()
        self.struct['/net/connman/technology/wifi']['hidden'] = 'true'
        self.struct['/net/connman/technology/ethernet']['hidden'] = 'true'
        for (path, technologie) in self.technologie_properties:
            if path in self.struct:
                if 'hidden' in self.struct[path]:
                    del self.struct[path]['hidden']
                for entry in self.struct[path]['settings']:
                    if entry in technologie:
                        self.struct[path]['settings'][entry]['value'] = str(technologie[entry])
        for setting in self.struct['Timeservers']['settings']:
            if 'Timeservers' in self.clock_properties:
                if int(setting) < len(self.clock_properties['Timeservers']):
                    self.struct['Timeservers']['settings'][setting]['value'] = self.clock_properties['Timeservers'][int(setting)]
            else:
                self.struct['Timeservers']['settings'][setting]['value'] = ''
        oe.winOeMain.build_menu(self.struct)

    @config.log_function
    def open_context_menu(self, listItem):
        values = {}
        if listItem is None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        if listItem is None:
            oe.dbg_log('connman::open_context_menu', 'exit_function (listItem=None)', oe.LOGDEBUG)
            return
        if listItem.getProperty('State') in ['ready', 'online']:
            values[1] = {
                'text': oe._(32143),
                'action': 'disconnect_network',
                }
        else:
            values[1] = {
                'text': oe._(32144),
                'action': 'connect_network',
                }
        if listItem.getProperty('Favorite') == '1':
            values[2] = {
                'text': oe._(32150),
                'action': 'configure_network',
                }
        if listItem.getProperty('Favorite') == '1' and listItem.getProperty('netType') == 'wifi':
            values[3] = {
                'text': oe._(32141),
                'action': 'delete_network',
                }
        if hasattr(self, 'technologie_properties'):
            for (path, technologie) in self.technologie_properties:
                if path == '/net/connman/technology/wifi':
                    values[4] = {
                        'text': oe._(32142),
                        'action': 'refresh_network',
                        }
                    break
        items = []
        actions = []
        for key in list(values.keys()):
            items.append(values[key]['text'])
            actions.append(values[key]['action'])
        select_window = xbmcgui.Dialog()
        title = oe._(32012)
        result = select_window.select(title, items)
        if result >= 0:
            getattr(self, actions[result])(listItem)

    @config.log_function
    def set_timeservers(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        oe.dbg_log('connman::set_timeservers', 'enter_function', oe.LOGDEBUG)
        self.clock = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Clock')
        timeservers = dbus.Array([], signature=dbus.Signature('s'), variant_level=1)
        for setting in sorted(self.struct['Timeservers']['settings']):
            if self.struct['Timeservers']['settings'][setting]['value'] != '':
                timeservers.append(self.struct['Timeservers']['settings'][setting]['value'])
        self.clock.SetProperty(dbus.String('Timeservers'), timeservers)

    @config.log_function
    def set_value(self, listItem=None):
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True

    @config.log_function
    def set_technologie(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        dbusConnmanManager = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Manager')
        self.technologie_properties = dbusConnmanManager.GetTechnologies()
        dbusConnmanManager = None
        techPath = '/net/connman/technology/wifi'
        for (path, technologie) in self.technologie_properties:
            if path == techPath:
                for setting in self.struct[techPath]['settings']:
                    settings = self.struct[techPath]['settings']
                    self.Technology = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', techPath), 'net.connman.Technology')
                    if settings['Powered']['value'] == '1':
                        if technologie['Powered'] != True:
                            self.Technology.SetProperty('Powered', dbus.Boolean(True, variant_level=1))
                        if settings['Tethering']['value'] == '1' and dbus.String(settings['TetheringIdentifier']['value']) != '' \
                            and dbus.String(settings['TetheringPassphrase']['value']) != '':
                            oe.xbmcm.waitForAbort(5)
                            self.Technology.SetProperty('TetheringIdentifier', dbus.String(settings['TetheringIdentifier']['value'],
                                                        variant_level=1))
                            self.Technology.SetProperty('TetheringPassphrase', dbus.String(settings['TetheringPassphrase']['value'],
                                                        variant_level=1))
                            if technologie['Tethering'] != True:
                                self.Technology.SetProperty('Tethering', dbus.Boolean(True, variant_level=1))
                        else:
                            if technologie['Tethering'] != False:
                                self.Technology.SetProperty('Tethering', dbus.Boolean(False, variant_level=1))
                    else:
                        xbmc.log('####' + repr(technologie['Powered']))
                        if technologie['Powered'] != False:
                            self.Technology.SetProperty('Powered', dbus.Boolean(False, variant_level=1))
                    break
        techPath = '/net/connman/technology/ethernet'
        for (path, technologie) in self.technologie_properties:
            if path == techPath:
                for setting in self.struct[techPath]['settings']:
                    settings = self.struct[techPath]['settings']
                    self.Technology = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', techPath), 'net.connman.Technology')
                    if settings['Powered']['value'] == '1':
                        if technologie['Powered'] != True:
                            self.Technology.SetProperty('Powered', dbus.Boolean(True, variant_level=1))
                    else:
                        if technologie['Powered'] != False:
                            self.Technology.SetProperty('Powered', dbus.Boolean(False, variant_level=1))
                    break
        self.technologie_properties = None
        self.menu_loader(None)

    @config.log_function
    def custom_regdom(self, **kwargs):
            if 'listItem' in kwargs:
                regSelect = str((kwargs['listItem']).getProperty('value'))
                regdom.set_regdom(regSelect)
                self.set_value(kwargs['listItem'])

    @config.log_function
    def configure_network(self, listItem=None):
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        self.configureService = connmanService(listItem.getProperty('entry'), oe)
        del self.configureService
        self.menu_connections(None)

    @config.log_function
    def connect_network(self, listItem=None):
        self.connect_attempt += 1
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        entry = listItem.getProperty('entry')
        try:
            config.BUS['net.connman'][entry].get_interface('net.connman.Service').Connect()
            self.menu_connections(None)
        except dbussy.DBusError as e:
            config.notification(repr(e))

    @config.log_function
    def connect_reply_handler(self):
        self.menu_connections(None)

    @config.log_function
    def dbus_error_handler(self, error):
        err_name = error.get_dbus_name()
        if 'InProgress' in err_name:
            if self.net_disconnected != 1:
                self.disconnect_network()
            else:
                self.net_disconnected = 0
            self.connect_network()
        else:
            err_message = error.get_dbus_message()
            if 'Operation aborted' in err_message or 'Input/output error' in err_message:
                if self.connect_attempt == 1:
                    self.log_error = 0
                    self.notify_error = 0
                    oe.xbmcm.waitForAbort(5)
                    self.connect_network()
                else:
                    self.log_error = 1
                    self.notify_error = 1
            elif 'Did not receive a reply' in err_message:
                self.log_error = 1
                self.notify_error = 0
            else:
                self.log_error = 1
                self.notify_error = 1
            if self.notify_error == 1:
                oe.notify('Network Error', err_message)
            else:
                self.notify_error = 1
            if self.log_error == 1:
                oe.dbg_log('connman::dbus_error_handler', 'ERROR: (' + err_message + ')', oe.LOGERROR)
            else:
                self.log_error = 1

    @config.log_function
    def disconnect_network(self, listItem=None):
        self.connect_attempt = 0
        self.net_disconnected = 1
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        entry = listItem.getProperty('entry')
        config.BUS['net.connman'][entry].get_interface('net.connman.Service').Disconnect()

    @config.log_function
    def delete_network(self, listItem=None):
        self.connect_attempt = 0
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        service_path = listItem.getProperty('entry')
        network_type = listItem.getProperty('netType')
        config.BUS['net.connman'][service_path].get_interface('net.connman.Service').Remove()
        del service_object
        oe.dbg_log('connman::delete_network', 'exit_function', oe.LOGDEBUG)

    @config.log_function
    def refresh_network(self, listItem=None):
        config.BUS['net.connman']['/net/connman/technology/wifi'].get_interface('net.connman.Technology').Scan()
        self.menu_connections(None)

    @config.log_function
    def start_service(self):
        self.load_values()
        self.init_netfilter(service=1)

    @config.log_function
    def stop_service(self):
        if hasattr(self, 'dbusConnmanManager'):
            self.dbusConnmanManager = None
            del self.dbusConnmanManager

    @config.log_function
    def set_network_wait(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        if self.struct['advanced']['settings']['wait_for_network']['value'] == '0':
            if os.path.exists(self.WAIT_CONF_FILE):
                os.remove(self.WAIT_CONF_FILE)
            return
        else:
            if not os.path.exists(os.path.dirname(self.WAIT_CONF_FILE)):
                os.makedirs(os.path.dirname(self.WAIT_CONF_FILE))
            wait_conf = open(self.WAIT_CONF_FILE, 'w')
            wait_conf.write('WAIT_NETWORK="true"\n')
            wait_conf.write(f"WAIT_NETWORK_TIME=\"{self.struct['advanced']['settings']['wait_for_network_time']['value']}\"\n")
            wait_conf.close()

    def init_netfilter(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        state = 1
        options = {}
        if self.struct['advanced']['settings']['netfilter']['value'] == oe._(32396):
            options['RULES'] = "custom"
        elif self.struct['advanced']['settings']['netfilter']['value'] == oe._(32398):
            options['RULES'] = "home"
        elif self.struct['advanced']['settings']['netfilter']['value'] == oe._(32399):
            options['RULES'] = "public"
        else:
            state = 0
        oe.set_service('iptables', options, state)

    @config.log_function
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32305))
        oe.winOeMain.set_wizard_text(oe._(32306))
        oe.winOeMain.set_wizard_button_title('')
        oe.winOeMain.set_wizard_list_title(oe._(32309))
        oe.winOeMain.getControl(1391).setLabel('show')

        oe.winOeMain.getControl(oe.winOeMain.buttons[2]['id'
                                     ]).controlUp(oe.winOeMain.getControl(oe.winOeMain.guiNetList))
        oe.winOeMain.getControl(oe.winOeMain.buttons[2]['id'
                                     ]).controlRight(oe.winOeMain.getControl(oe.winOeMain.buttons[1]['id']))
        oe.winOeMain.getControl(oe.winOeMain.buttons[1]['id'
                                     ]).controlUp(oe.winOeMain.getControl(oe.winOeMain.guiNetList))
        oe.winOeMain.getControl(oe.winOeMain.buttons[1]['id'
                                     ]).controlLeft(oe.winOeMain.getControl(oe.winOeMain.buttons[2]['id']))
        self.menu_connections(None)

    class monitor:

        @config.log_function
        def __init__(self, oeMain, parent):
            self.signal_receivers = []
            self.NameOwnerWatch = None
            self.parent = parent
            self.wifiAgentPath = '/LibreELEC/agent_wifi'

        @config.log_function
        def add_signal_receivers(self):
            config.BUS.listen_signal(
                interface='net.connman.Manager',
                fallback=True,
                func=self.propertyChanged,
                path='/',
                name='PropertyChanged')
            config.BUS.listen_signal(
                interface='net.connman.Service',
                fallback=True,
                func=self.propertyChanged,
                path='/',
                name='PropertyChanged')
            config.BUS.listen_signal(
                interface='net.connman.Manager',
                fallback=True,
                func=self.servicesChanged,
                path='/',
                name='ServicesChanged')
            config.BUS.listen_signal(
                interface='net.connman.Technology',
                fallback=True,
                func=self.technologyChanged,
                path='/',
                name='PropertyChanged')
            self.conNameOwnerWatch = oe.dbusSystemBus.watch_name_owner('net.connman', self.conNameOwnerChanged)

        @config.log_function
        def remove_signal_receivers(self):
            for signal_receiver in self.signal_receivers:
                signal_receiver.remove()
                signal_receiver = None
            self.conNameOwnerWatch.cancel()
            self.conNameOwnerWatch = None
            if hasattr(self, 'wifiAgent'):
                self.remove_agent()

        @config.log_function
        def conNameOwnerChanged(self, proxy):
            if proxy:
                self.initialize_agent()
            else:
                self.remove_agent()

        @config.log_function
        def initialize_agent(self):
            if not hasattr(self, 'wifiAgent'):
                dbusConnmanManager = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Manager')
                self.wifiAgent = connmanWifiAgent(oe.dbusSystemBus, self.wifiAgentPath)
                self.wifiAgent.oe = oe
                dbusConnmanManager.RegisterAgent(self.wifiAgentPath)

        @config.log_function
        def remove_agent(self):
            if hasattr(self, 'wifiAgent'):
                self.wifiAgent.remove_from_connection(oe.dbusSystemBus, self.wifiAgentPath)
                try:
                    dbusConnmanManager = dbus.Interface(oe.dbusSystemBus.get_object('net.connman', '/'), 'net.connman.Manager')
                    dbusConnmanManager.UnregisterAgent(self.wifiAgentPath)
                finally:
                    del self.wifiAgent

        @ravel.signal(name='PropertyChanged', in_signature = 'sv', arg_keys = ('name', 'value'), path_keyword='path')
        @config.log_function
        def propertyChanged(self, name, value, path):
            value = config.convert_dbussy(value)
            if self.parent.visible:
                self.updateGui(name, value, path)

        @ravel.signal(name='PropertyChanged', in_signature = 'sv', arg_keys = ('name', 'value'), path_keyword='path')
        @config.log_function
        def technologyChanged(self, name, value, path):
            value = config.convert_dbussy(value)
            if self.parent.visible:
                if oe.winOeMain.lastMenu == 1:
                    oe.winOeMain.lastMenu = -1
                    oe.winOeMain.onFocus(oe.winOeMain.guiMenList)
                else:
                    self.updateGui(name, value, path)

        @ravel.signal(name='PropertyChanged', in_signature = 'a(oa{sv})ao', arg_keys = ('services', 'removed'))
        @config.log_function
        def servicesChanged(self, services, removed):
            services = config.convert_dbussy(services)
            removed = config.convert_dbussy(removed)
            if self.parent.visible:
                self.parent.menu_connections(None, services, removed, force=True)

        @config.log_function
        def updateGui(self, name, value, path):
            try:
                if name == 'Strength':
                    value = str(int(value))
                    self.parent.listItems[path].setProperty(name, value)
                    self.forceRender()
                elif name == 'State':
                    value = str(value)
                    self.parent.listItems[path].setProperty(name, value)
                    self.forceRender()
                elif name == 'IPv4':
                    if 'Address' in value:
                        value = str(value['Address'])
                        self.parent.listItems[path].setProperty('Address', value)
                    if 'Method' in value:
                        value = str(value['Method'])
                        self.parent.listItems[path].setProperty('Address', value)
                    self.forceRender()
                elif name == 'Favorite':
                    value = str(int(value))
                    self.parent.listItems[path].setProperty(name, value)
                    self.forceRender()
                if hasattr(self.parent, 'is_wizard'):
                    self.parent.menu_connections(None, {}, {}, force=True)
            except KeyError:
                self.parent.menu_connections(None, {}, {}, force=True)

        @config.log_function
        def forceRender(self):
                focusId = oe.winOeMain.getFocusId()
                oe.winOeMain.setFocusId(oe.listObject['netlist'])
                oe.winOeMain.setFocusId(focusId)


class Failed(dbus.DBusException):

    _dbus_error_name = 'net.connman.Error.Failed'


class Canceled(dbus.DBusException):

    _dbus_error_name = 'net.connman.Error.Canceled'


class Retry(dbus.DBusException):

    _dbus_error_name = 'net.connman.Agent.Error.Retry'


class LaunchBrowser(dbus.DBusException):

    _dbus_error_name = 'net.connman.Agent.Error.LaunchBrowser'


class connmanWifiAgent(dbus.service.Object):

    def busy(self):
        oe.input_request = False

    @dbus.service.method('net.connman.Agent', in_signature='', out_signature='')
    def Release(self):
        oe.dbg_log('connman::connmanWifiAgent::Release', 'enter_function', oe.LOGDEBUG)
        oe.dbg_log('connman::connmanWifiAgent::Release', 'exit_function', oe.LOGDEBUG)
        return {}

    @dbus.service.method('net.connman.Agent', in_signature='oa{sv}', out_signature='a{sv}')
    def RequestInput(self, path, fields):
        try:
            oe.dbg_log('connman::connmanWifiAgent::RequestInput', 'enter_function', oe.LOGDEBUG)
            oe.input_request = True
            response = {}
            if 'Name' in fields:
                xbmcKeyboard = xbmc.Keyboard('', oe._(32146))
                xbmcKeyboard.doModal()
                if xbmcKeyboard.isConfirmed():
                    if xbmcKeyboard.getText() != '':
                        response['Name'] = xbmcKeyboard.getText()
                    else:
                        self.busy()
                        raise Canceled('canceled')
                        return response
                else:
                    self.busy()
                    raise Canceled('canceled')
                    return response
            if 'Passphrase' in fields:
                xbmcKeyboard = xbmc.Keyboard('', oe._(32147))
                xbmcKeyboard.doModal()
                if xbmcKeyboard.isConfirmed():
                    if xbmcKeyboard.getText() != '':
                        response['Passphrase'] = xbmcKeyboard.getText()
                        if 'Identity' in fields:
                            response['Identity'] = xbmcKeyboard.getText()
                        if 'wpspin' in fields:
                            response['wpspin'] = xbmcKeyboard.getText()
                    else:
                        self.busy()
                        raise Canceled('canceled')
                        return response
                else:
                    self.busy()
                    raise Canceled('canceled')
                    return response
            if 'Username' in fields:
                xbmcKeyboard = xbmc.Keyboard('', oe._(32148))
                xbmcKeyboard.doModal()
                if xbmcKeyboard.isConfirmed():
                    if xbmcKeyboard.getText() != '':
                        response['Username'] = xbmcKeyboard.getText()
                    else:
                        self.busy()
                        raise Canceled('canceled')
                        return response
                else:
                    self.busy()
                    raise Canceled('canceled')
                    return response
            if 'Password' in fields:
                xbmcKeyboard = xbmc.Keyboard('', oe._(32148), True)
                xbmcKeyboard.doModal()
                if xbmcKeyboard.isConfirmed():
                    if xbmcKeyboard.getText() != '':
                        response['Password'] = xbmcKeyboard.getText()
                    else:
                        self.busy()
                        raise Canceled('canceled')
                        return response
                else:
                    self.busy()
                    raise Canceled('canceled')
                    return response
            self.busy()
            oe.dbg_log('connman::connmanWifiAgent::RequestInput', 'exit_function', oe.LOGDEBUG)
            return response
        except Exception as e:
            oe.dbg_log('connman::connmanWifiAgent::RequestInput', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('net.connman.Agent', in_signature='os', out_signature='')
    def RequestBrowser(self, path, url):
        oe.dbg_log('connman::connmanWifiAgent::RequestBrowser', 'enter_function', oe.LOGDEBUG)
        oe.dbg_log('connman::connmanWifiAgent::RequestBrowser', 'exit_function', oe.LOGDEBUG)
        return

    @dbus.service.method('net.connman.Agent', in_signature='os', out_signature='')
    def ReportError(self, path, error):
        oe.dbg_log('connman::connmanWifiAgent::ReportError', 'enter_function', oe.LOGDEBUG)
        oe.dbg_log('connman::connmanWifiAgent::ReportError', 'exit_function (CANCELED)', oe.LOGDEBUG)
        raise Failed()
        return

    @dbus.service.method('net.connman.Agent', in_signature='', out_signature='')
    def Cancel(self):
        oe.dbg_log('connman::connmanWifiAgent::Cancel', 'enter_function', oe.LOGDEBUG)
        oe.dbg_log('connman::connmanWifiAgent::Cancel', 'exit_function', oe.LOGDEBUG)
        return
