import dbus_utils
import dbussy
import ravel

BUS_NAME = 'org.bluez.obex'
ERROR_REJECTED = 'org.bluez.Error.Rejected'
INTERFACE_AGENT = 'org.bluez.obex.Agent1'
INTERFACE_AGENT_MANAGER = 'org.bluez.obex.AgentManager1'
PATH_OBEX = '/org/bluez/obex'
PATH_AGENT = '/kodi/agent/obex'


@ravel.interface(ravel.INTERFACE.SERVER, name=INTERFACE_AGENT)
class Agent(dbus_utils.Agent):

    def __init__(self):
        super().__init__(BUS_NAME, PATH_AGENT)

    def manager_register_agent(self):
        dbus_utils.call_method(
            BUS_NAME, PATH_OBEX, INTERFACE_AGENT_MANAGER, 'RegisterAgent', PATH_AGENT)

    @ravel.method(
        in_signature='',
        out_signature=''
    )
    def Release(self):
        pass

    @ravel.method(
        in_signature='o',
        out_signature='s',
        arg_keys=['path'],
        result_keyword='reply'
    )
    def AuthorizePush(self, path):
        name = self.authorize_push(path)
        reply[0] = (dbus.Signature('s'), name)

    @ravel.method(
        in_signature='',
        out_signature=''
    )
    def Cancel(self):
        pass

    def reject(self, message):
        raise dbus.DBusError(ERROR_REJECTED, message)
