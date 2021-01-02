# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import dbus
import dbus.service
import dbus_bluez
import hostname
import log
import modules
import oe
import oeWindows
import os
import threading
import time
import xbmc
import xbmcgui
from dbussy import DBusError

LEGACY_SYSTEM_BUS = dbus.SystemBus()

class bluetooth(modules.Module):

    menu = {'6': {
        'name': 32331,
        'menuLoader': 'menu_connections',
        'listTyp': 'btlist',
        'InfoText': 704,
        }}
    ENABLED = False
    OBEX_ROOT = None
    OBEX_DAEMON = None
    BLUETOOTH_DAEMON = None
    D_OBEXD_ROOT = None

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.visible = False
        self.listItems = {}
        self.dbusBluezAdapter = None
        self.discovering = False

    @log.log_function()
    def do_init(self):
        self.visible = True

    @log.log_function()
    def start_service(self):
        self.find_adapter()

    @log.log_function()
    def stop_service(self):
        if hasattr(self, 'discovery_thread'):
            try:
                self.discovery_thread.stop()
                del self.discovery_thread
            except AttributeError:
                pass
        if hasattr(self, 'dbusBluezAdapter'):
            self.dbusBluezAdapter = None

    @log.log_function()
    def exit(self):
        if hasattr(self, 'discovery_thread'):
            try:
                self.discovery_thread.stop()
                del self.discovery_thread
            except AttributeError:
                pass
        self.clear_list()
        self.visible = False

    # ###################################################################
    # # Bluetooth Adapter
    # ###################################################################

    @log.log_function()
    def find_adapter(self):
        self.dbusBluezAdapter = dbus_bluez.find_adapter()
        if self.dbusBluezAdapter:
            self.init_adapter()

    @log.log_function()
    def init_adapter(self):
        dbus_bluez.adapter_set_alias(self.dbusBluezAdapter, hostname.get_hostname())
        dbus_bluez.adapter_set_powered(self.dbusBluezAdapter, True)

    @log.log_function()
    def start_discovery(self):
        self.discovering = True
        dbus_bluez.adapter_start_discovery(self.dbusBluezAdapter)

    @log.log_function()
    def stop_discovery(self):
        if self.discovering:
            dbus_bluez.adapter_stop_discovery(self.dbusBluezAdapter)
            self.discovering = False

    # ###################################################################
    # # Bluetooth Device
    # ###################################################################

    @log.log_function()
    def get_devices(self):
        return dbus_bluez.find_devices()

    @log.log_function()
    def init_device(self, listItem=None):
        if listItem is None:
            listItem = oe.winOeMain.getControl(oe.listObject['btlist']).getSelectedItem()
        if listItem is None:
            return
        if listItem.getProperty('Paired') != '1':
            self.pair_device(listItem.getProperty('entry'))
        else:
            self.connect_device(listItem.getProperty('entry'))

    @log.log_function()
    def trust_connect_device(self, listItem=None):
        # ########################################################
        # # This function is used to Pair PS3 Remote without auth
        # ########################################################
        if listItem is None:
            listItem = oe.winOeMain.getControl(oe.listObject['btlist']).getSelectedItem()
        if listItem is None:
            return
        self.trust_device(listItem.getProperty('entry'))
        self.connect_device(listItem.getProperty('entry'))

    @log.log_function()
    def enable_device_standby(self, listItem=None):
        devices = oe.read_setting('bluetooth', 'standby')
        if not devices == None:
            devices = devices.split(',')
        else:
            devices = []
        if not listItem.getProperty('entry') in devices:
            devices.append(listItem.getProperty('entry'))
        oe.write_setting('bluetooth', 'standby', ','.join(devices))

    @log.log_function()
    def disable_device_standby(self, listItem=None):
        devices = oe.read_setting('bluetooth', 'standby')
        if not devices == None:
            devices = devices.split(',')
        else:
            devices = []
        if listItem.getProperty('entry') in devices:
            devices.remove(listItem.getProperty('entry'))
        oe.write_setting('bluetooth', 'standby', ','.join(devices))

    @log.log_function()
    def pair_device(self, path):
        try:
            dbus_bluez.device_pair(path)
            listItem = oe.winOeMain.getControl(oe.listObject['btlist']).getSelectedItem()
            if listItem is None:
                return
            self.trust_device(listItem.getProperty('entry'))
            self.connect_device(listItem.getProperty('entry'))
            self.menu_connections()
        except DBusError as e:
            self.dbus_error_handler(e)

    @log.log_function()
    def trust_device(self, path):
        dbus_bluez.device_set_trusted(path, True)

    @log.log_function()
    def connect_device(self, path):
        try:
            dbus_bluez.device_connect(path)
            self.menu_connections()
        except DBusError as e:
            self.dbus_error_handler(e)

    @log.log_function()
    def disconnect_device(self, listItem=None):
        if listItem is None:
            listItem = self.oe.winOeMain.getControl(self.oe.listObject['btlist']).getSelectedItem()
        if listItem is None:
            return
        self.disconnect_device_by_path(listItem.getProperty('entry'))

    @log.log_function()
    def disconnect_device_by_path(self, path):
        try:
            dbus_bluez.device_disconnect(path)
            self.menu_connections()
        except DBusError as e:
            self.dbus_error_handler(e)

    @log.log_function()
    def remove_device(self, listItem=None):
        if listItem is None:
            listItem = oe.winOeMain.getControl(oe.listObject['btlist']).getSelectedItem()
        if listItem is None:
            return
        oe.dbg_log('bluetooth::remove_device->entry::', listItem.getProperty('entry'), oe.LOGDEBUG)
        path = listItem.getProperty('entry')
        dbus_bluez.adapter_remove_device(self.dbusBluezAdapter, path)
        self.disable_device_standby(listItem)
        self.menu_connections()

    # ###################################################################
    # # Bluetooth Error Handler
    # ###################################################################

    @log.log_function()
    def dbus_error_handler(self, error):
        oe.dbg_log('bluetooth::dbus_error_handler::err_message', repr(error.message), oe.LOGDEBUG)
        oe.notify('Bluetooth error', error.message.split('.')[0], 'bt')
        if hasattr(self, 'pinkey_window'):
            self.close_pinkey_window()

    # ###################################################################
    # # Bluetooth GUI
    # ###################################################################

    @log.log_function()
    def clear_list(self):
        remove = [entry for entry in self.listItems]
        for entry in remove:
            del self.listItems[entry]

    @log.log_function()
    def menu_connections(self, focusItem=None):
        if not hasattr(oe, 'winOeMain'):
            return 0
        if not oe.winOeMain.visible:
            return 0
        if not dbus_bluez.system_has_bluez():
            oe.winOeMain.getControl(1301).setLabel(oe._(32346))
            self.clear_list()
            oe.winOeMain.getControl(int(oe.listObject['btlist'])).reset()
            oe.dbg_log('bluetooth::menu_connections', 'exit_function (BT Disabled)', oe.LOGDEBUG)
            return
        if self.dbusBluezAdapter is None:
            oe.winOeMain.getControl(1301).setLabel(oe._(32338))
            self.clear_list()
            oe.winOeMain.getControl(int(oe.listObject['btlist'])).reset()
            oe.dbg_log('bluetooth::menu_connections', 'exit_function (No Adapter)', oe.LOGDEBUG)
            return
        if not dbus_bluez.adapter_get_powered(self.dbusBluezAdapter):
            oe.winOeMain.getControl(1301).setLabel(oe._(32338))
            self.clear_list()
            oe.winOeMain.getControl(int(oe.listObject['btlist'])).reset()
            oe.dbg_log('bluetooth::menu_connections', 'exit_function (No Adapter Powered)', oe.LOGDEBUG)
            return
        oe.winOeMain.getControl(1301).setLabel(oe._(32339))
        if not hasattr(self, 'discovery_thread'):
            self.start_discovery()
            self.discovery_thread = discoveryThread(oe)
            self.discovery_thread.start()
        else:
            if self.discovery_thread.stopped:
                del self.discovery_thread
                self.start_discovery()
                self.discovery_thread = discoveryThread(oe)
                self.discovery_thread.start()
        dictProperties = {}

        # type 1=int, 2=string, 3=array, 4=bool

        properties = {
            0: {
                'type': 4,
                'value': 'Paired',
                },
            1: {
                'type': 2,
                'value': 'Adapter',
                },
            2: {
                'type': 4,
                'value': 'Connected',
                },
            3: {
                'type': 2,
                'value': 'Address',
                },
            5: {
                'type': 1,
                'value': 'Class',
                },
            6: {
                'type': 4,
                'value': 'Trusted',
                },
            7: {
                'type': 2,
                'value': 'Icon',
                },
            }

        rebuildList = 0
        self.dbusDevices = self.get_devices()
        for dbusDevice in self.dbusDevices:
            rebuildList = 1
            oe.winOeMain.getControl(int(oe.listObject['btlist'])).reset()
            self.clear_list()
            break
        for dbusDevice in self.dbusDevices:
            dictProperties = {}
            apName = ''
            dictProperties['entry'] = dbusDevice
            dictProperties['modul'] = self.__class__.__name__
            dictProperties['action'] = 'open_context_menu'
            if 'Name' in self.dbusDevices[dbusDevice]:
                apName = self.dbusDevices[dbusDevice]['Name']
            if not 'Icon' in self.dbusDevices[dbusDevice]:
                dictProperties['Icon'] = 'default'
            for prop in properties:
                name = properties[prop]['value']
                if name in self.dbusDevices[dbusDevice]:
                    value = self.dbusDevices[dbusDevice][name]
                    if name == 'Connected':
                        if value:
                            dictProperties['ConnectedState'] = oe._(32334)
                        else:
                            dictProperties['ConnectedState'] = oe._(32335)
                    if properties[prop]['type'] == 1:
                        value = str(int(value))
                    if properties[prop]['type'] == 2:
                        value = str(value)
                    if properties[prop]['type'] == 3:
                        value = str(len(value))
                    if properties[prop]['type'] == 4:
                        value = str(int(value))
                    dictProperties[name] = value
            if rebuildList == 1:
                self.listItems[dbusDevice] = oe.winOeMain.addConfigItem(apName, dictProperties, oe.listObject['btlist'])
            else:
                if self.listItems[dbusDevice] != None:
                    self.listItems[dbusDevice].setLabel(apName)
                    for dictProperty in dictProperties:
                        self.listItems[dbusDevice].setProperty(dictProperty, dictProperties[dictProperty])

    @log.log_function()
    def open_context_menu(self, listItem):
        values = {}
        if listItem is None:
            listItem = oe.winOeMain.getControl(oe.listObject['btlist']).getSelectedItem()
        if listItem.getProperty('Paired') != '1':
            values[1] = {
                'text': oe._(32145),
                'action': 'init_device',
                }
            if listItem.getProperty('Trusted') != '1':
                values[2] = {
                    'text': oe._(32358),
                    'action': 'trust_connect_device',
                    }
        if listItem.getProperty('Connected') == '1':
            values[3] = {
                'text': oe._(32143),
                'action': 'disconnect_device',
                }
            devices = oe.read_setting('bluetooth', 'standby')
            if not devices == None:
                devices = devices.split(',')
            else:
                devices = []
            if listItem.getProperty('entry') in devices:
                values[4] = {
                    'text': oe._(32389),
                    'action': 'disable_device_standby',
                    }
            else:
                values[4] = {
                    'text': oe._(32388),
                    'action': 'enable_device_standby',
                    }
        elif listItem.getProperty('Paired') == '1':
            values[1] = {
                'text': oe._(32144),
                'action': 'init_device',
                }
        elif listItem.getProperty('Trusted') == '1':
            values[2] = {
                'text': oe._(32144),
                'action': 'trust_connect_device',
                }
        values[5] = {
            'text': oe._(32141),
            'action': 'remove_device',
            }
        values[6] = {
            'text': oe._(32142),
            'action': 'menu_connections',
            }
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

    @log.log_function()
    def open_pinkey_window(self, runtime=60, title=32343):
        self.pinkey_window = oeWindows.pinkeyWindow('service-LibreELEC-Settings-getPasskey.xml', oe.__cwd__, 'Default')
        self.pinkey_window.show()
        self.pinkey_window.set_title(oe._(title))
        self.pinkey_timer = pinkeyTimer(self, runtime)
        self.pinkey_timer.start()

    @log.log_function()
    def close_pinkey_window(self):
        if hasattr(self, 'pinkey_timer'):
            self.pinkey_timer.stop()
            self.pinkey_timer = None
            del self.pinkey_timer
        if hasattr(self, 'pinkey_window'):
            self.pinkey_window.close()
            self.pinkey_window = None
            del self.pinkey_window

    def standby_devices(self):
        if self.dbusBluezAdapter:
            devices = oe.read_setting('bluetooth', 'standby')
            if devices:
                for device in devices.split(','):
                    if dbus_bluez.device_get_connected(device):
                        self.disconnect_device_by_path(device)

    # ###################################################################
    # # Bluetooth monitor and agent subclass
    # ###################################################################

    class monitor:

        @log.log_function()
        def __init__(self, oeMain, parent):
            self.signal_receivers = []
            self.NameOwnerWatch = None
            self.ObexNameOwnerWatch = None
            self.btAgentPath = '/LibreELEC/bt_agent'
            self.obAgentPath = '/LibreELEC/ob_agent'
            self.parent = parent

        @log.log_function()
        def add_signal_receivers(self):
            self.signal_receivers.append(LEGACY_SYSTEM_BUS.add_signal_receiver(self.InterfacesAdded, bus_name='org.bluez',
                                         dbus_interface='org.freedesktop.DBus.ObjectManager', signal_name='InterfacesAdded'))
            self.signal_receivers.append(LEGACY_SYSTEM_BUS.add_signal_receiver(self.InterfacesRemoved, bus_name='org.bluez',
                                         dbus_interface='org.freedesktop.DBus.ObjectManager', signal_name='InterfacesRemoved'))
            self.signal_receivers.append(LEGACY_SYSTEM_BUS.add_signal_receiver(self.AdapterChanged,
                                         dbus_interface='org.freedesktop.DBus.Properties', signal_name='PropertiesChanged',
                                         arg0='org.bluez.Adapter1', path_keyword='path'))
            self.signal_receivers.append(LEGACY_SYSTEM_BUS.add_signal_receiver(self.PropertiesChanged,
                                         dbus_interface='org.freedesktop.DBus.Properties', signal_name='PropertiesChanged',
                                         arg0='org.bluez.Device1', path_keyword='path'))
            self.signal_receivers.append(LEGACY_SYSTEM_BUS.add_signal_receiver(self.TransferChanged,
                                         dbus_interface='org.freedesktop.DBus.Properties', arg0='org.bluez.obex.Transfer1'))
            self.NameOwnerWatch = LEGACY_SYSTEM_BUS.watch_name_owner('org.bluez', self.bluezNameOwnerChanged)
            self.ObexNameOwnerWatch = LEGACY_SYSTEM_BUS.watch_name_owner('org.bluez.obex', self.bluezObexNameOwnerChanged)

        @log.log_function()
        def remove_signal_receivers(self):
            for signal_receiver in self.signal_receivers:
                signal_receiver.remove()
                signal_receiver = None

            # Remove will cause xbmc freeze
            # bluez bug ?
            # does this work now ? 2014-01-19 / LUFI

            self.ObexNameOwnerWatch.cancel()
            self.ObexNameOwnerWatch = None
            self.NameOwnerWatch.cancel()
            self.NameOwnerWatch = None
            if hasattr(self, 'obAgent'):
                self.remove_obex_agent()
            if hasattr(self, 'btAgent'):
                self.remove_agent()

        @log.log_function()
        def bluezNameOwnerChanged(self, proxy):
            if proxy:
                self.initialize_agent()
            else:
                self.remove_agent()

        @log.log_function()
        def initialize_agent(self):
            self.btAgent = bluetoothAgent(LEGACY_SYSTEM_BUS, self.btAgentPath)
            self.btAgent.oe = oe
            self.btAgent.parent = self.parent
            dbusBluezManager = dbus.Interface(LEGACY_SYSTEM_BUS.get_object('org.bluez', '/org/bluez'), 'org.bluez.AgentManager1')
            dbusBluezManager.RegisterAgent(self.btAgentPath, 'KeyboardDisplay')
            dbusBluezManager.RequestDefaultAgent(self.btAgentPath)
            dbusBluezManager = None

        @log.log_function()
        def remove_agent(self):
            if hasattr(self, 'btAgent'):
                self.btAgent.remove_from_connection(LEGACY_SYSTEM_BUS, self.btAgentPath)
                try:
                    dbusBluezManager = dbus.Interface(LEGACY_SYSTEM_BUS.get_object('org.bluez', '/org/bluez'), 'org.bluez.AgentManager1')
                    dbusBluezManager.UnregisterAgent(self.btAgentPath)
                    dbusBluezManager = None
                except:
                    dbusBluezManager = None
                    pass
                del self.btAgent

        @log.log_function()
        def bluezObexNameOwnerChanged(self, proxy):
            if proxy:
                self.initialize_obex_agent()
            else:
                self.remove_obex_agent()

        @log.log_function()
        def initialize_obex_agent(self):
            self.obAgent = obexAgent(LEGACY_SYSTEM_BUS, self.obAgentPath)
            self.obAgent.oe = oe
            self.obAgent.parent = self.parent
            dbusBluezObexManager = dbus.Interface(LEGACY_SYSTEM_BUS.get_object('org.bluez.obex', '/org/bluez/obex'),
                                                  'org.bluez.obex.AgentManager1')
            dbusBluezObexManager.RegisterAgent(self.obAgentPath)
            dbusBluezObexManager = None

        @log.log_function()
        def remove_obex_agent(self):
            if hasattr(self, 'obAgent'):
                self.obAgent.remove_from_connection(LEGACY_SYSTEM_BUS, self.obAgentPath)
                try:
                    dbusBluezObexManager = dbus.Interface(LEGACY_SYSTEM_BUS.get_object('org.bluez.obex', '/org/bluez/obex'),
                                                          'org.bluez.obex.AgentManager1')
                    dbusBluezObexManager.UnregisterAgent(self.obAgentPath)
                    dbusBluezObexManager = None
                except:
                    dbusBluezObexManager = None
                    pass
                del self.obAgent

        @log.log_function()
        def InterfacesAdded(self, path, interfaces):
            if 'org.bluez.Adapter1' in interfaces:
                self.parent.dbusBluezAdapter = path
                self.parent.init_adapter()
            if hasattr(self.parent, 'pinkey_window'):
                if path == self.parent.pinkey_window.device:
                    self.parent.close_pinkey_window()
            if self.parent.visible:
                self.parent.menu_connections()

        @log.log_function()
        def InterfacesRemoved(self, path, interfaces):
            if 'org.bluez.Adapter1' in interfaces:
                self.parent.dbusBluezAdapter = None
            if self.parent.visible and not hasattr(self.parent, 'discovery_thread'):
                self.parent.menu_connections()

        @log.log_function()
        def AdapterChanged(self, interface, changed, invalidated, path):
            pass

        @log.log_function()
        def PropertiesChanged(self, interface, changed, invalidated, path):
            if self.parent.visible:
                properties = [
                    'Paired',
                    'Adapter',
                    'Connected',
                    'Address',
                    'Class',
                    'Trusted',
                    'Icon',
                    ]
                if path in self.parent.listItems:
                    for prop in changed:
                        if prop in properties:
                            self.parent.listItems[path].setProperty(str(prop), str(changed[prop]))
                else:
                    self.parent.menu_connections()

        @log.log_function()
        def TransferChanged(self, path, interface, dummy):
            if 'Status' in interface:
                if interface['Status'] == 'active':
                    self.parent.download_start = time.time()
                    self.parent.download = xbmcgui.DialogProgress()
                    self.parent.download.create('Bluetooth Filetransfer', f'{oe._(32181)}: {self.parent.download_file}')
                else:
                    if hasattr(self.parent, 'download'):
                        self.parent.download.close()
                        del self.parent.download
                        del self.parent.download_path
                        del self.parent.download_size
                        del self.parent.download_start
                    if interface['Status'] == 'complete':
                        xbmcDialog = xbmcgui.Dialog()
                        answer = xbmcDialog.yesno('Bluetooth Filetransfer', oe._(32383))
                        if answer == 1:
                            fil = f'{oe.DOWNLOAD_DIR}/{self.parent.download_file}'
                            if 'image' in self.parent.download_type:
                                xbmc.executebuiltin(f'showpicture({fil})')
                            else:
                                xbmc.Player().play(fil)
                        del self.parent.download_type
                        del self.parent.download_file
            if hasattr(self.parent, 'download'):
                if 'Transferred' in interface:
                    transferred = int(interface['Transferred'] / 1024)
                    speed = transferred / (time.time() - self.parent.download_start)
                    percent = int(round(100 / self.parent.download_size * (interface['Transferred'] / 1024), 0))
                    message = f'{oe._(32181)}: {self.parent.download_file}\n{oe._(32382)}: {speed} KB/s'
                    self.parent.download.update(percent, message)
                if self.parent.download.iscanceled():
                    obj = LEGACY_SYSTEM_BUS.get_object('org.bluez.obex', self.parent.download_path)
                    itf = dbus.Interface(obj, 'org.bluez.obex.Transfer1')
                    itf.Cancel()
                    obj = None
                    itf = None


