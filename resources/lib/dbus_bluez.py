import dbus_utils
import dbussy

BUS_NAME = 'org.bluez'
INTERFACE_ADAPTER = 'org.bluez.Adapter1'
INTERFACE_DEVICE = 'org.bluez.Device1'


def get_managed_objects():
    return dbus_utils.call_method(BUS_NAME, '/', dbussy.DBUSX.INTERFACE_OBJECT_MANAGER, 'GetManagedObjects')


def adapter_get_property(path, name):
    return dbus_utils.call_method(BUS_NAME, path, dbussy.DBUS.INTERFACE_PROPERTIES, 'Get', INTERFACE_ADAPTER, name)


def adapter_get_powered(path):
    return adapter_get_property(path, 'Powered')


def adapter_remove_device(path, device):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_ADAPTER, 'RemoveDevice', device)


def adapter_set_property(path, name, value):
    return dbus_utils.call_method(BUS_NAME, path, dbussy.DBUS.INTERFACE_PROPERTIES, 'Set', INTERFACE_ADAPTER, name, value)


def adapter_set_alias(path, alias):
    return adapter_set_property(path, 'Alias', (dbussy.DBUS.Signature('s'), alias))


def adapter_set_powered(path, powered):
    return adapter_set_property(path, 'Powered', (dbussy.DBUS.Signature('b'), powered))


def adapter_start_discovery(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_ADAPTER, 'StartDiscovery')


def adapter_stop_discovery(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_ADAPTER, 'StopDiscovery')


def device_get_property(path, name):
    return dbus_utils.call_method(BUS_NAME, path, dbussy.DBUS.INTERFACE_PROPERTIES, 'Get', INTERFACE_DEVICE, name)


def device_get_connected(path):
    return device_get_property(path, 'Connected')


def device_connect(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_DEVICE, 'Connect')


def device_disconnect(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_DEVICE, 'Disconnect')


def device_pair(path):
    return dbus_utils.call_method(BUS_NAME, path, INTERFACE_DEVICE, 'Pair')


def device_set_property(path, name, value):
    return dbus_utils.call_method(BUS_NAME, path, dbussy.DBUS.INTERFACE_PROPERTIES, 'Set', INTERFACE_DEVICE, name, value)


def device_set_trusted(path, trusted):
    return device_set_property(path, 'Trusted', (dbussy.DBUS.Signature('b'), trusted))


def system_has_bluez():
    return BUS_NAME in dbus_utils.list_names()


def find_adapter():
    if system_has_bluez():
        objects = get_managed_objects()
        for path, interfaces in objects.items():
            if interfaces.get(INTERFACE_ADAPTER):
                return path


def find_devices():
    devices = {}
    objects = get_managed_objects()
    for path, interfaces in objects.items():
        if interfaces.get(INTERFACE_DEVICE):
            devices[path] = interfaces[INTERFACE_DEVICE]
    return devices


if __name__ == '__main__':
    import pprint
    path = find_adapter()
    pprint.pprint(path)
    property = adapter_get_property(path, 'Alias')
    pprint.pprint(property)