####################################################################
## Bluetooth Agent class
####################################################################

class Rejected(dbus.DBusException):

    _dbus_error_name = 'org.bluez.Error.Rejected'


class bluetoothAgent(dbus.service.Object):

    @dbus.service.method('org.bluez.Agent1', in_signature='', out_signature='')
    def Release(self):
        try:
            oe.dbg_log('bluetooth::btAgent::Release', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::Release', 'exit_function', oe.LOGDEBUG)
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::Release', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='os', out_signature='')
    def AuthorizeService(self, device, uuid):
        try:
            oe.dbg_log('bluetooth::btAgent::AuthorizeService', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::AuthorizeService::device=', repr(device), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::AuthorizeService::uuid=', repr(uuid), oe.LOGDEBUG)
            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('Bluetooth', f'Authorize service {uuid}?')
            oe.dbg_log('bluetooth::btAgent::AuthorizeService::answer=', repr(answer), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::AuthorizeService', 'exit_function', oe.LOGDEBUG)
            if answer == 1:
                oe.dictModules['bluetooth'].trust_device(device)
                return
            raise Rejected('Connection rejected!')
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::AuthorizeService', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        try:
            oe.dbg_log('bluetooth::btAgent::RequestPinCode', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestPinCode::device=', repr(device), oe.LOGDEBUG)
            xbmcKeyboard = xbmc.Keyboard('', 'Enter PIN code')
            xbmcKeyboard.doModal()
            pincode = xbmcKeyboard.getText()
            oe.dbg_log('bluetooth::btAgent::RequestPinCode', 'return->' + pincode, oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestPinCode', 'exit_function', oe.LOGDEBUG)
            return dbus.String(pincode)
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::RequestPinCode', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='o', out_signature='u')
    def RequestPasskey(self, device):
        try:
            oe.dbg_log('bluetooth::btAgent::RequestPasskey', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestPasskey::device=', repr(device), oe.LOGDEBUG)
            xbmcDialog = xbmcgui.Dialog()
            passkey = int(xbmcDialog.numeric(0, 'Enter passkey (number in 0-999999)', '0'))
            oe.dbg_log('bluetooth::btAgent::RequestPasskey::passkey=', repr(passkey), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestPasskey', 'exit_function', oe.LOGDEBUG)
            return dbus.UInt32(passkey)
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::RequestPasskey', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='ouq', out_signature='')
    def DisplayPasskey(self, device, passkey, entered):
        try:
            oe.dbg_log('bluetooth::btAgent::DisplayPasskey', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::DisplayPasskey::device=', repr(device), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::DisplayPasskey::passkey=', repr(passkey), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::DisplayPasskey::entered=', repr(entered), oe.LOGDEBUG)
            if not hasattr(self.parent, 'pinkey_window'):
                self.parent.open_pinkey_window()
                self.parent.pinkey_window.device = device
                self.parent.pinkey_window.set_label1('Passkey: %06u' % (passkey))
            oe.dbg_log('bluetooth::btAgent::DisplayPasskey', 'exit_function', oe.LOGDEBUG)
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::DisplayPasskey', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='os', out_signature='')
    def DisplayPinCode(self, device, pincode):
        try:
            oe.dbg_log('bluetooth::btAgent::DisplayPinCode', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::DisplayPinCode::device=', repr(device), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::DisplayPinCode::pincode=', repr(pincode), oe.LOGDEBUG)
            if hasattr(self.parent, 'pinkey_window'):
                self.parent.close_pinkey_window()
            self.parent.open_pinkey_window(runtime=30)
            self.parent.pinkey_window.device = device
            self.parent.pinkey_window.set_label1(f'PIN code: {pincode}')
            oe.dbg_log('bluetooth::btAgent::DisplayPinCode', 'exit_function', oe.LOGDEBUG)
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::DisplayPinCode', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='ou', out_signature='')
    def RequestConfirmation(self, device, passkey):
        try:
            oe.dbg_log('bluetooth::btAgent::RequestConfirmation', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestConfirmation::device=', repr(device), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestConfirmation::passkey=', repr(passkey), oe.LOGDEBUG)
            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('Bluetooth', f'Confirm passkey {passkey}')
            oe.dbg_log('bluetooth::btAgent::RequestConfirmation::answer=', repr(answer), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestConfirmation', 'exit_function', oe.LOGDEBUG)
            if answer == 1:
                oe.dictModules['bluetooth'].trust_device(device)
                return
            raise Rejected("Passkey doesn't match")
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::RequestConfirmation', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='o', out_signature='')
    def RequestAuthorization(self, device):
        try:
            oe.dbg_log('bluetooth::btAgent::RequestAuthorization', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestAuthorization::device=', repr(device), oe.LOGDEBUG)
            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('Bluetooth', 'Accept pairing?')
            oe.dbg_log('bluetooth::btAgent::RequestAuthorization::answer=', repr(answer), oe.LOGDEBUG)
            oe.dbg_log('bluetooth::btAgent::RequestAuthorization', 'exit_function', oe.LOGDEBUG)
            if answer == 1:
                oe.dictModules['bluetooth'].trust_device(device)
                return
            raise Rejected('Pairing rejected')
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::RequestAuthorization', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.Agent1', in_signature='', out_signature='')
    def Cancel(self):
        try:
            oe.dbg_log('bluetooth::btAgent::Cancel', 'enter_function', oe.LOGDEBUG)
            if hasattr(self.parent, 'pinkey_window'):
                self.parent.close_pinkey_window()
            oe.dbg_log('bluetooth::btAgent::Cancel', 'exit_function', oe.LOGDEBUG)
        except Exception as e:
            oe.dbg_log('bluetooth::btAgent::Cancel', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)


####################################################################
## Obex Agent class
####################################################################

class obexAgent(dbus.service.Object):

    @dbus.service.method('org.bluez.obex.Agent1', in_signature='', out_signature='')
    def Release(self):
        try:
            oe.dbg_log('bluetooth::obexAgent::Release', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::obexAgent::Release', 'exit_function', oe.LOGDEBUG)
        except Exception as e:
            oe.dbg_log('bluetooth::obexAgent::Release', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.obex.Agent1', in_signature='o', out_signature='s')
    def AuthorizePush(self, path):
        try:
            oe.dbg_log('bluetooth::obexAgent::AuthorizePush', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::obexAgent::AuthorizePush::path=', repr(path), oe.LOGDEBUG)
            transfer = dbus.Interface(LEGACY_SYSTEM_BUS.get_object('org.bluez.obex', path), 'org.freedesktop.DBus.Properties')
            properties = transfer.GetAll('org.bluez.obex.Transfer1')
            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('Bluetooth', f"{oe._(32381)}\n\n{properties['Name']}")
            oe.dbg_log('bluetooth::obexAgent::AuthorizePush::answer=', repr(answer), oe.LOGDEBUG)
            if answer != 1:
                properties = None
                transfer = None
                raise dbus.DBusException('org.bluez.obex.Error.Rejected: Not Authorized')
            self.parent.download_path = path
            self.parent.download_file = properties['Name']
            self.parent.download_size = properties['Size'] / 1024
            if 'Type' in properties:
                self.parent.download_type = properties['Type']
            else:
                self.parent.download_type = None
            res = properties['Name']
            properties = None
            transfer = None
            oe.dbg_log('bluetooth::obexAgent::AuthorizePush', 'exit_function', oe.LOGDEBUG)
            return res
        except Exception as e:
            oe.dbg_log('bluetooth::obexAgent::AuthorizePush', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)

    @dbus.service.method('org.bluez.obex.Agent1', in_signature='', out_signature='')
    def Cancel(self):
        try:
            oe.dbg_log('bluetooth::obexAgent::Cancel', 'enter_function', oe.LOGDEBUG)
            oe.dbg_log('bluetooth::obexAgent::Cancel', 'exit_function', oe.LOGDEBUG)
        except Exception as e:
            oe.dbg_log('bluetooth::obexAgent::Cancel', 'ERROR: (' + repr(e) + ')', oe.LOGERROR)


class discoveryThread(threading.Thread):

    def __init__(self, oeMain):
        threading.Thread.__init__(self)
        self.last_run = 0
        self.stopped = False
        self.main_menu = oe.winOeMain.getControl(oe.winOeMain.guiMenList)

    @log.log_function()
    def stop(self):
        self.stopped = True
        oe.dictModules['bluetooth'].stop_discovery()

    @log.log_function()
    def run(self):
        while not self.stopped and not oe.xbmcm.abortRequested():
            current_time = time.time()
            if current_time > self.last_run + 5:
                if self.main_menu.getSelectedItem().getProperty('modul') != 'bluetooth' or not hasattr(oe.dictModules['bluetooth'], 'discovery_thread'):
                    oe.dictModules['bluetooth'].menu_connections()
                self.last_run = current_time
            if self.main_menu.getSelectedItem().getProperty('modul') != 'bluetooth':
                self.stop()
            oe.xbmcm.waitForAbort(1)


class pinkeyTimer(threading.Thread):

    @log.log_function()
    def __init__(self, parent, runtime=60):
        self.parent = parent
        self.start_time = time.time()
        self.last_run = time.time()
        self.stopped = False
        self.runtime = runtime
        threading.Thread.__init__(self)

    @log.log_function()
    def stop(self):
        self.stopped = True

    @log.log_function()
    def run(self):
        self.endtime = self.start_time + self.runtime
        while not self.stopped and not oe.xbmcm.abortRequested():
            current_time = time.time()
            percent = round(100 / self.runtime * (self.endtime - current_time), 0)
            self.parent.pinkey_window.getControl(1704).setPercent(percent)
            if current_time >= self.endtime:
                self.stopped = True
                self.parent.close_pinkey_window()
            else:
                oe.xbmcm.waitForAbort(1)
